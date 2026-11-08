---
name: qa-buenas-practicas
description: Aplica calidad basada en riesgo al implementar funcionalidades, corregir bugs, refactorizar o revisar código - criterios de aceptación, pruebas, seguridad y UX proporcionales. Úsala en casi cualquier trabajo de código, aunque el usuario no pida una auditoría.
---

# Aseguramiento de calidad y buenas prácticas

Ajusta la profundidad al riesgo: un cambio de texto puede requerir solo inspección; autenticación, datos o pagos piden más evidencia. Sirve también para planes de calidad de servicios y entregables.

## Ruta de trabajo
1. **Contexto:** lee requisitos, instrucciones del proyecto, implementación cercana y pruebas pertinentes. Traduce lo pedido a criterios observables y conserva contratos y convenciones. Pregunta solo por decisiones que cambien materialmente el resultado.
2. **Defecto:** define comportamiento esperado y observado, intenta reproducirlo en un entorno permitido y sigue el flujo hasta la causa. Si no reproduces, separa hipótesis de evidencia y usa inspección o una comprobación aislada antes de afirmar la causa. **Funcionalidad:** identifica entradas, estados, errores y compatibilidad afectados.
3. **Cambio:** si el encargo incluye implementar o corregir, resuelve la causa o cumple el criterio. En una *revisión*, entrega hallazgos sin editar. Revisa responsabilidades, duplicación, dependencias, errores y complejidad cuando el cambio los afecte; sin refactors ajenos al encargo.
4. **Controles** (tabla abajo). Profundiza con la skill especializada si el riesgo lo justifica; no cargues todas por cada cambio.
5. **Comprobaciones:** prefiere las pruebas existentes y añade una de regresión cuando proteja el comportamiento corregido o un riesgo sin cubrir. Elige compilación, análisis estático, prueba funcional o revisión visual según lo que puedan demostrar. No añadas pruebas que solo repitan la implementación. Tras pasar, repite solo ante cambios nuevos.

## Controles según el cambio
| Si el cambio… | Revisa |
|---|---|
| recibe datos externos | validación en el servidor, límites de tamaño o rango, uso seguro en consultas, comandos, rutas y HTML; la validación del cliente no basta |
| accede a recursos protegidos | autorización por operación, objeto y tenant; que errores, respuestas y logs no expongan secretos o datos ajenos |
| escribe, reintenta o es concurrente | integridad, duplicados, recuperación tras fallo parcial; no repitas una operación de resultado desconocido sin consultar su estado |
| cambia un flujo visible | teclado, foco, etiquetas, mensajes útiles; estados de carga, vacío, éxito, error y recuperación que existan; tamaños de pantalla (apoya con `ux-principios-diseno`) |
| exige un estándar | convenciones del proyecto; vincula a una norma solo si el alcance lo pide (ver `references/marcos-para-codigo.md`); no declares cumplimiento |

## Cierre con evidencia
Relaciona cada criterio importante con su comprobación y resultado. Informa qué cambió, qué se ejecutó y qué queda sin verificar (revisión estática ≠ prueba ejecutada). En auditorías, prioriza hallazgos con ubicación, evidencia, impacto y corrección verificable; sin hallazgos, indica alcance y limitaciones. No inventes cobertura, resultados ni conformidad.

**Perfil de modelo:** E; para cambios riesgosos, revisa con un modelo de otra familia de proveedor (por ejemplo Claude Haiku 4.5 si implementaste con un modelo OpenAI, o viceversa).
