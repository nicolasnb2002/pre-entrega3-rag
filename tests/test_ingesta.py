"""Ingesta: chunking en tokens, ids, persistencia y no reindexar."""

import pytest

import config
from ingest import EmbeddingsDistintos, cargar_documentos, contar_tokens, crear_cliente, fragmentar, ingestar


def test_data_tiene_entre_3_y_4_archivos():
    docs = cargar_documentos()
    assert 3 <= len(docs) <= 4
    assert all(d.metadata["fuente"].endswith((".md", ".txt")) for d in docs)


def test_chunks_respetan_500_tokens_y_generan_varios_por_archivo():
    chunks = fragmentar(cargar_documentos())
    assert len(chunks) >= 12
    tokens = [contar_tokens(c.page_content) for c in chunks]
    assert max(tokens) <= config.TAMANO_CHUNK
    # El prefijo "passage: " + tokens especiales entran en los 512 del modelo.
    assert max(tokens) + 10 <= config.MAX_TOKENS_MODELO_EMBEDDINGS
    for fuente in {c.metadata["fuente"] for c in chunks}:
        assert sum(c.metadata["fuente"] == fuente for c in chunks) >= 3


def _solapamiento(a: str, b: str) -> str:
    """El final más largo de a que aparece al principio de b."""

    mejor = ""
    for k in range(1, min(len(a), len(b))):
        if b.startswith(a[-k:]):
            mejor = a[-k:]
    return mejor


def test_solapamiento_hasta_50_tokens_entre_chunks_consecutivos():
    chunks = fragmentar(cargar_documentos())
    pares = [(a, b) for a, b in zip(chunks, chunks[1:]) if a.metadata["fuente"] == b.metadata["fuente"]]
    solapes = [contar_tokens(_solapamiento(a.page_content, b.page_content)) for a, b in pares]
    # El splitter repite piezas enteras (párrafos, renglones) de hasta 50 tokens.
    assert max(solapes) <= config.SOLAPAMIENTO_CHUNK
    assert sum(1 for s in solapes if s > 0) >= len(pares) // 2


def test_ids_unicos_y_estables():
    a = [c.metadata["chunk_id"] for c in fragmentar(cargar_documentos())]
    b = [c.metadata["chunk_id"] for c in fragmentar(cargar_documentos())]
    assert a == b and len(set(a)) == len(a)


def test_persistencia_no_reindexa(tmp_path, embeddings_falsos):
    primera = ingestar(carpeta_vectorstore=tmp_path, embeddings=embeddings_falsos)
    assert primera.reindexado and primera.cantidad_chunks > 0

    # Otro cliente, como si fuera otra ejecución del script: los datos siguen en disco.
    segunda = ingestar(carpeta_vectorstore=tmp_path, embeddings=embeddings_falsos)
    assert not segunda.reindexado
    assert segunda.cantidad_chunks == primera.cantidad_chunks
    assert crear_cliente(tmp_path).get_collection(config.NOMBRE_COLECCION).count() == primera.cantidad_chunks


def test_force_reindexa_sin_duplicar(tmp_path, embeddings_falsos):
    primera = ingestar(carpeta_vectorstore=tmp_path, embeddings=embeddings_falsos)
    forzada = ingestar(carpeta_vectorstore=tmp_path, embeddings=embeddings_falsos, force=True)
    assert forzada.reindexado
    assert crear_cliente(tmp_path).get_collection(config.NOMBRE_COLECCION).count() == primera.cantidad_chunks


def test_rechaza_consultar_con_otro_modelo_de_embeddings(tmp_path, embeddings_falsos):
    ingestar(carpeta_vectorstore=tmp_path, embeddings=embeddings_falsos)

    class OtroModelo(type(embeddings_falsos)):
        nombre_modelo: str = "otro-modelo"

    with pytest.raises(EmbeddingsDistintos):
        ingestar(carpeta_vectorstore=tmp_path, embeddings=OtroModelo(size=384))


def test_coleccion_guarda_modelo_y_distancia_coseno(tmp_path, embeddings_falsos):
    ingestar(carpeta_vectorstore=tmp_path, embeddings=embeddings_falsos)
    meta = crear_cliente(tmp_path).get_collection(config.NOMBRE_COLECCION).metadata
    assert meta["modelo_embeddings"] == "falso-384"
    assert meta["hnsw:space"] == "cosine"
