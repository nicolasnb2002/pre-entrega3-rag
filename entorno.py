"""Lectura de configuración desde variables de entorno (misma lógica que la pre-entrega 2).

Las claves NO viven en el código: salen solo de OPENAI_API_KEY, que
load_dotenv() carga desde el archivo .env. Con OPENAI_BASE_URL se usa un
proveedor gratuito compatible con OpenAI (Gemini o Groq) con el mismo ChatOpenAI.
Un placeholder del ejemplo tampoco cuenta como clave, así no se manda
"tu_clave_aca" a un servicio pago.
"""

import os

PROVEEDORES_VALIDOS = {"openai", "demo"}

# Modelos por defecto. NO están verificados contra una cuenta real.
MODELO_POR_DEFECTO = {
    "openai": "gpt-4o-mini",
}

VARIABLE_DE_CLAVE = {
    "openai": "OPENAI_API_KEY",
}

VARIABLE_DE_MODELO = {
    "openai": "OPENAI_MODEL",
}

_PLACEHOLDERS = {
    "tu_clave",
    "tu_clave_aca",
    "tu_clave_aqui",
    "changeme",
    "sk-...",
    "pega_tu_clave",
    "pegá_tu_clave",
    "pegá_acá_la_clave_de_gemini",
    "pegá_acá_la_clave_de_groq",
    "tu_clave_de_gemini",
    "tu_clave_de_groq",
}


def clave_util(valor: str | None) -> bool:
    """True si el texto parece una clave cargada de verdad."""

    if valor is None:
        return False
    limpio = valor.strip()
    if not limpio:
        return False
    return limpio.lower() not in _PLACEHOLDERS


def proveedor_elegido() -> str:
    """Lee LLM_PROVIDER. Por defecto openai (si no hay clave, se usa el modelo falso)."""

    proveedor = os.getenv("LLM_PROVIDER", "openai").strip().lower()
    if proveedor not in PROVEEDORES_VALIDOS:
        raise ValueError(
            f"LLM_PROVIDER='{proveedor}' no sirve. Opciones: openai o demo."
        )
    return proveedor


def hay_clave_para(proveedor: str) -> bool:
    variable = VARIABLE_DE_CLAVE.get(proveedor)
    return variable is not None and clave_util(os.getenv(variable))


def leer_clave(proveedor: str) -> str:
    """Devuelve la clave del proveedor leída del entorno. Nunca la imprime."""

    variable = VARIABLE_DE_CLAVE[proveedor]
    valor = os.getenv(variable)
    if not clave_util(valor):
        raise ValueError(f"Falta {variable} en el entorno (o es el texto de ejemplo).")
    return valor.strip()


def leer_base_url() -> str | None:
    """Lee OPENAI_BASE_URL (opcional).

    Sirve para usar un proveedor compatible con OpenAI (Gemini, Groq) con el
    mismo ChatOpenAI. Si no está o está vacía, devuelve None y se usa la URL
    oficial de OpenAI.
    """

    valor = (os.getenv("OPENAI_BASE_URL") or "").strip()
    if not valor:
        return None
    if not valor.startswith(("https://", "http://")):
        raise ValueError(
            f"OPENAI_BASE_URL='{valor}' no parece una URL (tiene que empezar con https://)."
        )
    return valor


def leer_max_tokens(por_defecto: int) -> int:
    """Lee LLM_MAX_TOKENS (opcional): tope de tokens de salida del modelo.

    Los modelos que "piensan" (Gemini 3.x, gpt-oss) gastan tokens de
    razonamiento dentro de ese tope; con un tope chico la respuesta se corta.
    """

    valor = (os.getenv("LLM_MAX_TOKENS") or "").strip()
    if not valor:
        return por_defecto
    try:
        numero = int(valor)
    except ValueError:
        raise ValueError(f"LLM_MAX_TOKENS='{valor}' tiene que ser un número entero.") from None
    if numero < 1:
        raise ValueError("LLM_MAX_TOKENS tiene que ser 1 o más.")
    return numero


def leer_modelo(proveedor: str) -> str:
    variable = VARIABLE_DE_MODELO[proveedor]
    return (os.getenv(variable) or MODELO_POR_DEFECTO[proveedor]).strip()
