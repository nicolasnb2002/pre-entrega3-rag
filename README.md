# Pre-entrega 3 — RAG local sobre apuntes de Estadística 2

Trabajo de **Nazareno Bergamo** para la pre-entrega 3 de Coderhouse (AI Engineering).

Es un sistema de **recuperación semántica local (RAG)** de punta a punta, en Python 3.12 con LangChain y ChromaDB. Le hacés una pregunta, busca los fragmentos más parecidos en una base vectorial guardada en disco y un modelo de lenguaje redacta la respuesta **usando solo esos fragmentos**. Si la respuesta no está en los apuntes, contesta exactamente **"No lo sé"**.

El "cerebro" son 4 apuntes propios de **Matemática y Estadística 2** (orden de temas de Levin y Rubin), en `data/`:

| Archivo | Tema |
| --- | --- |
| `01_estimacion_intervalos_confianza.md` | Estimación puntual y por intervalo, z y t de Student, proporciones, tamaño de muestra |
| `02_pruebas_hipotesis_una_muestra.md` | H0 y H1, errores tipo I y II, una y dos colas, valor p, pruebas z y t, proporciones |
| `03_pruebas_dos_muestras.md` | Diferencia de medias (grandes, chicas con varianza combinada, pareadas) y de proporciones |
| `04_chi_cuadrada_y_anova.md` | Chi-cuadrada de independencia y bondad de ajuste, ANOVA con F, prueba para una varianza |

Los textos y los ejemplos numéricos son inventados para estudiar (no copian el libro). Las cuentas están verificadas a mano.

## Qué pide la consigna y dónde está

| Pedido | Dónde |
| --- | --- |
| Entorno virtual con langchain, chromadb, provider y pydantic | `requirements.txt` y "Instalación" |
| Script de carga que lee `/data` | `ingest.py`: `cargar_documentos()` |
| Chunking estratégico de 500 tokens con 50 de overlap, con `RecursiveCharacterTextSplitter` | `ingest.py`: `crear_splitter()`, números en `config.py` |
| Persistir en ChromaDB local (`./vectorstore`) | `ingest.py`: `crear_cliente()` usa `chromadb.PersistentClient` |
| Verificar si la base ya existe antes de reindexar | `ingest.py`: `ingestar()`. Para forzar: `python ingest.py --force` |
| Mismo modelo de embeddings para indexar y consultar | `config.py`: `MODELO_EMBEDDINGS` y `obtener_embeddings()`, usados por los dos scripts. Además la colección guarda el nombre del modelo y se niega a consultar con otro |
| `top_k` entre 3 y 5 | `TOP_K = 4` en `config.py`, validado por `validar_top_k()` |
| Retriever: pregunta → embedding → fragmentos más relevantes | `rag.py`: `crear_retriever()` |
| Prompt de sistema como "filtro de veracidad" que dice "No lo sé" | `rag.py`: `MENSAJE_SISTEMA` |
| Cadena LCEL: retriever + transformador de documentos + modelo + `PydanticOutputParser` | `rag.py`: `construir_cadena()` y `formatear_documentos()` |
| Función async `get_rag_response(query: str)` que busca, arma el prompt, llama al LLM con `await` y parsea a Pydantic con texto y referencias | `rag.py`: `get_rag_response()` devuelve `RAGResponse` (`schemas.py`) |
| Dos pruebas: pregunta con respuesta y pregunta trampa | `python rag.py` (sin argumentos) y los tests de `tests/test_cadena.py` |
| Dataset de ejemplo .txt/.md | `data/` |
| Sin llaves de API en el código (`.env`) | `.env.example`, `.gitignore`, `entorno.py` |
| README con cómo ejecutarlo | Este archivo |

## Estructura

