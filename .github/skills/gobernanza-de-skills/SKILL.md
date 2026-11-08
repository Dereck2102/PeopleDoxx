---
name: gobernanza-de-skills
description: Diagnostica por qué una skill no se activa, se activa mal o da resultados inconsistentes; corrige solapamientos y audita el catálogo (estructura, descripciones, enlaces). Úsala solo al mantener, instalar o depurar skills de Copilot, no en tareas de código cotidianas.
disable-model-invocation: true
---

# Gobernanza del catálogo de skills

Es una skill de **mantenimiento**. Por eso lleva `disable-model-invocation: true`: no se carga sola, solo se invoca a propósito con `/gobernanza-de-skills`. Cargarla en cada tarea gastaría contexto y créditos de IA sin aportar nada al trabajo normal.

## Cómo decide Copilot
En cada turno Copilot solo ve `name` y `description` de cada skill; lee el cuerpo completo únicamente si la descripción parece relevante para la petición. Por eso:
- Si la skill **no se elige** o se elige fuera de alcance → corrige la `description`.
- Si **se elige pero actúa mal** → corrige el cuerpo, los scripts o las referencias.

## Diagnóstico
1. **Descubrimiento.** Comprueba las rutas: proyecto `.github/skills/<skill>/` y personal `~/.copilot/skills/<skill>/`. Ejecuta **Chat: Open Customizations** desde la paleta de comandos (o el panel lateral de Agents) y abre la pestaña **Skills**: ahí se ve qué skills detectó Copilot, su origen y si hay archivos faltantes. Una skill nueva o editada se recoge al abrir una sesión de chat nueva.
2. **Selección.** Busca evidencia concreta: la petición que no activa la skill, la activación fuera de alcance, o dos skills que se disputan lo mismo. Mantén los disparadores específicos y las fronteras explícitas ("para X usa `otra-skill`"). Acortar caracteres no demuestra ahorro total.
3. **Dependencias.** Verifica que cada herramienta, script o archivo que la skill nombra exista de verdad (usa el script de abajo). Una instrucción que cita una herramienta inexistente bloquea trabajo autorizado.
4. **Comportamiento.** Reproduce con un prompt realista con `/<nombre-de-skill>` y compara con el resultado esperado.

## Auditoría estructural
```
python scripts/audit_catalog.py --root <carpeta-con-skills> [--json salida.json]
```
Revisa frontmatter, nombre = carpeta, longitud de descripción, longitud del cuerpo, nombres duplicados y enlaces o rutas rotas. Ejecútalo con `--help` primero si dudas. La comprobación estructural **no** acredita comportamiento.

## Evaluación de cambios sustanciales
Sigue `references/evaluacion.md`. Prueba la activación con al menos dos modelos distintos de los que tengas disponibles (por ejemplo uno ligero y uno más capaz), porque el enrutado puede variar según el modelo.

## Al mejorar
Mejora una skill existente si ya cubre el flujo antes de crear otra. Mueve mecánica repetida a `scripts/` y detalle condicional a `references/`. Antes de instalar cambios, haz respaldo y evita pisar ediciones concurrentes. Conserva `name` (coincide con el directorio y con el comando `/<nombre>`). Entrega fallos corregidos, resultados observados y límites pendientes; no declares garantizada la selección automática.

**Perfil de modelo:** E.
