# Unidad 2 — Pruebas de hipótesis de una muestra

Apuntes propios de Matemática y Estadística 2, siguiendo el orden del libro de Levin y Rubin. Los ejemplos numéricos son inventados para practicar.

## 1. La idea de una prueba de hipótesis

Una prueba de hipótesis es un procedimiento para decidir, con datos de una muestra, si una afirmación sobre un parámetro poblacional es razonable o si la evidencia la contradice. La lógica es parecida a la de un juicio: se parte de suponer que el acusado es inocente y solo se lo declara culpable si la evidencia es lo bastante fuerte.

- **Hipótesis nula (H0):** la afirmación que se pone a prueba y que se supone verdadera mientras no haya evidencia en contra. Siempre incluye la igualdad, por ejemplo H0: μ = 500.
- **Hipótesis alternativa (H1):** lo que concluimos si rechazamos H0. Por ejemplo H1: μ ≠ 500, H1: μ > 500 o H1: μ < 500.

Importante: nunca "aceptamos" ni "probamos" H0. Si la evidencia no alcanza, decimos que **no se rechaza** H0. No rechazar no significa que H0 sea verdadera; significa que la muestra no aporta evidencia suficiente para descartarla.

## 2. Nivel de significancia y tipos de error

El **nivel de significancia α** es la probabilidad de rechazar H0 cuando en realidad es verdadera. Se fija antes de mirar los datos; los valores usuales son 0,10, 0,05 y 0,01.

Hay dos errores posibles:

| | H0 verdadera | H0 falsa |
| --- | --- | --- |
| Rechazo H0 | **Error tipo I** (probabilidad α) | Decisión correcta |
| No rechazo H0 | Decisión correcta | **Error tipo II** (probabilidad β) |

- El **error tipo I** es rechazar una hipótesis nula verdadera.
- El **error tipo II** es no rechazar una hipótesis nula falsa.
- La **potencia de la prueba** es 1 − β: la probabilidad de rechazar H0 cuando efectivamente es falsa.

Para un tamaño de muestra fijo, bajar α hace subir β, y viceversa. La única forma de reducir los dos a la vez es aumentar el tamaño de la muestra. La elección de α depende del costo de cada error: si el error tipo I es muy caro (por ejemplo, frenar una línea de producción que funcionaba bien), conviene un α chico.

## 3. Pruebas de una y de dos colas

- **Prueba de dos colas:** H1 dice "distinto" (≠). La región de rechazo se reparte en las dos colas, α/2 en cada una. Con α = 0,05 los valores críticos de z son −1,96 y +1,96.
- **Prueba de cola derecha (superior):** H1 dice "mayor que" (>). Toda la región de rechazo, α, está a la derecha. Con α = 0,05 el valor crítico es z = 1,645.
- **Prueba de cola izquierda (inferior):** H1 dice "menor que" (<). Con α = 0,05 el valor crítico es z = −1,645; con α = 0,01 es z = −2,33.

La elección entre una y dos colas sale de la pregunta del problema, no de los datos. Si el enunciado pregunta si la media "cambió", es de dos colas; si pregunta si "aumentó" o "es menor", es de una cola.

## 4. Pasos para resolver una prueba

1. Plantear H0 y H1.
2. Elegir el nivel de significancia α.
3. Elegir la distribución adecuada (z o t) y calcular el error estándar.
4. Calcular el estadístico de prueba estandarizado.
5. Comparar con el valor crítico (o calcular el valor p).
6. Decidir: rechazar o no rechazar H0.
7. Redactar la conclusión en el lenguaje del problema.

## 5. Prueba para la media con σ conocida (o muestra grande)

El estadístico es:

z = (x̄ − μ_H0) / σ_x̄, con σ_x̄ = σ / √n

**Ejemplo.** Una envasadora afirma que sus paquetes pesan en promedio 500 g, con σ = 12 g. Se toman 36 paquetes y la media muestral es x̄ = 495,2 g. ¿Hay evidencia, con α = 0,05, de que el peso medio es distinto de 500 g?

