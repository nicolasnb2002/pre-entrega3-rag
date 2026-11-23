"""Elección del LLM: sin clave nunca se llama a una API."""

from langchain_openai import ChatOpenAI

from modelo_falso import ModeloFalso
from rag import crear_llm


def test_sin_clave_usa_modelo_falso(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    assert isinstance(crear_llm(), ModeloFalso)


def test_placeholder_no_cuenta_como_clave(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "pegá_acá_la_clave_de_gemini")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    assert isinstance(crear_llm(), ModeloFalso)


def test_con_clave_y_base_url_usa_chatopenai_compatible(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "clave-de-prueba-no-real")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
    monkeypatch.setenv("OPENAI_MODEL", "gemini-3.5-flash-lite")
    llm = crear_llm()  # no hace ninguna llamada: solo arma el cliente
    assert isinstance(llm, ChatOpenAI)
    assert llm.model_name == "gemini-3.5-flash-lite"
    assert "generativelanguage" in str(llm.openai_api_base)


def test_demo_fuerza_modelo_falso_aunque_haya_clave(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "demo")
    monkeypatch.setenv("OPENAI_API_KEY", "clave-de-prueba-no-real")
    assert isinstance(crear_llm(), ModeloFalso)
