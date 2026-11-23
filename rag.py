"""Cadena RAG asíncrona: pregunta -> ChromaDB (top 4) -> prompt -> LLM -> Pydantic.

Uso:
    python rag.py                       # corre las dos pruebas de la consigna
    python rag.py "tu pregunta"         # una consulta
    python rag.py --solo-recuperar "…"  # muestra qué fragmentos trae ChromaDB, sin LLM

Sin OPENAI_API_KEY usa el modelo falso de modelo_falso.py (MODO DEMOSTRACIÓN).
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import unicodedata

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.exceptions import OutputParserException
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable, RunnableLambda, RunnableParallel, RunnablePassthrough

import config
import entorno
from schemas import RAGResponse, Referencia, RespuestaDelModelo

logger = logging.getLogger("rag")

PREGUNTA_CON_RESPUESTA = (
    "¿Cómo se calcula un intervalo de confianza para la media cuando la desviación "
    "estándar de la población es desconocida y la muestra es chica?"
)
PREGUNTA_TRAMPA = "¿Cómo se interpreta el coeficiente de determinación R² en una regresión lineal múltiple?"

# --- Prompt: el "filtro de veracidad" ---------------------------------------
MENSAJE_SISTEMA = (
    "Sos un asistente de estudio de Matemática y Estadística 2. "
    "Respondé ÚNICAMENTE con la información del CONTEXTO que te paso. "
    "No uses lo que sepas por tu cuenta, aunque estés seguro. "
    "Si la respuesta no está en el CONTEXTO, o el CONTEXTO solo la menciona sin explicarla, "
    'respondé exactamente "{no_lo_se}" y dejá la lista de fuentes vacía. '
    "Cuando sí respondas, citá en fuentes los ids entre corchetes de los fragmentos que usaste.\n\n"
    "{instrucciones_formato}"
)
MENSAJE_USUARIO = "CONTEXTO:\n{contexto}\n\nPREGUNTA: {pregunta}"


def construir_prompt(parser: PydanticOutputParser) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [("system", MENSAJE_SISTEMA), ("human", MENSAJE_USUARIO)]
    ).partial(no_lo_se=config.NO_LO_SE, instrucciones_formato=parser.get_format_instructions())


def formatear_documentos(documentos: list[Document]) -> str:
    """Transformador de documentos: cada chunk con su id entre corchetes."""

    return "\n\n".join(f"[{d.metadata['chunk_id']}]\n{d.page_content}" for d in documentos)


# --- Piezas de la cadena -----------------------------------------------------
def abrir_vectorstore(cliente=None, embeddings=None) -> Chroma:
    """Abre la colección existente con el MISMO modelo de embeddings de la ingesta."""

    from ingest import EmbeddingsDistintos, crear_cliente

    cliente = cliente or crear_cliente()
    embeddings = embeddings or config.obtener_embeddings()
    try:
        coleccion = cliente.get_collection(config.NOMBRE_COLECCION)
    except Exception:
        raise RuntimeError("No hay base vectorial. Corré primero: python ingest.py") from None
    guardado = (coleccion.metadata or {}).get("modelo_embeddings")
    if guardado != config.nombre_de_embeddings(embeddings):
        raise EmbeddingsDistintos(
            f"La base se indexó con '{guardado}'. Reindexá con python ingest.py --force."
        )
    return Chroma(client=cliente, collection_name=config.NOMBRE_COLECCION, embedding_function=embeddings)


def crear_retriever(vectorstore: Chroma, k: int = config.TOP_K) -> BaseRetriever:
    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": config.validar_top_k(k)})


def crear_llm() -> BaseChatModel:
    """ChatOpenAI (OpenAI, Gemini o Groq según OPENAI_BASE_URL) o el modelo falso."""

    proveedor = entorno.proveedor_elegido()
    if proveedor == "demo" or not entorno.hay_clave_para("openai"):
        from modelo_falso import ModeloFalso

        logger.warning("MODO DEMOSTRACIÓN: sin OPENAI_API_KEY se usa un modelo falso guionado.")
        return ModeloFalso()

    from langchain_openai import ChatOpenAI

    opciones = {
        "model": entorno.leer_modelo("openai"),
        "api_key": entorno.leer_clave("openai"),
        "temperature": 0,
        "max_tokens": entorno.leer_max_tokens(config.MAX_TOKENS_RESPUESTA),
        "timeout": config.TIMEOUT_SEGUNDOS,
    }
    base_url = entorno.leer_base_url()
    if base_url:
        opciones["base_url"] = base_url
    return ChatOpenAI(**opciones)


def _normalizar(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sin_tildes.strip().strip(".¡!\"'").lower()


def armar_respuesta(datos: dict) -> RAGResponse:
    """Último paso: valida las fuentes contra lo que de verdad se recuperó."""

    salida: RespuestaDelModelo = datos["salida_modelo"]
    documentos: list[Document] = datos["documentos"]
    if _normalizar(salida.respuesta) == _normalizar(config.NO_LO_SE):
        return RAGResponse(pregunta=datos["pregunta"], respuesta=config.NO_LO_SE, encontrada=False)

    por_id = {d.metadata["chunk_id"]: d for d in documentos}
    inventadas = [f for f in salida.fuentes if f not in por_id]
    if inventadas:
        logger.warning("El modelo citó fuentes que no se recuperaron (se descartan): %s", inventadas)
    citados = [por_id[f] for f in dict.fromkeys(salida.fuentes) if f in por_id]
    if not citados:
        logger.warning("El modelo respondió sin citar: se usan como referencia todos los fragmentos.")
        citados = documentos
    referencias = [
        Referencia(
            chunk_id=d.metadata["chunk_id"],
            fuente=d.metadata["fuente"],
            fragmento=" ".join(d.page_content.split())[: config.LARGO_VISTA_PREVIA],
        )
        for d in citados
    ]
    return RAGResponse(
        pregunta=datos["pregunta"], respuesta=salida.respuesta.strip(), encontrada=True, referencias=referencias
    )


def construir_cadena(retriever: BaseRetriever, llm: BaseChatModel) -> Runnable:
    """Cadena LCEL completa.

    pregunta ─► {documentos: retriever, pregunta}
             ─► + salida_modelo = (contexto formateado | prompt | llm | PydanticOutputParser)
             ─► armar_respuesta ─► RAGResponse
    """

    parser = PydanticOutputParser(pydantic_object=RespuestaDelModelo)
    prompt = construir_prompt(parser)

    generar = (
        RunnableLambda(lambda x: {"contexto": formatear_documentos(x["documentos"]), "pregunta": x["pregunta"]})
        | prompt
        | llm
        | parser
    ).with_retry(
        retry_if_exception_type=(OutputParserException,),
        stop_after_attempt=config.INTENTOS_MAXIMOS,
        wait_exponential_jitter=False,
    )

    return (
        RunnableParallel(documentos=retriever, pregunta=RunnablePassthrough())
        | RunnablePassthrough.assign(salida_modelo=generar)
        | RunnableLambda(armar_respuesta)
    ).with_config(run_name="cadena_rag")


_cadena_por_defecto: Runnable | None = None


def _obtener_cadena() -> Runnable:
    global _cadena_por_defecto
    if _cadena_por_defecto is None:
        load_dotenv()
        _cadena_por_defecto = construir_cadena(crear_retriever(abrir_vectorstore()), crear_llm())
    return _cadena_por_defecto


async def get_rag_response(query: str, *, cadena: Runnable | None = None) -> RAGResponse:
    """Busca en ChromaDB, arma el prompt, llama al LLM de forma asíncrona y parsea."""

    if not query or not query.strip():
        raise ValueError("La pregunta está vacía.")
    cadena = cadena or _obtener_cadena()
    return await cadena.ainvoke(query.strip())


# --- Línea de comandos ---------------------------------------------------------
def mostrar_recuperacion(pregunta: str, vectorstore: Chroma, k: int = config.TOP_K) -> None:
    print(f"\nPregunta: {pregunta}")
    resultados = vectorstore.similarity_search_with_score(pregunta, k=config.validar_top_k(k))
    for posicion, (doc, distancia) in enumerate(resultados, 1):
        vista = " ".join(doc.page_content.split())[:160]
        print(f"  {posicion}. {doc.metadata['chunk_id']:<42} distancia coseno={distancia:.4f}")
        print(f"     «{vista}…»")


def imprimir_respuesta(r: RAGResponse) -> None:
    print(r.model_dump_json(indent=2))


async def _demo() -> None:
    llm = crear_llm()
    vectorstore = abrir_vectorstore()
    cadena = construir_cadena(crear_retriever(vectorstore), llm)
    from modelo_falso import ModeloFalso

    if isinstance(llm, ModeloFalso):
        print("=" * 72)
        print("MODO DEMOSTRACIÓN: la recuperación es REAL; la respuesta la escribe un")
        print("modelo FALSO con texto fijo (no hay API key). Ver README.")
        print("=" * 72)
    for titulo, pregunta in (("Prueba 1: pregunta con respuesta en los apuntes", PREGUNTA_CON_RESPUESTA),
                             ("Prueba 2: pregunta trampa (no está en los apuntes)", PREGUNTA_TRAMPA)):
        print(f"\n### {titulo}")
        mostrar_recuperacion(pregunta, vectorstore)
        print("Respuesta:")
        imprimir_respuesta(await get_rag_response(pregunta, cadena=cadena))


def main() -> None:
    parser = argparse.ArgumentParser(description="Consulta el RAG de apuntes de Estadística 2.")
    parser.add_argument("pregunta", nargs="?", help="Sin pregunta, corre las dos pruebas de la consigna.")
    parser.add_argument("--solo-recuperar", action="store_true", help="Muestra los fragmentos, sin LLM.")
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
    config.silenciar_logs_externos()
    load_dotenv()

    if args.solo_recuperar:
        if not args.pregunta:
            parser.error("--solo-recuperar necesita una pregunta.")
        mostrar_recuperacion(args.pregunta, abrir_vectorstore())
    elif args.pregunta:
        imprimir_respuesta(asyncio.run(get_rag_response(args.pregunta)))
    else:
        asyncio.run(_demo())


if __name__ == "__main__":
    main()