- H0: μ = 500; H1: μ ≠ 500 (dos colas).
- σ_x̄ = 12 / √36 = 2.
- z = (495,2 − 500) / 2 = −2,4.
- Valores críticos: ±1,96. Como −2,4 < −1,96, el estadístico cae en la región de rechazo.
- Decisión: se rechaza H0. Hay evidencia de que el peso medio es distinto de 500 g.

## 6. El valor p

El **valor p** es la probabilidad de obtener un estadístico tan extremo como el observado, o más, suponiendo que H0 es verdadera. Es el nivel de significancia más bajo al que se rechazaría H0 con esos datos.

Regla de decisión: si valor p < α, se rechaza H0; si valor p ≥ α, no se rechaza.

En el ejemplo de la envasadora, P(Z < −2,4) = 0,0082. Como la prueba es de dos colas, el valor p es 2 · 0,0082 = 0,0164. Como 0,0164 < 0,05, se rechaza H0, igual que con el valor crítico. Pero con α = 0,01 no se rechazaría.

La ventaja del valor p es que informa cuán fuerte es la evidencia, en lugar de dar solo un "sí" o "no".

## 7. Prueba para la media con muestra chica: t de Student

Si n < 30, σ es desconocida y la población es aproximadamente normal, se usa:

t = (x̄ − μ_H0) / (s / √n), con n − 1 grados de libertad.

**Ejemplo.** Un centro de atención dice que el tiempo medio de espera es de 20 minutos. Se observan 15 llamadas y se obtiene x̄ = 22,1 minutos con s = 3,5 minutos. Con α = 0,05, ¿hay evidencia de que la espera media es mayor que 20 minutos?

- H0: μ = 20; H1: μ > 20 (cola derecha).
- Grados de libertad: 14. Valor crítico t (una cola, 0,05): 1,761.
- Error estándar estimado: 3,5 / √15 = 0,904.
- t = (22,1 − 20) / 0,904 = 2,32.
- Como 2,32 > 1,761, se rechaza H0: la espera media parece mayor a 20 minutos.

## 8. Prueba para una proporción

Con n grande, el estadístico es:

z = (p̄ − p_H0) / σ_p̄, con σ_p̄ = √(p_H0 · q_H0 / n)

Atención: en la prueba de hipótesis el error estándar se calcula con la proporción de la hipótesis nula (p_H0), no con p̄. En cambio, en el intervalo de confianza se usa p̄ porque ahí no hay un valor hipotético.

**Ejemplo.** Una universidad sostiene que el 60 % de sus ingresantes trabaja. En una muestra de 150 ingresantes, el 52 % trabaja. Con α = 0,01, ¿hay evidencia de que la proporción real es menor al 60 %?

- H0: p = 0,60; H1: p < 0,60 (cola izquierda).
- σ_p̄ = √(0,6 · 0,4 / 150) = √0,0016 = 0,04.
- z = (0,52 − 0,60) / 0,04 = −2,0.
- Valor crítico con α = 0,01 a la izquierda: −2,33. Como −2,0 > −2,33, no cae en la región de rechazo.
- Valor p = P(Z < −2,0) = 0,0228, mayor que 0,01.
- Decisión: no se rechaza H0. Con este nivel de significancia la muestra no alcanza para afirmar que la proporción es menor al 60 %. Con α = 0,05 sí se habría rechazado, lo que muestra lo importante que es fijar α antes de mirar los datos.

## 9. Errores comunes

- Plantear la igualdad en la hipótesis alternativa.
- Decidir si la prueba es de una o dos colas mirando el resultado de la muestra.
- Decir "se acepta H0" o "queda probado que μ = 500".
- Usar p̄ en lugar de p_H0 para el error estándar de una prueba de proporción.
- Olvidar duplicar el valor p en una prueba de dos colas.
