"""Módulo de ingesta: data/ -> chunks -> embeddings -> ChromaDB persistente.

Uso:
    python ingest.py           # indexa solo si la colección no existe
    python ingest.py --force   # borra la colección y reindexa todo
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from pathlib import Path

import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

import config

logger = logging.getLogger("ingesta")


class EmbeddingsDistintos(RuntimeError):
    """La colección se indexó con otro modelo de embeddings."""


@dataclass
class ResultadoIngesta:
    reindexado: bool
    cantidad_chunks: int
    archivos: list[str]


def crear_cliente(carpeta: Path = config.CARPETA_VECTORSTORE) -> chromadb.ClientAPI:
    """Cliente PERSISTENTE: los vectores quedan en disco en ./vectorstore."""

    carpeta.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(carpeta), settings=Settings(anonymized_telemetry=False)
    )


def cargar_documentos(carpeta: Path = config.CARPETA_DATOS) -> list[Document]:
    """Lee los .md y .txt de data/ (un Document por archivo)."""

    archivos = sorted(
        p for p in carpeta.iterdir() if p.is_file() and p.suffix.lower() in config.EXTENSIONES_VALIDAS
    )
    if not archivos:
        raise FileNotFoundError(f"No hay archivos .md ni .txt en {carpeta}.")
    return [
        Document(page_content=p.read_text(encoding="utf-8"), metadata={"fuente": p.name})
        for p in archivos
    ]


def crear_splitter(
    tamano: int = config.TAMANO_CHUNK, solapamiento: int = config.SOLAPAMIENTO_CHUNK
) -> RecursiveCharacterTextSplitter:
    """RecursiveCharacterTextSplitter que mide en tokens del modelo de embeddings.

    Los separadores de Markdown hacen que primero intente cortar en títulos
    (##), después en párrafos, después en renglones y recién al final en
    palabras: así un chunk rara vez queda partido a mitad de una idea.
    """

    return RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        config.obtener_tokenizer(),
        chunk_size=tamano,
        chunk_overlap=solapamiento,
        separators=RecursiveCharacterTextSplitter.get_separators_for_language(Language.MARKDOWN),
    )


def contar_tokens(texto: str) -> int:
    return len(config.obtener_tokenizer().tokenize(texto))


def fragmentar(documentos: list[Document]) -> list[Document]:
    """Corta cada documento y le pone a cada chunk un id estable: archivo#n."""

    splitter = crear_splitter()
    chunks: list[Document] = []
    for doc in documentos:
        for n, texto in enumerate(splitter.split_text(doc.page_content)):
            fuente = doc.metadata["fuente"]
            chunks.append(
                Document(
                    page_content=texto,
                    metadata={"fuente": fuente, "chunk": n, "chunk_id": f"{fuente}#{n}"},
                )
            )
    return chunks


def _coleccion_existente(cliente: chromadb.ClientAPI):
    try:
        return cliente.get_collection(config.NOMBRE_COLECCION)
    except Exception:  # chromadb lanza NotFoundError/ValueError según versión
        return None


def ingestar(
    *,
    carpeta_datos: Path = config.CARPETA_DATOS,
    carpeta_vectorstore: Path = config.CARPETA_VECTORSTORE,
    embeddings: Embeddings | None = None,
    force: bool = False,
) -> ResultadoIngesta:
    """Indexa data/ en ChromaDB. Si la colección ya existe, NO reindexa (salvo force)."""

    embeddings = embeddings or config.obtener_embeddings()
    modelo = config.nombre_de_embeddings(embeddings)
    cliente = crear_cliente(carpeta_vectorstore)

    existente = _coleccion_existente(cliente)
    if existente is not None and not force:
        guardado = (existente.metadata or {}).get("modelo_embeddings")
        if guardado != modelo:
            raise EmbeddingsDistintos(
                f"La colección se indexó con '{guardado}' y ahora se usa '{modelo}'. "
                "Corré python ingest.py --force para reindexar con el modelo actual."
            )
        cantidad = existente.count()
        if cantidad > 0:
            fuentes = sorted({m["fuente"] for m in existente.get(include=["metadatas"])["metadatas"]})
            logger.info("La colección ya existe con %d chunks: no se reindexa.", cantidad)
            return ResultadoIngesta(reindexado=False, cantidad_chunks=cantidad, archivos=fuentes)

    if existente is not None:
        logger.info("Borrando la colección anterior para reindexar.")
        cliente.delete_collection(config.NOMBRE_COLECCION)

    documentos = cargar_documentos(carpeta_datos)
    chunks = fragmentar(documentos)
    vectorstore = Chroma(
        client=cliente,
        collection_name=config.NOMBRE_COLECCION,
        embedding_function=embeddings,
        collection_metadata={
            "hnsw:space": "cosine",
            "modelo_embeddings": modelo,
            "tamano_chunk": config.TAMANO_CHUNK,
            "solapamiento_chunk": config.SOLAPAMIENTO_CHUNK,
        },
    )
    vectorstore.add_documents(chunks, ids=[c.metadata["chunk_id"] for c in chunks])
    logger.info("Indexados %d chunks de %d archivos.", len(chunks), len(documentos))
    return ResultadoIngesta(
        reindexado=True,
        cantidad_chunks=len(chunks),
        archivos=[d.metadata["fuente"] for d in documentos],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Indexa data/ en ChromaDB (./vectorstore).")
    parser.add_argument("--force", action="store_true", help="Borra la colección y reindexa.")
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
    logger.setLevel(logging.INFO)
    config.silenciar_logs_externos()

    resultado = ingestar(force=args.force)
    estado = "Indexado nuevo" if resultado.reindexado else "Sin cambios (ya estaba indexado)"
    print(f"{estado}: {resultado.cantidad_chunks} chunks de {len(resultado.archivos)} archivos.")
    if resultado.reindexado:
        for chunk in fragmentar(cargar_documentos()):
            print(f"  {chunk.metadata['chunk_id']:<45} {contar_tokens(chunk.page_content):>4} tokens")


if __name__ == "__main__":
    main()
