---
name: ciencia-de-datos
description: Analiza datos, diseña experimentos y construye modelos estadísticos o predictivos exploratorios y offline. Úsala para EDA, hipótesis, métricas, validación, A/B tests y evaluación de modelos; los pipelines van en ingenieria-big-data y la operación de modelos en ingenieria-ia-ml.
---

# Ciencia de datos

## Flujo
1. **Formula** la pregunta, la decisión que informará y la unidad de análisis.
2. **Audita los datos** antes de interpretar: procedencia, definiciones, granularidad, cobertura temporal, calidad, sesgos, faltantes y restricciones de privacidad.
3. **Elige análisis proporcional** al objetivo. Compara con una línea base, define métricas ligadas al costo de los errores y valida con una partición acorde al tiempo y al proceso que genera los datos. Reporta incertidumbre, limitaciones y supuestos.
4. **Modelado predictivo:** separa entrenamiento y evaluación *antes* de ajustar transformaciones, imputación o selección de variables, porque hacerlo después filtra información del conjunto de prueba. Verifica que cada variable existiera al momento de predecir. No ajustes repetidamente contra el conjunto reservado.
5. **Reproducibilidad:** conserva la definición de la métrica, el conjunto evaluado y los parámetros que permiten repetir el resultado.

## Límites
No presentes asociación como causalidad sin un diseño de identificación válido. No inventes calidad, representatividad ni resultados. Cada conclusión debe poder rastrearse a los datos y al método.

**Perfil de modelo:** E.
