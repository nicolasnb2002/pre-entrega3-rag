"""Modelos Pydantic del RAG.

Hay dos modelos a propósito:

- RespuestaDelModelo: lo que le pedimos al LLM (texto + ids de los fragmentos
  que usó). Lo valida el PydanticOutputParser al final de la cadena LCEL.
- RAGResponse: lo que devuelve get_rag_response. Las referencias se arman con
  los fragmentos que REALMENTE se recuperaron de ChromaDB, así el modelo no
  puede inventar una fuente.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from config import NO_LO_SE


class RespuestaDelModelo(BaseModel):
    """Salida que el LLM tiene que escribir en JSON."""

    respuesta: str = Field(
        description=(
            "Respuesta en español basada SOLO en el contexto. "
            f'Si el contexto no alcanza, exactamente "{NO_LO_SE}".'
        ),
        min_length=1,
    )
    fuentes: list[str] = Field(
        default_factory=list,
        description=(
            "Ids de los fragmentos del contexto usados para responder, tal como "
            "aparecen entre corchetes (por ejemplo 01_estimacion_intervalos_confianza.md#2). "
            f'Lista vacía si la respuesta es "{NO_LO_SE}".'
        ),
    )


class Referencia(BaseModel):
    """Un fragmento recuperado de ChromaDB que respalda la respuesta."""

    model_config = ConfigDict(extra="forbid")

    chunk_id: str = Field(description="Archivo + número de fragmento, ej. 02_x.md#3")
    fuente: str = Field(description="Nombre del archivo de data/")
    fragmento: str = Field(description="Comienzo del texto del fragmento")


class RAGResponse(BaseModel):
    """Lo que devuelve get_rag_response: texto + referencias."""

    model_config = ConfigDict(extra="forbid")

    pregunta: str
    respuesta: str
    encontrada: bool = Field(description=f'False si la respuesta es "{NO_LO_SE}"')
    referencias: list[Referencia] = Field(default_factory=list)

    @model_validator(mode="after")
    def coherencia(self) -> "RAGResponse":
        if not self.encontrada and self.referencias:
            raise ValueError(f'Una respuesta "{NO_LO_SE}" no puede traer referencias.')
        if self.encontrada and self.respuesta == NO_LO_SE:
            raise ValueError(f'"{NO_LO_SE}" tiene que marcarse como encontrada=False.')
        return self
