"""Configuración central del RAG: un solo lugar para los números y los modelos.

Regla de oro del proyecto: el modelo de embeddings se define ACÁ y en ningún
otro lado. ingest.py (indexar) y rag.py (consultar) llaman a
obtener_embeddings(), así es imposible indexar con un modelo y consultar con
otro (el error #1 que marca la consigna).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from langchain_core.embeddings import Embeddings

# --- Rutas -----------------------------------------------------------------
CARPETA_PROYECTO = Path(__file__).resolve().parent
CARPETA_DATOS = CARPETA_PROYECTO / "data"
CARPETA_VECTORSTORE = CARPETA_PROYECTO / "vectorstore"
NOMBRE_COLECCION = "apuntes_estadistica2"
EXTENSIONES_VALIDAS = (".md", ".txt")

# --- Embeddings (locales y gratis) ------------------------------------------
# multilingual-e5-small: 118M parámetros, 384 dimensiones, entiende español y
# acepta hasta 512 tokens por texto. Corre en CPU, sin API key.
MODELO_EMBEDDINGS = "intfloat/multilingual-e5-small"
# La familia E5 se entrenó con estos prefijos: "passage: " para lo que se
# guarda y "query: " para lo que se pregunta. Sin ellos busca peor.
PREFIJO_DOCUMENTO = "passage: "
PREFIJO_CONSULTA = "query: "
MAX_TOKENS_MODELO_EMBEDDINGS = 512

# --- Chunking -------------------------------------------------------------
# Medido en TOKENS del tokenizer del propio modelo de embeddings (no en
# caracteres). 500 + el prefijo y los tokens especiales < 512, así el modelo
# nunca corta (trunca) un fragmento.
TAMANO_CHUNK = 500
SOLAPAMIENTO_CHUNK = 50

# --- Recuperación ---------------------------------------------------------
TOP_K = 4  # La consigna pide entre 3 y 5.
TOP_K_MINIMO, TOP_K_MAXIMO = 3, 5

# --- Generación -----------------------------------------------------------
NO_LO_SE = "No lo sé"
MAX_TOKENS_RESPUESTA = 1024  # Se puede pisar con LLM_MAX_TOKENS en el .env.
TIMEOUT_SEGUNDOS = 60.0
INTENTOS_MAXIMOS = 2  # 1 intento + 1 reintento si el JSON vuelve roto.
LARGO_VISTA_PREVIA = 220  # Caracteres del fragmento que se muestran en las referencias.


def validar_top_k(k: int) -> int:
    if not TOP_K_MINIMO <= k <= TOP_K_MAXIMO:
        raise ValueError(f"top_k={k} fuera de rango: tiene que estar entre 3 y 5.")
    return k


class EmbeddingsE5(Embeddings):
    """Envoltorio de HuggingFaceEmbeddings que agrega los prefijos de E5.

    Es la ÚNICA clase de embeddings del proyecto: la usan la ingesta y la consulta.
    """

    def __init__(self, nombre_modelo: str = MODELO_EMBEDDINGS) -> None:
        from langchain_huggingface import HuggingFaceEmbeddings

        self.nombre_modelo = nombre_modelo
        self._modelo = HuggingFaceEmbeddings(
            model_name=nombre_modelo,
            model_kwargs={"device": "cpu"},
            # Vectores normalizados: la distancia coseno queda bien definida.
            encode_kwargs={"normalize_embeddings": True},
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._modelo.embed_documents([PREFIJO_DOCUMENTO + t for t in texts])

    def embed_query(self, text: str) -> list[float]:
        return self._modelo.embed_query(PREFIJO_CONSULTA + text)


@lru_cache(maxsize=1)
def obtener_embeddings() -> EmbeddingsE5:
    """El mismo objeto para indexar y para consultar (se carga una sola vez)."""

    return EmbeddingsE5()


@lru_cache(maxsize=1)
def obtener_tokenizer():
    """Tokenizer del modelo de embeddings: con él se miden los chunks."""

    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(MODELO_EMBEDDINGS)


def nombre_de_embeddings(embeddings: Embeddings) -> str:
    return getattr(embeddings, "nombre_modelo", type(embeddings).__name__)


def silenciar_logs_externos() -> None:
    """Baja el ruido de Hugging Face (descargas, barras de progreso) en la consola."""

    import logging
    import os

    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
    for nombre in ("httpx", "huggingface_hub", "sentence_transformers", "transformers"):
        logging.getLogger(nombre).setLevel(logging.ERROR)
    try:
        from huggingface_hub.utils import logging as hf_logging

        hf_logging.set_verbosity_error()
    except Exception:
        pass
