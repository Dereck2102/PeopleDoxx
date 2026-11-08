# Evaluar cambios en una skill

Úsalo para cambios sustanciales (nueva skill, descripción reescrita, flujo modificado). Una comprobación estructural no demuestra comportamiento; esto sí lo acerca.

## 1. Prepara prompts realistas
Escribe como hablaría un usuario real, con la sustancia suficiente para que el agente necesite la skill (una petición trivial se resuelve sin skill aunque la descripción coincida).
- **3–5 que deben activarla**, con variaciones de vocabulario.
- **3–5 que no deben activarla**, incluidos los casi-aciertos que pertenecen a una skill vecina.

## 2. Ejecuta en sesión limpia
Una conversación nueva por prompt (el modelo elegido persiste dentro de una conversación). Anota qué skill se leyó: la pestaña **Skills** del Agent Customizations editor, o la vista de actividad de herramientas del chat, muestran si la skill se cargó.

## 3. Repite con dos modelos
El enrutado puede depender del modelo. Prueba al menos con un modelo ligero (por ejemplo GPT-6 Luna) y uno más capaz (por ejemplo Claude Haiku 4.5 o Kimi K3, si tu plan los permite). Si solo uno acierta, la descripción es frágil: hazla más específica.

## 4. Registra
| Prompt | ¿Debía activarse? | Modelo | ¿Se activó? | ¿Resultado correcto? | Cambio hecho |
|---|---|---|---|---|---|

## 5. Corrige por tipo de fallo
- No se activa → reescribe la `description` (qué hace + cuándo usarla + palabras clave).
- Se activa fuera de alcance → añade la frontera ("para X usa `otra-skill`").
- Se activa pero el resultado es malo → corrige el cuerpo, un script o una referencia.
- Dos skills se disputan → fusiona o separa por criterio observable.

## 6. Vuelve a ejecutar
Tras cada cambio, repite los prompts que fallaron y una muestra de los que pasaban, para detectar regresiones.

No declares garantizada la selección automática: documenta qué probaste y con qué modelos.
