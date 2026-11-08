---
name: eficiencia-de-contexto
description: Reduce lecturas, llamadas a herramientas y consumo de cuota en tareas largas, con muchos archivos o investigación multi-fuente, sin perder evidencia. Úsala cuando pidan ahorrar tiempo o tokens, o al notar contexto saturado o cuota agotándose.
---

# Eficiencia de contexto y cuota

En Copilot cada interacción consume créditos de IA según el modelo y los tokens usados (entrada, salida y caché), y un contexto saturado además empeora la calidad. En el plan Student los créditos incluidos son pocos, así que ahorrar bien significa hacer menos trabajo redundante, no recortar verificaciones.

## Reglas
1. **Fija el criterio de término** del resultado esperado y reutiliza lo ya leído antes de volver a buscar.
2. **Lee con puntería:** búsquedas dirigidas, secciones pertinentes, salidas filtradas. Nada de colecciones completas por defecto.
3. **Delega la exploración amplia** a un subagente (herramienta `runSubagent`, o el agente `investigador` de este paquete) y pide un resumen con rutas y evidencia; el subagente empieza sin contexto, así que da tarea, rutas y formato de respuesta. Así el main agent no carga con cientos de archivos leídos de más.
4. **Conserva rutas y evidencia** de cada hallazgo para no releer. Vuelve a comprobar solo si hubo cambios, contradicciones o dependencia temporal.
5. **Agrupa lecturas independientes** y evita llamadas repetidas, escaneos amplios y planes narrados que no ayudan.
6. **Método simple primero.** Escribe un script solo si el trabajo es repetitivo y determinista y el ahorro supera el costo de prepararlo.
7. **Web:** consultas concretas, fuentes primarias, y para cuando la evidencia baste.
8. **Mantén** toda verificación que el usuario pidió, que sostenga una afirmación o que el riesgo exija. Nunca presentes como comprobado algo que no verificaste.
9. No atribuyas ahorros exactos de tokens o tiempo sin medición.

**Perfil de modelo:** L.
