---
name: ingenieria-bases-de-datos
description: Diseña esquemas y consultas, revisa índices, planes de ejecución, migraciones e integridad en bases de datos de aplicaciones (SQL/NoSQL). Úsala ante consultas lentas, cambios de esquema, migraciones o modelado; las plataformas analíticas distribuidas van en ingenieria-big-data.
---

# Ingeniería de bases de datos

## Flujo
1. **Identifica** motor y versión, volumen, carga de lectura/escritura, esquema, consistencia y disponibilidad requeridas y restricciones de cambio. Revisa definiciones y planes de consulta antes de recomendar optimizaciones.
2. **Diseña** preservando integridad y comportamiento esperado. Evalúa índices, cardinalidad, bloqueos, concurrencia, compatibilidad y recuperación.
3. **Migraciones:** prefiere cambios incrementales y reversibles. Comprueba lectura/escritura con las versiones de aplicación que coexistirán durante el despliegue y separa *expansión → backfill → retirada* cuando haga falta. Documenta impacto, respaldo y plan de reversión.
4. **Consulta lenta:** identifica el plan y la carga *antes* de añadir índices, y compara bajo condiciones equivalentes. `EXPLAIN ANALYZE` ejecuta la consulta: evalúa sus efectos y el entorno antes de usarlo, sobre todo con escrituras.
5. Usa documentación oficial vigente para las particularidades del motor.

## Límites
No ejecutes consultas destructivas ni cambios de esquema en entornos compartidos o productivos sin autorización explícita. No afirmes una mejora de rendimiento sin medición comparable.

**Perfil de modelo:** E; P para migraciones de tablas críticas o grandes.
