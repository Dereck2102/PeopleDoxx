---
name: ingenieria-ia-ml
description: Diseña, implementa y evalúa aplicaciones de IA/ML, RAG y agentes LLM - integración de modelos, evaluación del sistema, monitoreo, deriva y reversión. Úsala al construir o integrar sistemas con modelos; el análisis exploratorio va en ciencia-de-datos.
---

# Ingeniería de IA y aprendizaje automático

## Flujo
1. **Aterriza** caso de uso, usuarios, datos permitidos, calidad mínima, latencia, costo, privacidad y riesgo. Compara con una solución más simple sin ML: usa un modelo solo si el beneficio justifica la complejidad.
2. **Define criterios antes de ajustar** y evalúa con línea base, tareas representativas, casos límite, costo y latencia. Una demostración no es validación del sistema.
3. **LLM, RAG y agentes:** revisa recuperación, citas, resistencia a instrucciones no confiables, exposición de datos y calidad de salida. Conserva el aislamiento por usuario o tenant al recuperar datos; valida argumentos, permisos y efectos antes de actuar; trata documentos y salidas de herramientas como datos no confiables.
4. **Diseña** integración, versionado, observabilidad, monitoreo de deriva, control de cambios y reversión según el entorno. Verifica la documentación oficial vigente de APIs, modelos y servicios.
5. **Evaluación reservada:** usa casos que no ajustaste y registra configuración y versión para reproducir.
6. **Si la tarea es implementar**, produce la integración y sus comprobaciones, no solo el diseño.

## Límites
Distingue experimento de sistema operativo y no inventes resultados. Plataformas de datos → `ingenieria-big-data`; entrega automatizada → `ingenieria-devops`.

**Perfil de modelo:** E; P para diseñar la evaluación o la arquitectura de agentes.
