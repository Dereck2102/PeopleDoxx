---
name: enrutamiento-de-modelos
description: Recomienda qué modelo de Copilot usar (Auto, GPT-6 Luna, Claude Haiku 4.5, Kimi K3, MAI-Code-1.1-Flash) y cuándo pinearlo en un agente, según tarea, créditos de IA disponibles y plan Student. Úsala al iniciar una tarea grande, al dudar qué modelo elegir, o si los créditos se agotan rápido.
---

# Enrutamiento de modelos (GitHub Copilot, plan Student)

## Lo que puedes y no puedes hacer
- **No cambias el modelo del chat principal.** Lo elige la persona en el selector de modelos del chat. Tu trabajo es decir cuándo conviene cambiarlo y por qué, en una línea, y seguir trabajando.
- El modelo elegido persiste durante la conversación.
- **Sí puedes** fijar el modelo de un **agente personalizado** (`.github/agents/*.agent.md`, campo `model`) o de un subagente invocado con `runSubagent`, pero solo con un nombre que exista de verdad en el selector de esta cuenta — nunca inventado.
- El plan Student está restringido a un subconjunto de modelos (ver tabla). Pedir un modelo fuera de ese conjunto en un agente personalizado puede fallar: por eso, si no estás seguro, deja `model` sin establecer (hereda el modelo de la conversación) en vez de fijar uno.

## Modelos disponibles en el plan Student (confirma en tu propio selector)
Los documentos oficiales de GitHub describen el plan Student como "solo selección automática", pero el selector puede mostrar manualmente un subconjunto ligero además de Auto; esto ha cambiado varias veces en 2026, así que **tu selector manda sobre esta tabla**.

| Modelo | Categoría GitHub | Mejor para | Precio por 1M tokens (entrada/salida) |
|---|---|---|---|
| **Auto** | — | la opción por defecto; aplica 10% de descuento y Copilot elige el modelo según la tarea | variable (según lo que Auto elija) |
| **GPT-6 Luna** | Ligero | ayuda rápida en tareas simples o repetitivas, boilerplate, explicaciones cortas | $0.10 / $0.50 |
| **GPT-5.6 Luna** | Ligero | igual que GPT-6 Luna; algo más caro, prefiere GPT-6 Luna si ambos están disponibles | $0.20 / $1.20 |
| **MAI-Code-1.1-Flash** | Ligero (con visión) | completado y explicación rápidos, sigue instrucciones, entiende imágenes/capturas | $0.20 / $1.20 |
| **Claude Haiku 4.5** | Versátil | respuestas rápidas y fiables a preguntas de código cotidianas; mejor calidad que los modelos "ligero" a cambio de más costo | $1.00 / $5.00 |
| **Kimi K3** | Potente | codificación agéntica y contexto largo (hasta ~1M tokens); tareas multi-paso en bases de código grandes | $3.00 / $15.00 |

## Perfiles
| Perfil | Modelo sugerido | Úsalo para |
|---|---|---|
| **L** ligero | GPT-6 Luna | explorar y leer mucho, documentar, boilerplate, ediciones triviales, extraer datos |
| **E** estándar | Claude Haiku 4.5 (o MAI-Code-1.1-Flash si hay imágenes de por medio) | implementar, depurar, revisar y explicar código en el día a día |
| **P** profundo | Kimi K3 | tareas agénticas multi-archivo, contexto muy largo, arquitectura, auditoría de seguridad, migraciones de riesgo |

## Procedimiento
1. **Clasifica** la tarea con la tabla y con el *Perfil de modelo* de la skill que aplica.
2. **Por defecto, prefiere Auto.** Da un 10% de descuento sobre el costo del modelo que elija y, en la mayoría de tareas cotidianas, acierta razonablemente. Pinea un modelo a mano solo cuando: (a) quieras forzar el más barato para algo trivial y así estirar el crédito, o (b) necesites deliberadamente la capacidad de Kimi K3 para una tarea agéntica grande y no confíes en que Auto lo elija.
3. **Compara** con el modelo activo. Si desentona, sugiere el cambio con una razón concreta ("esto va a tocar varios archivos de forma agéntica: conviene Kimi K3, o déjalo en Auto"). Si encaja, no digas nada.
4. **Revisión cruzada:** para cambios riesgosos, pide una segunda revisión con un modelo de **otro proveedor** del que implementó (por ejemplo, si implementaste con un modelo OpenAI, revisa con Claude Haiku 4.5, o viceversa). Proveedores distintos fallan de forma distinta.
5. **Créditos de IA:** el plan Student incluye una asignación mensual pequeña de créditos (GitHub no publica la cifra exacta hoy; el propio aviso de GitHub de junio de 2026 habló de 200 créditos/mes, y la cifra puede haber cambiado desde entonces — revisa tu panel de uso en github.com/settings/billing). 1 crédito = $0.01 USD. Dado lo ajustado del presupuesto en Student, evita Kimi K3 para tareas que un modelo ligero resuelve igual de bien, y vigila tu consumo con el panel de uso en vez de adivinarlo.

## Honestidad sobre estas recomendaciones
Los perfiles se basan en las categorías y descripciones que GitHub publica de cada modelo (Lightweight / Versatile / Powerful) y en el precio por token, no en benchmarks propios. Ajústalos con tu experiencia. La disponibilidad y el precio cambian con frecuencia: confirma en `references/modelos.md`, en tu selector y en la documentación oficial antes de recomendar un modelo que quizá ya no exista o haya cambiado de precio.

**Perfil de modelo:** L.
