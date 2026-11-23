"""Cadena RAG con LLM falso: pregunta normal, trampa, parser y referencias."""

import json

import pytest
from langchain_core.documents import Document
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.retrievers import BaseRetriever

import config
from ingest import crear_cliente, ingestar
from modelo_falso import ModeloFalso
from rag import (
    PREGUNTA_CON_RESPUESTA,
    PREGUNTA_TRAMPA,
    abrir_vectorstore,
    construir_cadena,
    crear_retriever,
    get_rag_response,
)
from schemas import RAGResponse


class RetrieverFijo(BaseRetriever):
    documentos: list[Document]

    def _get_relevant_documents(self, query, *, run_manager=None):
        return self.documentos


DOCS = [
    Document(page_content="Con muestra chica y σ desconocida se usa la t de Student con n − 1 grados de libertad.",
             metadata={"fuente": "01_x.md", "chunk": 2, "chunk_id": "01_x.md#2"}),
    Document(page_content="El ANOVA compara tres o más medias con el cociente F.",
             metadata={"fuente": "04_x.md", "chunk": 3, "chunk_id": "04_x.md#3"}),
]


def respuesta_json(respuesta, fuentes):
    return json.dumps({"respuesta": respuesta, "fuentes": fuentes}, ensure_ascii=False)


async def test_pregunta_normal_devuelve_texto_y_referencias():
    llm = FakeListChatModel(responses=[respuesta_json("Se usa la t de Student.", ["01_x.md#2"])])
    r = await get_rag_response("¿Qué uso con muestra chica?", cadena=construir_cadena(RetrieverFijo(documentos=DOCS), llm))
    assert isinstance(r, RAGResponse)
    assert r.encontrada and r.respuesta == "Se usa la t de Student."
    assert [ref.chunk_id for ref in r.referencias] == ["01_x.md#2"]
    assert r.referencias[0].fuente == "01_x.md"


async def test_pregunta_trampa_devuelve_no_lo_se_sin_referencias():
    llm = FakeListChatModel(responses=[respuesta_json("No lo sé.", [])])
    r = await get_rag_response(PREGUNTA_TRAMPA, cadena=construir_cadena(RetrieverFijo(documentos=DOCS), llm))
    assert r.respuesta == config.NO_LO_SE  # normalizado, sin el punto
    assert not r.encontrada and r.referencias == []


async def test_fuentes_inventadas_se_descartan():
    llm = FakeListChatModel(responses=[respuesta_json("Se usa F.", ["04_x.md#3", "99_inventado.md#7"])])
    r = await get_rag_response("¿ANOVA?", cadena=construir_cadena(RetrieverFijo(documentos=DOCS), llm))
    assert [ref.chunk_id for ref in r.referencias] == ["04_x.md#3"]


async def test_json_roto_se_reintenta_una_vez():
    llm = FakeListChatModel(responses=["esto no es JSON", respuesta_json("Se usa F.", ["04_x.md#3"])])
    r = await get_rag_response("¿ANOVA?", cadena=construir_cadena(RetrieverFijo(documentos=DOCS), llm))
    assert r.respuesta == "Se usa F."


async def test_json_dentro_de_bloque_markdown_se_parsea():
    llm = FakeListChatModel(responses=["```json\n" + respuesta_json("Se usa F.", ["04_x.md#3"]) + "\n```"])
    r = await get_rag_response("¿ANOVA?", cadena=construir_cadena(RetrieverFijo(documentos=DOCS), llm))
    assert r.encontrada


async def test_pregunta_vacia_falla_antes_de_llamar():
    with pytest.raises(ValueError):
        await get_rag_response("   ", cadena=construir_cadena(RetrieverFijo(documentos=DOCS), ModeloFalso()))


async def test_el_prompt_incluye_contexto_con_ids_y_filtro_de_veracidad():
    vistos = []

    class Espia(FakeListChatModel):
        def _call(self, messages, stop=None, run_manager=None, **kwargs):
            vistos.append("\n".join(str(m.content) for m in messages))
            return super()._call(messages, stop, run_manager, **kwargs)

    llm = Espia(responses=[respuesta_json("No lo sé", [])])
    await get_rag_response("¿Algo?", cadena=construir_cadena(RetrieverFijo(documentos=DOCS), llm))
    prompt = vistos[0]
    assert "[01_x.md#2]" in prompt and "[04_x.md#3]" in prompt
    assert '"No lo sé"' in prompt and "ÚNICAMENTE" in prompt
    assert "PREGUNTA: ¿Algo?" in prompt


def test_top_k_fuera_de_rango_falla():
    for k in (2, 6, 50):
        with pytest.raises(ValueError):
            config.validar_top_k(k)
    assert config.TOP_K == 4


# --- Con ChromaDB y embeddings locales reales --------------------------------
@pytest.fixture(scope="module")
def vectorstore_real(tmp_path_factory, embeddings_reales):
    carpeta = tmp_path_factory.mktemp("vectorstore")
    ingestar(carpeta_vectorstore=carpeta, embeddings=embeddings_reales)
    return abrir_vectorstore(cliente=crear_cliente(carpeta), embeddings=embeddings_reales)


@pytest.mark.modelo_real
def test_retriever_real_trae_exactamente_top_k(vectorstore_real):
    docs = crear_retriever(vectorstore_real).invoke(PREGUNTA_CON_RESPUESTA)
    assert len(docs) == config.TOP_K == 4


@pytest.mark.modelo_real
def test_retriever_real_encuentra_el_fragmento_de_t_de_student(vectorstore_real):
    docs = crear_retriever(vectorstore_real).invoke(PREGUNTA_CON_RESPUESTA)
    assert any("x̄ ± t · (s / √n)" in d.page_content for d in docs)
    assert docs[0].metadata["fuente"].startswith("01_")


@pytest.mark.modelo_real
def test_trampa_queda_mas_lejos_que_la_pregunta_buena(vectorstore_real):
    buena = vectorstore_real.similarity_search_with_score(PREGUNTA_CON_RESPUESTA, k=1)[0][1]
    trampa = vectorstore_real.similarity_search_with_score(PREGUNTA_TRAMPA, k=1)[0][1]
    assert trampa > buena
    textos = " ".join(d.page_content for d in vectorstore_real.similarity_search(PREGUNTA_TRAMPA, k=4))
    assert "R²" not in textos and "regresión" not in textos.lower()


@pytest.mark.modelo_real
async def test_cadena_completa_real_con_modelo_falso(vectorstore_real):
    cadena = construir_cadena(crear_retriever(vectorstore_real), ModeloFalso())
    buena = await get_rag_response(PREGUNTA_CON_RESPUESTA, cadena=cadena)
    trampa = await get_rag_response(PREGUNTA_TRAMPA, cadena=cadena)
    assert buena.encontrada and buena.referencias
    assert all(ref.fuente.startswith("01_") for ref in buena.referencias)
    assert trampa.respuesta == "No lo sé" and trampa.referencias == []
