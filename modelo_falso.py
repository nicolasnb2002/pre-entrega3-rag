"""Modelo de lenguaje FALSO para probar la cadena sin API key.

No piensa ni lee de verdad: tiene respuestas ESCRITAS A MANO para las dos
preguntas de la demo. Lo único que hace con el prompt es buscar, entre los
fragmentos del CONTEXTO, cuáles contienen ciertas palabras, para citar sus
ids. Para cualquier otra pregunta contesta "No lo sé".

Sirve para comprobar que la cadena LCEL, el parser de Pydantic y el armado de
referencias funcionan. NO prueba que un LLM real no alucine: eso solo se ve
con Gemini o Groq (ver README).
"""

from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from config import NO_LO_SE

# (palabra clave de la pregunta, palabra que debe tener el fragmento citado, respuesta fija)
RESPUESTAS_GUIONADAS: list[tuple[str, str, str]] = [
    (
        "desviación estándar de la población es desconocida",
        "t de Student",
        "Se usa la distribución t de Student con n − 1 grados de libertad: "
        "x̄ ± t · (s / √n), suponiendo que la población es aproximadamente normal.",
    ),
]

_BLOQUE = re.compile(r"\[(?P<id>[^\]]+#\d+)\]\n(?P<texto>.*?)(?=\n\[[^\]]+#\d+\]\n|\Z)", re.S)


class ModeloFalso(BaseChatModel):
    """Chat model guionado. Devuelve el JSON que espera el PydanticOutputParser."""

    llamadas: int = 0

    @property
    def _llm_type(self) -> str:
        return "modelo-falso-guionado"

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None, **kwargs: Any) -> ChatResult:
        self.llamadas += 1
        prompt = "\n".join(str(m.content) for m in messages)
        pregunta = prompt.rsplit("PREGUNTA:", 1)[-1]
        salida = {"respuesta": NO_LO_SE, "fuentes": []}
        for clave, palabra, texto in RESPUESTAS_GUIONADAS:
            if clave.lower() in pregunta.lower():
                citados = [m["id"] for m in _BLOQUE.finditer(prompt) if palabra in m["texto"]]
                if citados:  # si el contexto no trae nada útil, igual dice "No lo sé"
                    salida = {"respuesta": texto, "fuentes": citados[:2]}
                break
        mensaje = AIMessage(content=json.dumps(salida, ensure_ascii=False))
        return ChatResult(generations=[ChatGeneration(message=mensaje)])
