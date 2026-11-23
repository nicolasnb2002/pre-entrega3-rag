import sys
from pathlib import Path

import pytest
from langchain_core.embeddings import DeterministicFakeEmbedding

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config  # noqa: E402


class EmbeddingsFalsos(DeterministicFakeEmbedding):
    """Vectores al azar pero fijos por texto: sirven para probar persistencia, no relevancia."""

    nombre_modelo: str = "falso-384"


@pytest.fixture
def embeddings_falsos():
    return EmbeddingsFalsos(size=384)


@pytest.fixture(scope="session")
def embeddings_reales():
    try:
        return config.obtener_embeddings()
    except Exception as error:  # sin internet la primera vez
        pytest.skip(f"No se pudo cargar {config.MODELO_EMBEDDINGS}: {error}")
