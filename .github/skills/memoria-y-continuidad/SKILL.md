---
name: memoria-y-continuidad
description: Recupera o conserva contexto duradero para retomar proyectos entre conversaciones - decisiones, estado, pendientes y siguiente acción. Úsala cuando pidan recordar algo, continuar trabajo de otro chat, o preparar un traspaso o resumen de estado.
---

# Memoria y continuidad

Una skill no crea memoria persistente ni acceso automático a otras conversaciones: solo persiste lo que quede escrito en un archivo o recuperable con una herramienta que observes funcionando. VS Code conserva el historial de sesiones de chat (se pueden reanudar desde la vista de sesiones), y si la organización tiene Copilot Memory habilitada, Copilot puede recordar preferencias entre sesiones de forma nativa; verifica si esa función está disponible en esta cuenta antes de asumirlo, en vez de darlo por hecho.

## Recuperar
1. Distingue **preferencias estables**, **reglas del proyecto** y **estado temporal**.
2. Reutiliza primero el contexto actual y los documentos de estado ya identificados; comprueba que la evidencia recuperada siga vigente antes de actuar.
3. Para traer contexto de otro chat, usa solo las herramientas de conversaciones que el entorno exponga y lee los turnos mínimos necesarios, sin explorar conversaciones ajenas al encargo. Si varias podrían ser la fuente y elegir cambia el trabajo, pide la identificación; si no hay acceso, pide solo el enlace, archivo o resumen indispensable y avanza lo independiente.

## Conservar
1. Usa memoria nativa solo si el entorno expone una capacidad verificable para esa operación. Guardar una preferencia en la conversación no la lleva a otro chat.
2. **Reglas estables** → `AGENTS.md` del repositorio (breve, y solo si la tarea autoriza modificarlo). **Progreso cambiante** → el documento de estado que ya exista o un resumen pequeño en el proyecto. Sin proyecto, usa el espacio de trabajo autorizado.
3. Lee el estado existente antes de escribir y **sustituye lo obsoleto** en vez de acumular transcripciones. Conserva: objetivo, alcance, decisiones y razones, restricciones, estado confirmado, pendientes, rutas de fuentes y siguiente acción; marca incertidumbres y fechas.
4. No edites almacenes de memoria generados ni guardes secretos, credenciales o datos personales sensibles.
5. Informa qué archivo guardaste y cómo referenciarlo en otro chat; un archivo disponible no implica que se cargue solo. Afirma persistencia o recuperación solo tras observar el resultado.

**Perfil de modelo:** L.
