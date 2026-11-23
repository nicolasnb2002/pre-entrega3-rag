# Unidad 4 — Chi-cuadrada y análisis de varianza (ANOVA)

Apuntes propios de Matemática y Estadística 2 siguiendo el capítulo de Levin y Rubin sobre chi-cuadrada y análisis de varianza. Los ejemplos numéricos son inventados.

## 1. Qué problemas resuelven

Las pruebas de las unidades anteriores comparan una o dos medias o proporciones. En esta unidad aparecen herramientas para casos con **más de dos grupos o categorías**:

- La **prueba chi-cuadrada de independencia** analiza si dos variables categóricas están relacionadas.
- La **prueba chi-cuadrada de bondad de ajuste** analiza si los datos siguen una distribución teórica.
- El **análisis de varianza (ANOVA)** compara las medias de tres o más poblaciones a la vez.
- La **prueba chi-cuadrada para una varianza** analiza si la varianza de una población es igual a un valor dado.

## 2. La distribución chi-cuadrada

La distribución chi-cuadrada (χ²) no toma valores negativos, es asimétrica hacia la derecha y su forma depende de los grados de libertad: con pocos grados de libertad es muy sesgada, y a medida que aumentan se vuelve más simétrica. En las pruebas de independencia y de bondad de ajuste la región de rechazo está siempre en la **cola derecha**, porque valores grandes de χ² indican que lo observado se aleja mucho de lo esperado.

## 3. Prueba de independencia: tablas de contingencia

Los datos se organizan en una **tabla de contingencia** con r filas y c columnas. Las hipótesis son:

- H0: las dos variables son independientes.
- H1: las dos variables no son independientes (están relacionadas).

Para cada celda se calcula la **frecuencia esperada** suponiendo que H0 es verdadera:

fe = (total de la fila · total de la columna) / total general

El estadístico es:

χ² = Σ (fo − fe)² / fe

donde fo es la frecuencia observada. Los grados de libertad son **(r − 1) · (c − 1)**.

Condición de uso: cada frecuencia esperada debe ser **al menos 5**. Si alguna es menor, conviene combinar categorías.

**Ejemplo.** ¿El resultado de una materia depende de la modalidad de cursada? Se observan 250 alumnos:

| Modalidad | Aprobó | Recursa | Abandonó | Total |
| --- | --- | --- | --- | --- |
| Presencial | 60 | 25 | 15 | 100 |
| A distancia | 70 | 45 | 35 | 150 |
| Total | 130 | 70 | 50 | 250 |

Frecuencias esperadas: para Presencial–Aprobó, 130 · 100 / 250 = 52. Siguiendo igual: Presencial 52, 28 y 20; A distancia 78, 42 y 30.

χ² = 64/52 + 9/28 + 25/20 + 64/78 + 9/42 + 25/30 = 1,231 + 0,321 + 1,250 + 0,821 + 0,214 + 0,833 = 4,67

Grados de libertad: (2 − 1) · (3 − 1) = 2. Valor crítico con α = 0,05: 5,991. Como 4,67 < 5,991, **no se rechaza H0**: con estos datos no hay evidencia suficiente de que el resultado dependa de la modalidad.

## 4. Prueba de bondad de ajuste

Sirve para ver si una distribución observada se ajusta a una distribución teórica (uniforme, binomial, Poisson, normal). Se calculan las frecuencias esperadas según el modelo teórico y se usa el mismo estadístico χ² = Σ (fo − fe)² / fe.

Los grados de libertad son **k − 1 − m**, donde k es la cantidad de categorías y m la cantidad de parámetros de la distribución teórica que se estimaron con la muestra. Por ejemplo, si se prueba un ajuste a una Poisson estimando la media λ con los datos, se pierde un grado de libertad adicional.

## 5. Análisis de varianza (ANOVA)

El ANOVA de un factor prueba si varias poblaciones tienen la misma media:

- H0: μ1 = μ2 = … = μk.
- H1: no todas las medias son iguales.

¿Por qué no hacer muchas pruebas t de a pares? Porque cada prueba tiene su propio riesgo de error tipo I y, al hacer muchas, la probabilidad de cometer al menos un error crece bastante. El ANOVA hace una sola prueba con un solo α.

Supuestos del ANOVA:

1. Cada población es aproximadamente normal.
2. Todas las poblaciones tienen la misma varianza.
3. Las muestras son aleatorias e independientes.

La idea central es comparar **dos estimaciones de la varianza poblacional σ²**:

- **Varianza entre columnas (entre grupos):** se basa en cuánto varían las medias muestrales alrededor de la gran media x̿.
  σ̂_b² = Σ n_j · (x̄_j − x̿)² / (k − 1)
- **Varianza dentro de columnas (dentro de los grupos):** promedio ponderado de las varianzas de cada muestra.
  σ̂_w² = Σ ((n_j − 1) / (n_T − k)) · s_j²

Si H0 es verdadera, las dos estimaciones deberían ser parecidas. Si las medias son distintas, la varianza entre columnas crece. El estadístico es el **cociente F**:

F = σ̂_b² / σ̂_w²

con **k − 1 grados de libertad en el numerador** y **n_T − k en el denominador**, donde k es la cantidad de grupos y n_T el total de observaciones. Valores de F cercanos a 1 apoyan H0; valores grandes llevan a rechazarla. La región de rechazo está en la cola derecha de la distribución F.

**Ejemplo.** Se comparan tres métodos de estudio con 5 alumnos cada uno (notas sobre 100):

- Método A: 70, 74, 68, 72, 76 → x̄_A = 72, s_A² = 10.
- Método B: 78, 80, 75, 82, 80 → x̄_B = 79, s_B² = 7.
- Método C: 69, 71, 73, 70, 67 → x̄_C = 70, s_C² = 5.

Gran media: x̿ = 1105 / 15 = 73,67.

- Entre columnas: σ̂_b² = 5 · [(72 − 73,67)² + (79 − 73,67)² + (70 − 73,67)²] / 2 = 5 · 44,67 / 2 = 111,67.
- Dentro de columnas: σ̂_w² = (4/12) · 10 + (4/12) · 7 + (4/12) · 5 = 7,33.
- F = 111,67 / 7,33 = 15,23.
- Grados de libertad: 2 en el numerador y 12 en el denominador. Valor crítico F con α = 0,05: 3,89.
- Como 15,23 > 3,89, **se rechaza H0**: al menos un método tiene una media distinta.

El ANOVA dice que hay diferencias, pero no dice **cuáles** medias difieren. Para eso hacen falta comparaciones posteriores.

## 6. Inferencia sobre una varianza

Para probar si la varianza de una población normal es igual a un valor σ0², se usa:

χ² = (n − 1) · s² / σ0², con n − 1 grados de libertad.

**Ejemplo.** Una máquina debería llenar envases con varianza σ0² = 1,5. Una muestra de 20 envases da s² = 2,6. ¿La variabilidad aumentó, con α = 0,05?

- χ² = 19 · 2,6 / 1,5 = 32,93.
- Valor crítico de cola derecha con 19 grados de libertad: 30,144.
- Como 32,93 > 30,144, se rechaza H0: la variabilidad parece mayor a la especificada.

## 7. Errores comunes

- Usar frecuencias relativas o porcentajes en lugar de frecuencias absolutas en la tabla de contingencia.
- Aplicar chi-cuadrada con frecuencias esperadas menores que 5.
- Concluir "causalidad" a partir de una prueba de independencia: solo muestra asociación.
- Olvidar que el ANOVA supone varianzas iguales entre grupos.
- Interpretar un F significativo como "todas las medias son distintas".