```text
pre-entrega3-rag/
├── data/                  # los 4 apuntes (.md) que alimentan la base
├── config.py              # números y modelo de embeddings (UN solo lugar)
├── ingest.py              # ingesta: leer, cortar, embeber, guardar en ChromaDB
├── rag.py                 # cadena LCEL + get_rag_response + demo de las 2 pruebas
├── schemas.py             # modelos Pydantic: RespuestaDelModelo, Referencia, RAGResponse
├── entorno.py             # lee el .env (misma lógica que la pre-entrega 2)
├── modelo_falso.py        # LLM falso para probar sin clave
├── tests/                 # pytest: ingesta, persistencia, top_k, cadena, entorno
├── .env.example           # plantilla del .env (sin claves)
├── requirements.txt
└── vectorstore/           # la crea ingest.py; NO se sube (está en .gitignore)
```

## Instalación

Hace falta **Python 3.12**. En una terminal, parado en esta carpeta:

```bash
python3.12 -m venv .venv
```

Activar el entorno:

- Linux o macOS: `source .venv/bin/activate`
- Windows: `.venv\Scripts\activate`

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

En Windows y macOS eso instala PyTorch para CPU, que es lo que se necesita. En Linux, `pip` baja por defecto la versión con soporte de GPU (varios GB). Para bajar solo la de CPU, antes del paso anterior:

```bash
pip install torch==2.15.0 --index-url https://download.pytorch.org/whl/cpu
```

La **primera vez** que corras `ingest.py` se descarga el modelo de embeddings `intfloat/multilingual-e5-small` (unos 470 MB) desde Hugging Face. Después queda en el caché de tu compu y ya no hace falta internet para los embeddings.

## Modelo de lenguaje y clave

El sistema tiene dos modelos distintos, y conviene no confundirlos:

| | Para qué | ¿Cuesta? | ¿Necesita clave? |
| --- | --- | --- | --- |
| **Modelo de embeddings** (`intfloat/multilingual-e5-small`) | Convertir los apuntes y la pregunta en vectores para buscar | Gratis, corre en tu compu | No |
| **Modelo de lenguaje** (LLM) | Redactar la respuesta a partir de los fragmentos | Hay opciones gratis | Sí |

La búsqueda funciona sin ninguna clave. **Para que la respuesta la escriba un modelo de verdad, hace falta una clave de un LLM.** Sin clave, `rag.py` usa un modelo falso (ver "Modo demostración").

El código usa `ChatOpenAI`. Gemini y Groq aceptan pedidos con el mismo formato que OpenAI, así que alcanza con cambiar la URL (`OPENAI_BASE_URL`) y el modelo (`OPENAI_MODEL`); la clave va siempre en `OPENAI_API_KEY`.

### Recomendado: Gemini, gratis

1. Entrá a https://aistudio.google.com/apikey con tu cuenta de Google y creá una clave.
2. Copiá la plantilla del `.env`:

   ```bash
   # Linux o macOS
   cp .env.example .env
   # Windows
   copy .env.example .env
   ```

3. Abrí `.env` con un editor y dejá estas líneas (pegando tu clave donde dice):

   ```bash
   LLM_PROVIDER=openai
   OPENAI_API_KEY=pegá_acá_la_clave_de_gemini
   OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
   OPENAI_MODEL=gemini-3.5-flash-lite
   LLM_MAX_TOKENS=2048
   ```

4. Corré `python rag.py`.

### Alternativa: Groq, gratis

1. Creá la clave en https://console.groq.com/keys.
2. En el `.env`:

   ```bash
   LLM_PROVIDER=openai
   OPENAI_API_KEY=pegá_acá_la_clave_de_groq
   OPENAI_BASE_URL=https://api.groq.com/openai/v1
   OPENAI_MODEL=openai/gpt-oss-20b
   LLM_MAX_TOKENS=2048
   ```

### Lo que verifiqué y lo que no

Verificado en la documentación oficial el **23 de noviembre de 2026**:

