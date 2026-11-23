# Unidad 1 — Estimación e intervalos de confianza

Apuntes propios de Matemática y Estadística 2, basados en la estructura del libro *Estadística para administración y economía* de Levin y Rubin (capítulo de estimación). Los ejemplos numéricos son inventados para estudiar.

## 1. Para qué sirve estimar

En casi todos los problemas reales no conocemos los parámetros de la población: la media poblacional μ, la desviación estándar poblacional σ o la proporción poblacional p. Lo que tenemos es una muestra. La estimación consiste en usar los datos de esa muestra para decir algo razonable sobre el parámetro desconocido.

Hay dos tipos de estimación:

- **Estimación puntual:** un solo número que usamos como mejor aproximación del parámetro. Por ejemplo, la media muestral x̄ es el estimador puntual de μ, la desviación estándar muestral s es el estimador puntual de σ y la proporción muestral p̄ es el estimador puntual de p.
- **Estimación de intervalo:** un rango de valores dentro del cual creemos que está el parámetro, junto con un nivel de confianza que dice qué tan seguros estamos del procedimiento.

La estimación puntual tiene un problema: casi nunca coincide exactamente con el parámetro, y por sí sola no dice qué tan lejos puede estar. El intervalo resuelve eso porque agrega una medida del error.

## 2. Propiedades de un buen estimador

Levin y Rubin destacan cuatro propiedades deseables:

1. **Insesgado:** el valor esperado del estimador es igual al parámetro. La media muestral x̄ es un estimador insesgado de μ.
2. **Eficiente:** entre dos estimadores insesgados, es más eficiente el que tiene menor error estándar. Un estimador eficiente varía menos de una muestra a otra.
3. **Consistente:** a medida que crece el tamaño de la muestra, el estimador se acerca cada vez más al parámetro.
4. **Suficiente:** usa toda la información que la muestra contiene sobre el parámetro.

Para estimar la varianza poblacional se usa s² con denominador n − 1 y no n. Dividir por n − 1 es lo que hace que s² sea un estimador insesgado de σ². A ese n − 1 se lo llama grados de libertad.

## 3. Error estándar de la media

La distribución muestral de la media tiene media μ y una desviación estándar llamada **error estándar de la media**:

σ_x̄ = σ / √n

Cuando la población es finita y la muestra es grande en relación con ella (más del 5 % de la población, es decir n/N > 0,05), se aplica el **multiplicador de población finita**:

σ_x̄ = (σ / √n) · √((N − n) / (N − 1))

Si no conocemos σ, la reemplazamos por s y obtenemos el error estándar estimado:

σ̂_x̄ = s / √n

Por el teorema central del límite, si n es grande (como regla práctica, n ≥ 30) la distribución de x̄ es aproximadamente normal aunque la población no lo sea.

## 4. Nivel de confianza y valor z

El **nivel de confianza** es la probabilidad de que el procedimiento genere un intervalo que contenga al parámetro. Los más usados son 90 %, 95 % y 99 %. Cada uno tiene su valor crítico z de la distribución normal estándar:

| Nivel de confianza | Valor z |
| --- | --- |
| 90 % | 1,645 |
| 95 % | 1,96 |
| 99 % | 2,575 |

Interpretación correcta de un intervalo del 95 %: si repitiéramos el muestreo muchas veces y en cada muestra armáramos un intervalo con el mismo método, alrededor del 95 % de esos intervalos contendrían a la media poblacional. No es correcto decir que "μ tiene 95 % de probabilidad de estar en este intervalo puntual", porque μ es fija: lo que varía es el intervalo.

Hay un trade-off: un nivel de confianza más alto da un intervalo más ancho, y un intervalo más ancho es menos preciso. Para tener a la vez alta confianza e intervalo angosto hay que aumentar el tamaño de la muestra.

## 5. Intervalo para la media con muestras grandes

Con n ≥ 30, el intervalo de confianza para μ es:

x̄ ± z · σ_x̄

y si σ es desconocida se usa σ̂_x̄ = s / √n.

**Ejemplo.** Una muestra de 64 estudiantes de la modalidad a distancia estudia en promedio x̄ = 12,5 horas por semana, con s = 4 horas. Queremos un intervalo del 95 %.

- Error estándar estimado: σ̂_x̄ = 4 / √64 = 4 / 8 = 0,5.
- Margen de error: 1,96 · 0,5 = 0,98.
- Intervalo: 12,5 ± 0,98, es decir, de 11,52 a 13,48 horas.

