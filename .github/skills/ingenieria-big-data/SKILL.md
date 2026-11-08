---
name: ingenieria-big-data
description: Diseña pipelines y plataformas de datos por lotes o streaming - ingestión, particionado, idempotencia, backfill, calidad y linaje. Úsala para ETL/ELT, lakehouse o streaming; la estadística va en ciencia-de-datos y las bases de aplicación en ingenieria-bases-de-datos.
---

# Ingeniería de datos y Big Data

## Flujo
1. **Aclara** fuentes, consumidores, volumen y crecimiento, latencia o frescura requerida, contratos, costos y disponibilidad. Verifica arquitectura y formatos existentes antes de proponer cambios.
2. **Diseña** ingestión, transformación, almacenamiento y entrega con esquemas y evolución explícitos, particionado adecuado, idempotencia, eventos tardíos, reintentos, checkpoints y recuperación. No prometas semántica "exactamente una vez" sin demostrar cómo la soporta la plataforma elegida.
3. **Al implementar**, define la clave de deduplicación y la política de reejecución o backfill. Comprueba el contrato de salida, los registros descartados y el tratamiento de errores permanentes; repetir un lote o recuperar un checkpoint debe tener un resultado explicable.
4. **Evalúa** corrección y frescura además de rendimiento. No exijas infraestructura distribuida si una ejecución simple cubre la carga.
5. Considera calidad y linaje, observabilidad, seguridad, control de acceso y costo de cómputo y almacenamiento. Para servicios concretos, usa su documentación oficial vigente.

## Entregable
Flujo, decisiones, fallos posibles y criterios operativos.

**Perfil de modelo:** E.
