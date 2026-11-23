# Unidad 3 — Pruebas de hipótesis de dos muestras

Apuntes propios de Matemática y Estadística 2 (orden de temas de Levin y Rubin). Los ejemplos numéricos son inventados.

## 1. Cuándo se usan

Muchas preguntas de negocios no comparan una muestra contra un valor fijo, sino **dos poblaciones entre sí**: ¿los alumnos de la modalidad a distancia rinden distinto que los presenciales?, ¿una campaña nueva convierte más que la anterior?, ¿un curso de nivelación mejora las notas de los mismos estudiantes?

En estas pruebas la hipótesis nula suele ser que no hay diferencia: H0: μ1 = μ2, que es lo mismo que H0: μ1 − μ2 = 0.

Lo primero es distinguir el tipo de muestras:

- **Muestras independientes:** los elementos de una muestra no tienen relación con los de la otra (por ejemplo, 50 alumnos presenciales y 60 alumnos a distancia, personas distintas).
- **Muestras dependientes o pareadas:** cada dato de una muestra está emparejado con un dato de la otra (por ejemplo, la nota de un mismo alumno antes y después de un curso).

## 2. Distribución muestral de la diferencia de medias

Si tomamos muchas muestras de dos poblaciones y calculamos x̄1 − x̄2 cada vez, esas diferencias forman una distribución muestral con media μ1 − μ2 y **error estándar de la diferencia**:

σ_(x̄1−x̄2) = √(σ1² / n1 + σ2² / n2)

Si no conocemos las varianzas poblacionales y las muestras son grandes, se estiman con s1² y s2²:

σ̂_(x̄1−x̄2) = √(s1² / n1 + s2² / n2)

## 3. Diferencia de medias con muestras grandes e independientes

El estadístico es:

z = ((x̄1 − x̄2) − (μ1 − μ2)_H0) / σ̂_(x̄1−x̄2)

**Ejemplo.** Se compara la nota final de dos comisiones. Comisión 1: n1 = 50, x̄1 = 74, s1 = 8. Comisión 2: n2 = 60, x̄2 = 70, s2 = 10. Con α = 0,05, ¿hay diferencia entre las medias?

- H0: μ1 = μ2; H1: μ1 ≠ μ2 (dos colas).
- σ̂ = √(64/50 + 100/60) = √(1,28 + 1,667) = √2,947 = 1,717.
- z = (74 − 70 − 0) / 1,717 = 2,33.
- Valores críticos: ±1,96. Como 2,33 > 1,96, se rechaza H0.
- Conclusión: hay evidencia de que las medias de las dos comisiones son distintas.

## 4. Diferencia de medias con muestras chicas: varianza combinada

Cuando las muestras son chicas, se usa la distribución t. El método clásico del libro supone que:

- las dos poblaciones son aproximadamente normales, y
- las dos poblaciones tienen la misma varianza (aunque desconocida).

Con ese supuesto, se combinan las dos varianzas muestrales en una **estimación combinada (pooled)**:

s_p² = ((n1 − 1) · s1² + (n2 − 1) · s2²) / (n1 + n2 − 2)

El error estándar estimado de la diferencia es:

σ̂_(x̄1−x̄2) = s_p · √(1/n1 + 1/n2)

y el estadístico t tiene **n1 + n2 − 2 grados de libertad**.

**Ejemplo.** Grupo A: n1 = 10, x̄1 = 25, s1 = 4. Grupo B: n2 = 12, x̄2 = 21, s2 = 5. Con α = 0,05 y dos colas:

- s_p² = (9 · 16 + 11 · 25) / 20 = (144 + 275) / 20 = 20,95, entonces s_p = 4,577.
- σ̂ = 4,577 · √(1/10 + 1/12) = 4,577 · 0,428 = 1,960.
- t = (25 − 21) / 1,960 = 2,04.
- Grados de libertad: 10 + 12 − 2 = 20. Valor crítico t (dos colas, 0,05): 2,086.
- Como 2,04 < 2,086, no se rechaza H0. La diferencia observada de 4 puntos no alcanza para afirmar, con α = 0,05, que las medias poblacionales sean distintas.

Este ejemplo muestra que el resultado puede quedar muy cerca del valor crítico: la conclusión depende de α y de la cantidad de datos.

## 5. Muestras dependientes (pareadas)

Cuando las observaciones vienen de a pares, no se usan las dos medias por separado. Se calcula la **diferencia d** de cada par y se trabaja con esas diferencias como si fuera una sola muestra:

- d̄ = media de las diferencias.
- s_d = desviación estándar de las diferencias.
- t = (d̄ − 0) / (s_d / √n), con n − 1 grados de libertad, donde n es la cantidad de pares.

La ventaja de las muestras pareadas es que eliminan la variabilidad entre individuos: cada persona se compara consigo misma.

**Ejemplo.** Seis alumnos rinden un simulacro antes y después de un curso de nivelación. La mejora media es d̄ = 2,5 puntos, con s_d = 2,0. ¿Mejoraron, con α = 0,05?

- H0: μ_d = 0; H1: μ_d > 0 (cola derecha).
- Error estándar: 2,0 / √6 = 0,816.
- t = 2,5 / 0,816 = 3,06.
- Grados de libertad: 5. Valor crítico (una cola, 0,05): 2,015.
- Como 3,06 > 2,015, se rechaza H0: hay evidencia de mejora.

Un error frecuente es tratar datos pareados como muestras independientes. Eso infla el error estándar y puede llevar a no detectar una diferencia que existe.

## 6. Diferencia de proporciones

Para comparar dos proporciones con muestras grandes, bajo H0: p1 = p2 se usa una **proporción combinada**:

p̂ = (n1 · p̄1 + n2 · p̄2) / (n1 + n2), con q̂ = 1 − p̂

El error estándar estimado es:

σ̂_(p̄1−p̄2) = √(p̂ · q̂ · (1/n1 + 1/n2))

y el estadístico es z = (p̄1 − p̄2) / σ̂_(p̄1−p̄2).

**Ejemplo.** Una campaña nueva consigue 84 inscripciones sobre 200 consultas (p̄1 = 0,42) y la campaña anterior 85 sobre 250 (p̄2 = 0,34).

- p̂ = (84 + 85) / 450 = 0,3756; q̂ = 0,6244.
- σ̂ = √(0,3756 · 0,6244 · (1/200 + 1/250)) = √(0,2345 · 0,009) = 0,0459.
- z = (0,42 − 0,34) / 0,0459 = 1,74.

Con α = 0,05:

- Si la pregunta es "¿hay diferencia?" (dos colas, críticos ±1,96), no se rechaza H0.
- Si la pregunta es "¿la campaña nueva convierte más?" (cola derecha, crítico 1,645), se rechaza H0.

Otra vez: la cantidad de colas tiene que salir del enunciado, decidida antes de mirar los datos.

## 7. Cuadro resumen

| Situación | Estadístico | Grados de libertad |
| --- | --- | --- |
| Medias, muestras grandes independientes | z con √(s1²/n1 + s2²/n2) | — |
| Medias, muestras chicas independientes, varianzas iguales | t con varianza combinada s_p² | n1 + n2 − 2 |
| Medias, muestras pareadas | t sobre las diferencias d | n − 1 (n = pares) |
| Proporciones, muestras grandes | z con proporción combinada p̂ | — |