Conclusión: con 95 % de confianza, la media de horas de estudio semanales de la población está entre 11,52 y 13,48 horas.

## 6. Intervalo para la media con muestras chicas: distribución t de Student

Cuando la muestra es chica (n < 30) y **no conocemos la desviación estándar poblacional σ**, no podemos usar la normal. En ese caso se usa la **distribución t de Student**, siempre que la población sea aproximadamente normal.

Características de la distribución t:

- Es simétrica y con forma de campana, como la normal, pero con colas más pesadas: hay más probabilidad en los extremos.
- Hay una distribución t distinta para cada cantidad de **grados de libertad**. Para estimar una media, los grados de libertad son **n − 1**.
- A medida que aumentan los grados de libertad, la t se parece cada vez más a la normal estándar.

El intervalo es:

x̄ ± t · (s / √n)

donde t se busca en la tabla con n − 1 grados de libertad y el área de cola que corresponde al nivel de confianza. Ojo con la tabla de Levin y Rubin: la tabla t del libro se lee por el área total en las dos colas. Para un intervalo del 95 % se busca la columna 0,05.

**Ejemplo.** Diez exámenes parciales elegidos al azar tienen nota media x̄ = 78 puntos y s = 6 puntos. Queremos un intervalo del 95 %.

- Grados de libertad: 10 − 1 = 9.
- Valor t para 95 % y 9 grados de libertad: 2,262.
- Error estándar estimado: 6 / √10 = 1,897.
- Margen de error: 2,262 · 1,897 = 4,29.
- Intervalo: 78 ± 4,29, es decir, de 73,71 a 82,29 puntos.

Si hubiéramos usado z = 1,96 por error, el intervalo habría salido más angosto de lo que corresponde y la confianza real sería menor al 95 %.

Resumen de cuándo usar z o t para la media:

| Situación | Distribución |
| --- | --- |
| σ conocida (cualquier n si la población es normal, o n ≥ 30) | Normal (z) |
| σ desconocida y n ≥ 30 | Normal (z) usando s, como aproximación |
| σ desconocida, n < 30 y población aproximadamente normal | t de Student con n − 1 grados de libertad |

## 7. Intervalo para una proporción

Para proporciones, si n es grande (como regla, n·p y n·q mayores que 5), la distribución de p̄ se aproxima con una normal. El error estándar estimado de la proporción es:

σ̂_p̄ = √(p̄ · q̄ / n), con q̄ = 1 − p̄

y el intervalo es p̄ ± z · σ̂_p̄.

**Ejemplo.** En una encuesta a 200 aspirantes, 58 dicen que eligieron la carrera por la modalidad virtual. Entonces p̄ = 58 / 200 = 0,29.

- σ̂_p̄ = √(0,29 · 0,71 / 200) = √0,0010295 = 0,0321.
- Margen al 95 %: 1,96 · 0,0321 = 0,0629.
- Intervalo: de 0,227 a 0,353, o sea, entre 22,7 % y 35,3 %.

## 8. Tamaño de muestra

Antes de salir a muestrear conviene decidir qué error máximo E estamos dispuestos a aceptar y con qué confianza.

Para estimar una media, despejando de E = z · σ / √n:

n = (z · σ / E)²

**Ejemplo.** Si σ = 15, queremos un error máximo de E = 3 y 95 % de confianza: n = (1,96 · 15 / 3)² = 9,8² = 96,04. Siempre se redondea **hacia arriba**: n = 97.

Para estimar una proporción:

n = z² · p · q / E²

Si no tenemos idea de p, se usa p = 0,5 porque es el valor que hace máximo el producto p · q y da el tamaño de muestra más conservador. Por ejemplo, con 95 % de confianza y E = 0,04: n = 1,96² · 0,25 / 0,0016 = 600,25, que se redondea a 601.

## 9. Errores comunes al resolver ejercicios

- Usar z cuando corresponde t (muestra chica y σ desconocida).
- Olvidar el multiplicador de población finita cuando n/N > 0,05.
- Redondear el tamaño de muestra hacia abajo.
- Interpretar el nivel de confianza como la probabilidad de que el parámetro esté en un intervalo ya calculado.
- Confundir la desviación estándar de la población (σ) con el error estándar de la media (σ_x̄).