- Gemini: la URL `https://generativelanguage.googleapis.com/v1beta/openai/` es la del modo compatible con OpenAI ([doc](https://ai.google.dev/gemini-api/docs/openai); Google lo sigue marcando como beta). `gemini-3.5-flash-lite` figura en la [página de precios](https://ai.google.dev/gemini-api/docs/pricing) con nivel gratuito ("Free of charge" en entrada y salida).
- Groq: la URL `https://api.groq.com/openai/v1` sale de su [doc de compatibilidad](https://console.groq.com/docs/openai). `openai/gpt-oss-20b` es modelo de producción ([modelos](https://console.groq.com/docs/models)) y el plan gratis lo incluye con 30 pedidos por minuto, 1.000 por día y 8.000 tokens por minuto ([límites](https://console.groq.com/docs/rate-limits)). Cada consulta de este RAG manda unos 2.500 tokens (4 fragmentos + instrucciones), así que entran unas 3 por minuto.

**No lo probé con una clave real** (no había clave disponible). Los niveles gratuitos tienen límites y pueden cambiar. Si un proveedor rechaza algún parámetro, la API responde un error 400 que se ve en la consola.

¿Por qué `LLM_MAX_TOKENS=2048`? Los dos modelos "razonan" antes de contestar y ese razonamiento gasta tokens del mismo tope. Con un tope chico, la respuesta puede cortarse y el JSON quedar incompleto.

## Cómo ejecutarlo

Con el entorno activado:

```bash
python ingest.py               # 1) indexa data/ en ./vectorstore (solo la primera vez)
python rag.py                  # 2) corre las dos pruebas de la consigna
python rag.py "¿Qué es el error tipo II?"            # una pregunta cualquiera
python rag.py --solo-recuperar "¿Qué supuestos tiene el ANOVA?"   # ver qué fragmentos trae, sin LLM
python -m pytest               # tests (no necesitan clave)
```

Si cambiás los apuntes de `data/` o el modelo de embeddings, reindexá con `python ingest.py --force`.

## Salida real de las dos pruebas

### Ingesta (real)

Primera corrida de `python ingest.py`:

```text
INFO ingesta: Indexados 20 chunks de 4 archivos.
Indexado nuevo: 20 chunks de 4 archivos.
  01_estimacion_intervalos_confianza.md#0        462 tokens
  01_estimacion_intervalos_confianza.md#1        449 tokens
  01_estimacion_intervalos_confianza.md#2        432 tokens
  01_estimacion_intervalos_confianza.md#3        497 tokens
  01_estimacion_intervalos_confianza.md#4        433 tokens
  02_pruebas_hipotesis_una_muestra.md#0          499 tokens
  02_pruebas_hipotesis_una_muestra.md#1          467 tokens
  02_pruebas_hipotesis_una_muestra.md#2          481 tokens
  02_pruebas_hipotesis_una_muestra.md#3          376 tokens
  02_pruebas_hipotesis_una_muestra.md#4          283 tokens
  03_pruebas_dos_muestras.md#0                   455 tokens
  03_pruebas_dos_muestras.md#1                   454 tokens
  03_pruebas_dos_muestras.md#2                   495 tokens
  03_pruebas_dos_muestras.md#3                   382 tokens
  03_pruebas_dos_muestras.md#4                   186 tokens
  04_chi_cuadrada_y_anova.md#0                   483 tokens
  04_chi_cuadrada_y_anova.md#1                   494 tokens
  04_chi_cuadrada_y_anova.md#2                   442 tokens
  04_chi_cuadrada_y_anova.md#3                   480 tokens
  04_chi_cuadrada_y_anova.md#4                   101 tokens
```

Segunda corrida, sin `--force` (no reindexa):

```text
INFO ingesta: La colección ya existe con 20 chunks: no se reindexa.
Sin cambios (ya estaba indexado): 20 chunks de 4 archivos.
```

### Recuperación (real) y respuesta (SIMULADA)

Salida de `python rag.py` **sin clave**. Ojo al leerla:

- **La recuperación es real**: los fragmentos y las distancias salen de ChromaDB con los embeddings locales.
- **La respuesta es SIMULADA**: la escribe `modelo_falso.py`, que tiene el texto de la prueba 1 escrito a mano y contesta "No lo sé" a cualquier otra cosa. Sirve para mostrar que la cadena, el parser y las referencias funcionan, **no** para demostrar que un LLM no alucina.

```text
WARNING rag: MODO DEMOSTRACIÓN: sin OPENAI_API_KEY se usa un modelo falso guionado.
========================================================================
MODO DEMOSTRACIÓN: la recuperación es REAL; la respuesta la escribe un
modelo FALSO con texto fijo (no hay API key). Ver README.
========================================================================

### Prueba 1: pregunta con respuesta en los apuntes

Pregunta: ¿Cómo se calcula un intervalo de confianza para la media cuando la desviación estándar de la población es desconocida y la muestra es chica?
  1. 01_estimacion_intervalos_confianza.md#1    distancia coseno=0.0890
     «Para estimar la varianza poblacional se usa s² con denominador n − 1 y no n. Dividir por n − 1 es lo que hace que s² sea un estimador insesgado de σ². A ese n −…»
  2. 01_estimacion_intervalos_confianza.md#2    distancia coseno=0.0924
     «Hay un trade-off: un nivel de confianza más alto da un intervalo más ancho, y un intervalo más ancho es menos preciso. Para tener a la vez alta confianza e inte…»
  3. 01_estimacion_intervalos_confianza.md#4    distancia coseno=0.0926
     «**Ejemplo.** En una encuesta a 200 aspirantes, 58 dicen que eligieron la carrera por la modalidad virtual. Entonces p̄ = 58 / 200 = 0,29. - σ̂_p̄ = √(0,29 · 0,7…»
  4. 02_pruebas_hipotesis_una_muestra.md#3      distancia coseno=0.1045
     «Si n < 30, σ es desconocida y la población es aproximadamente normal, se usa: t = (x̄ − μ_H0) / (s / √n), con n − 1 grados de libertad. **Ejemplo.** Un centro d…»
Respuesta:
{
  "pregunta": "¿Cómo se calcula un intervalo de confianza para la media cuando la desviación estándar de la población es desconocida y la muestra es chica?",
  "respuesta": "Se usa la distribución t de Student con n − 1 grados de libertad: x̄ ± t · (s / √n), suponiendo que la población es aproximadamente normal.",
  "encontrada": true,
  "referencias": [
    {
      "chunk_id": "01_estimacion_intervalos_confianza.md#2",
      "fuente": "01_estimacion_intervalos_confianza.md",
      "fragmento": "Hay un trade-off: un nivel de confianza más alto da un intervalo más ancho, y un intervalo más ancho es menos preciso. Para tener a la vez alta confianza e intervalo angosto hay que aumentar el tamaño de la muestra. ## 5"
    }
  ]
}

### Prueba 2: pregunta trampa (no está en los apuntes)

Pregunta: ¿Cómo se interpreta el coeficiente de determinación R² en una regresión lineal múltiple?
  1. 02_pruebas_hipotesis_una_muestra.md#1      distancia coseno=0.1533
     «Para un tamaño de muestra fijo, bajar α hace subir β, y viceversa. La única forma de reducir los dos a la vez es aumentar el tamaño de la muestra. La elección d…»
  2. 01_estimacion_intervalos_confianza.md#1    distancia coseno=0.1549
     «Para estimar la varianza poblacional se usa s² con denominador n − 1 y no n. Dividir por n − 1 es lo que hace que s² sea un estimador insesgado de σ². A ese n −…»
  3. 03_pruebas_dos_muestras.md#0               distancia coseno=0.1615
     «# Unidad 3 — Pruebas de hipótesis de dos muestras Apuntes propios de Matemática y Estadística 2 (orden de temas de Levin y Rubin). Los ejemplos numéricos son in…»
  4. 01_estimacion_intervalos_confianza.md#4    distancia coseno=0.1623
     «**Ejemplo.** En una encuesta a 200 aspirantes, 58 dicen que eligieron la carrera por la modalidad virtual. Entonces p̄ = 58 / 200 = 0,29. - σ̂_p̄ = √(0,29 · 0,7…»
Respuesta:
{
  "pregunta": "¿Cómo se interpreta el coeficiente de determinación R² en una regresión lineal múltiple?",
  "respuesta": "No lo sé",
  "encontrada": false,
  "referencias": []
}
```

Qué se ve en la recuperación:

- **Prueba 1:** los 3 primeros fragmentos son del apunte de estimación, y el que tiene la respuesta (`01_…#2`, donde está "x̄ ± t · (s / √n)") sale segundo. El cuarto es de pruebas de una muestra y también habla de la t con σ desconocida.
- **Prueba 2 (trampa):** ningún fragmento habla de regresión ni de R², porque los apuntes no cubren ese tema. ChromaDB igual devuelve 4 fragmentos (siempre devuelve los k más parecidos, aunque sean malos), pero todos están más lejos (distancia 0,153 a 0,162) que los de la prueba 1 (0,089 a 0,105). Ahí es donde el prompt tiene que hacer su trabajo: con un contexto que no responde, el modelo tiene que decir "No lo sé".

Sobre las distancias: con este modelo (E5) todas quedan bastante juntas, entre 0 y 0,3. Lo que importa es la comparación, no el número suelto.

### Respuesta con un LLM real (completar)

Cuando tengas la clave en el `.env`, corré `python rag.py` y pegá acá la salida. El encabezado de "MODO DEMOSTRACIÓN" no debería aparecer.

```text
(pegar acá la salida de python rag.py con Gemini o Groq)
```

Qué revisar:

1. En la prueba 1, que la respuesta mencione la t de Student con n − 1 grados de libertad y cite `01_estimacion_intervalos_confianza.md#2`.
2. En la prueba 2, que diga exactamente `"No lo sé"`, con `"encontrada": false` y sin referencias. Si el modelo explica qué es R² (que lo sabe de su entrenamiento), **alucinó por fuera del contexto** y hay que endurecer el prompt.

## Cómo funciona (para estudiar)

### El recorrido completo

```text
            INGESTA (ingest.py, una sola vez)
data/*.md ─► cargar ─► cortar en chunks ─► embeddings ─► ChromaDB (./vectorstore)

            CONSULTA (rag.py, cada pregunta)
pregunta ─► embedding ─► ChromaDB: 4 chunks más parecidos ─► prompt con CONTEXTO
        ─► LLM (await) ─► PydanticOutputParser ─► armar_respuesta ─► RAGResponse
```

RAG significa *Retrieval-Augmented Generation*: generación aumentada con recuperación. El modelo de lenguaje no "sabe" nuestros apuntes; antes de cada respuesta le buscamos los pedazos relevantes y se los pegamos en el prompt. Así responde con información nuestra y verificable, y se puede ver de dónde sacó cada cosa.

### 1. Ingesta: `ingest.py`

1. **Cargar.** `cargar_documentos()` lee cada `.md` y `.txt` de `data/` y lo convierte en un `Document` de LangChain (texto + metadatos con el nombre del archivo).
2. **Cortar (chunking).** Un apunte entero es demasiado largo para buscar con precisión: su embedding sería un "promedio" de muchos temas. Por eso se corta en pedazos de **hasta 500 tokens** con **50 de solapamiento**. Lo hace `RecursiveCharacterTextSplitter`, que prueba separadores en orden: primero títulos de Markdown (`## `), después párrafos, después renglones y recién al final palabras. Así casi nunca parte una idea por la mitad.
3. **Ponerle un id a cada chunk.** `archivo#número`, por ejemplo `01_estimacion_intervalos_confianza.md#2`. Ese id es la "referencia" que después aparece en la respuesta.
4. **Embeber.** El modelo de embeddings convierte cada chunk en un vector de 384 números. Textos que hablan de lo mismo quedan con vectores parecidos.
5. **Guardar.** `chromadb.PersistentClient` escribe todo en `./vectorstore`. La colección guarda también qué modelo de embeddings se usó y que la distancia es coseno.

**Persistencia.** Antes de hacer todo eso, `ingestar()` se fija si la colección ya existe y tiene datos. Si existe, no reindexa (no recalcula embeddings: ahorra tiempo y, con embeddings pagos, plata). Para reindexar a propósito: `--force`, que borra la colección y la arma de nuevo (sin duplicar chunks).

### 2. Recuperación: el retriever

`vectorstore.as_retriever(search_kwargs={"k": 4})` hace esto con cada pregunta:

1. Convierte la pregunta en un vector **con el mismo modelo de embeddings** que se usó para indexar.
2. Busca en ChromaDB los 4 vectores más cercanos (menor distancia coseno).
3. Devuelve esos 4 chunks como `Document`, con su texto y sus metadatos.

### 3. Generación grounded: la cadena LCEL

LCEL (*LangChain Expression Language*) es la forma de encadenar pasos con `|`, como tuberías. La cadena de `construir_cadena()` es:

```python
RunnableParallel(documentos=retriever, pregunta=RunnablePassthrough())
| RunnablePassthrough.assign(
      salida_modelo = formatear_documentos | prompt | llm | PydanticOutputParser
  )
| RunnableLambda(armar_respuesta)
```

Paso por paso:

1. **`RunnableParallel`** recibe la pregunta y arma un diccionario con dos cosas: los documentos que trae el retriever y la pregunta tal cual.
2. **Transformador de documentos** (`formatear_documentos`): convierte la lista de chunks en un solo texto, cada uno con su id entre corchetes, así el modelo puede citarlos.
3. **Prompt** (`ChatPromptTemplate`): un mensaje de sistema con el **filtro de veracidad** y un mensaje de usuario con `CONTEXTO:` y `PREGUNTA:`.
4. **LLM**: `ChatOpenAI` (Gemini o Groq) o el modelo falso. Se llama con `await cadena.ainvoke(...)`, o sea, de forma asíncrona.
5. **`PydanticOutputParser`**: le agrega al prompt las instrucciones de formato (un esquema JSON) y después lee la respuesta del modelo y la valida contra `RespuestaDelModelo` (`respuesta` + `fuentes`). Si el JSON viene roto, se reintenta una vez (`with_retry`).
6. **`armar_respuesta`**: arma el `RAGResponse` final. Las referencias se construyen con los chunks que **de verdad** se recuperaron: si el modelo cita un id que no estaba en el contexto, se descarta. Si la respuesta es "No lo sé" (con o sin punto o tilde), se normaliza a `"No lo sé"` exacto y se dejan las referencias vacías.

### 4. El filtro de veracidad

El mensaje de sistema (`MENSAJE_SISTEMA` en `rag.py`) dice, en resumen:

> Respondé ÚNICAMENTE con la información del CONTEXTO. No uses lo que sepas por tu cuenta, aunque estés seguro. Si la respuesta no está en el CONTEXTO, o solo se menciona sin explicarse, respondé exactamente "No lo sé" y dejá la lista de fuentes vacía.

La frase "aunque estés seguro" es importante: la pregunta trampa (R² en regresión) es de estadística, el modelo la sabe responder de memoria, y justamente por eso es una buena trampa. Un RAG bien hecho no tiene que usar ese conocimiento.

### 5. `get_rag_response(query)`

```python
respuesta = await get_rag_response("¿Qué es el valor p?")
respuesta.respuesta      # el texto
respuesta.encontrada     # False si es "No lo sé"
respuesta.referencias    # [Referencia(chunk_id, fuente, fragmento), ...]
```

Rechaza una pregunta vacía antes de gastar una llamada. La cadena se arma una sola vez y se reutiliza.

## Decisiones de diseño

| Tema | Qué hice | Por qué | Dónde cambiarlo |
| --- | --- | --- | --- |
| Modelo de embeddings | `intfloat/multilingual-e5-small` | Gratis, corre en CPU, entiende español y acepta hasta 512 tokens. Los `MiniLM` más conocidos cortan el texto antes: `paraphrase-multilingual-MiniLM-L12-v2` a los 128 tokens y `all-MiniLM-L6-v2` (pensado para inglés) a los 256. Con chunks de 500, buena parte de cada chunk no se habría tenido en cuenta | `MODELO_EMBEDDINGS` en `config.py` |
| Prefijos `passage:` / `query:` | Se agregan solos en `EmbeddingsE5` | La familia E5 se entrenó así; sin los prefijos busca peor | `config.py` |
| Mismo embedding siempre | Un solo `obtener_embeddings()` para los dos scripts, y la colección guarda el nombre del modelo | Si se indexa con un modelo y se consulta con otro, las distancias no significan nada (el error #1 de la consigna). Si no coinciden, el programa frena con `EmbeddingsDistintos` | `config.py`, `ingest.py`, `rag.py` |
| Unidad del chunk | **Tokens del tokenizer del modelo de embeddings**, no caracteres | Así 500 tokens + prefijo entran en los 512 del modelo y nada se trunca | `crear_splitter()` en `ingest.py` |
| Tamaño y solapamiento | `chunk_size=500`, `chunk_overlap=50` (lo que pide la consigna) | 500 es el tope de cada chunk; los chunks salen de 101 a 499 tokens porque el splitter corta en un título o párrafo antes de pasarse. El último chunk de cada archivo es más corto porque es lo que sobra. Medidos con el tokenizer de OpenAI (`tiktoken`, `cl100k_base`), los mismos chunks dan de 117 a 613 tokens: el de E5 cuenta distinto | `TAMANO_CHUNK` y `SOLAPAMIENTO_CHUNK` en `config.py` |
| Cómo se da el solapamiento | Hasta 50 tokens, en piezas enteras | El splitter repite al principio del chunk siguiente los últimos párrafos o renglones completos que entren en 50 tokens. Si el último párrafo es más largo, ese par no comparte texto (pasa en 5 de los 16 pares) | — |
| Separadores | Los de Markdown (`get_separators_for_language(Language.MARKDOWN)`) | Cortar primero por títulos deja cada chunk con un tema | `crear_splitter()` |
| `top_k` | 4 | La consigna pide 3 a 5. Con 4 × 500 tokens el contexto queda en ~2.000 tokens: alcanza para preguntas que cruzan dos secciones y no cae en "Lost in the Middle" | `TOP_K` en `config.py` |
| Distancia | Coseno (`hnsw:space: cosine`) con vectores normalizados | Es la que recomienda E5 | `ingest.py` |
| Persistencia | `PersistentClient` en `./vectorstore`; si existe, no reindexa | Pedido de la consigna | `ingestar()` |
| Salida del LLM | `PydanticOutputParser` (JSON en texto) en lugar de `with_structured_output` | La consigna pide `PydanticOutputParser`. Además no depende de que el proveedor gratis soporte tool calling | `construir_cadena()` |
| Referencias | Se arman con los chunks recuperados, no con lo que diga el modelo | El modelo no puede inventar una fuente | `armar_respuesta()` |
| Respuesta sin citas | Si el modelo responde algo pero no cita, se ponen como referencia los 4 chunks del contexto (y se loguea un aviso) | Es el contexto que tuvo; mejor eso que nada | `armar_respuesta()` |
| Temperatura | 0 | Respuestas más estables y menos "creativas" | `crear_llm()` |
| Reintentos | 1 reintento si el JSON vuelve roto | Los modelos chicos a veces agregan texto fuera del JSON | `INTENTOS_MAXIMOS` en `config.py` |
| Proveedor del LLM | `ChatOpenAI` con `OPENAI_BASE_URL` (OpenAI, Gemini o Groq). A diferencia de la pre-entrega 2, no incluí Anthropic | Naza usa proveedores gratis; menos dependencias | `crear_llm()` y `entorno.py` |
| Sin clave | Modelo falso guionado | Poder correr y testear todo gratis | `modelo_falso.py` |

## Modo demostración

Si `OPENAI_API_KEY` está vacía, o es el texto de ejemplo, o `LLM_PROVIDER=demo`, `rag.py` usa `ModeloFalso`:

- Para la pregunta 1 tiene una respuesta **escrita a mano** y cita los fragmentos del contexto que contienen "t de Student".
- Para cualquier otra pregunta dice "No lo sé".

Lo que **sí** prueba: que la recuperación, el prompt, el parser de Pydantic y el armado de referencias funcionan de punta a punta. Lo que **no** prueba: que un LLM real respete el filtro de veracidad. Eso solo se ve con una clave (sección "Respuesta con un LLM real").

## Tests

```bash
python -m pytest
```

24 tests, sin clave y sin llamar a ninguna API:

- **`tests/test_ingesta.py`**: hay 3 o 4 archivos; ningún chunk pasa de 500 tokens y todos entran en los 512 del modelo; hay al menos 3 chunks por archivo; el solapamiento nunca pasa de 50 tokens; los ids son únicos y estables; **persistencia** (la segunda corrida no reindexa y la cuenta de chunks no cambia); `--force` reindexa sin duplicar; frena si se quiere usar otro modelo de embeddings; la colección guarda el modelo y la distancia coseno. Estos usan embeddings falsos (vectores fijos al azar), porque prueban la mecánica, no la relevancia.
- **`tests/test_cadena.py`**: con `FakeListChatModel`, la pregunta normal devuelve texto y referencias; la **trampa** devuelve "No lo sé" exacto sin referencias; se descartan fuentes inventadas; un JSON roto se reintenta; un JSON dentro de un bloque Markdown se lee igual; una pregunta vacía falla antes de llamar; el prompt lleva el contexto con ids y el filtro de veracidad; `top_k` fuera de 3 a 5 falla. Con **embeddings reales y ChromaDB real**: el retriever trae exactamente 4 chunks; para la pregunta 1 trae el chunk con la fórmula de la t; la trampa queda más lejos que la pregunta buena y no trae nada de regresión; la cadena completa con el modelo falso da la respuesta y el "No lo sé".
- **`tests/test_entorno.py`**: sin clave o con la clave de ejemplo se usa el modelo falso; con clave y `OPENAI_BASE_URL` se arma un `ChatOpenAI` apuntando a Gemini (sin llamarlo); `LLM_PROVIDER=demo` fuerza el modelo falso.

Los tests con embeddings reales usan el modelo descargado; si no se puede descargar (sin internet la primera vez), se saltean solos.

## Limitaciones

- **No se probó con un LLM real.** No había clave. La respuesta de las dos pruebas del apartado de salida es simulada. El "No lo sé" de la trampa con un modelo real queda por comprobar.
- **La trampa depende del prompt.** ChromaDB siempre devuelve 4 fragmentos aunque no sirvan; no hay un umbral de distancia que corte antes. Se podría agregar (por ejemplo, si el mejor fragmento está a más de 0,14, contestar "No lo sé" sin llamar al LLM), pero el número habría que calibrarlo con más preguntas.
- **La vista previa de cada referencia** es el comienzo del chunk (220 caracteres), que no siempre es la parte que responde. El chunk completo está en la base.
- **Un solo idioma probado**: los apuntes y las preguntas están en español.
- Los apuntes son un resumen propio: sirven para el ejercicio pero no reemplazan al libro.
