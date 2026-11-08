---
name: documentacion-tecnica
description: Crea o actualiza README, guías, referencias de API, instalación, ADR y runbooks verificándolos contra el código y la configuración reales. Úsala siempre que se pida documentar, actualizar docs o escribir instrucciones de uso u operación.
---

# Documentación técnica

## Flujo
1. **Identifica** audiencia (usuarios, desarrolladores, operadores, soporte, auditores), propósito, versión, alcance y formato: guía, tutorial, referencia, arquitectura, ADR, runbook, instalación o solución de problemas.
2. **Verifica cada detalle** contra archivos, código, configuración o fuentes disponibles. No inventes comandos, parámetros, requisitos ni comportamiento; marca lo que no pudiste confirmar.
3. **Actualizar:** localiza primero la fuente mantenida y edítala ahí, para no crear una guía paralela que quede desfasada. Ata las instrucciones a una versión o entorno y revisa las referencias que el cambio afecta.
4. **APIs:** deriva autenticación, parámetros, tipos, errores y ejemplos del contrato o de la implementación. **Operaciones:** deriva comandos y recuperación de la configuración y procedimientos existentes; no deduzcas capacidades por el nombre de un comando.
5. **Procedimientos:** prerrequisitos → pasos ordenados → resultado esperado → comprobación → errores frecuentes → recuperación (los que apliquen).
6. **Ejemplos mínimos y comprobables.** Si está dentro del encargo, ejecútalos en un entorno permitido. Protege secretos y datos personales.

## Cierre
Mantén nombres, términos y enlaces coherentes con el producto y separa decisiones vigentes de propuestas. Indica qué contenido fue revisado, qué comandos se ejecutaron y qué pasos quedan por comprobar. Precisión antes que rapidez.

**Perfil de modelo:** L para documentar lo ya leído; E si hay que derivar el comportamiento de código complejo.
