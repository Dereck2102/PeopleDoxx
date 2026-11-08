# Catálogo de modelos y precios de GitHub Copilot (verificado 2026-11-08)

Fuentes primarias: https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing · https://docs.github.com/en/copilot/reference/ai-models/model-comparison · https://docs.github.com/en/copilot/get-started/plans
Esta información cambia con frecuencia (GitHub ha retirado y añadido modelos varias veces en 2026). Si la fecha de arriba tiene semanas, vuelve a comprobarla antes de citar un precio o una disponibilidad.

## Facturación
Desde el 1 de junio de 2026, Copilot factura por **créditos de IA de GitHub** (1 crédito = $0.01 USD) según tokens de entrada, salida y caché, en vez de "premium requests" por solicitud. Los completados de código (inline) siguen sin medirse y son ilimitados en planes de pago.

## Plan Copilot Student
- Gratis para estudiantes verificados. Completados de código ilimitados.
- Asignación mensual de créditos de IA: GitHub no publica hoy una cifra exacta en su documentación ("An allowance of GitHub AI Credits"). Su propio anuncio de junio de 2026 fijó 200 créditos/mes; fuentes de terceros más recientes citan cifras distintas y no siempre fiables. **Confirma la cifra vigente en tu panel de uso**, no la des por supuesta.
- Modelos: la documentación oficial dice "solo selección automática (Auto)". En la práctica, el selector de esta cuenta puede mostrar también un subconjunto manual (observado: Auto, Claude Haiku 4.5, GPT-5.6 Luna, GPT-6 Luna, Kimi K3, MAI-Code-1.1-Flash) — esto ha cambiado más de una vez durante 2026, así que trata el selector como la fuente de verdad, por encima de este documento.
- Excluye agentes de terceros y Copilot code review con algunos modelos restringidos a planes de pago.

## Precios por 1M de tokens (de la tabla oficial de GitHub)
| Modelo | Proveedor | Categoría | Entrada | Caché | Salida |
|---|---|---|---|---|---|
| GPT-6 Luna | OpenAI | Ligero | $0.10 | $0.01 | $0.50 |
| GPT-5.6 Luna | OpenAI | Ligero | $0.20 | $0.02 | $1.20 |
| MAI-Code-1.1-Flash | Microsoft | Ligero | $0.20 | $0.02 | $1.20 |
| Claude Haiku 4.5 | Anthropic | Versátil | $1.00 | $0.10 | $5.00 |
| Kimi K3 | Moonshot AI | Potente | $3.00 | $0.30 | $15.00 |
| Claude Haiku 5.5 | Anthropic | Ligero | $0.10–$0.50* | $0.01–$0.05* | $0.50–$2.50* |
| Gemini 3.8 Flash | Google | Versátil | $0.75 | $0.075 | $3.75 |
| Gemini 4 Argon | Google | Potente | $2.00 | $0.10 | $10.00 |

\* Claude Haiku 5.5 tiene precio según umbral de contexto (≤100K / >100K tokens).

Estos dos últimos (Gemini) y Claude Haiku 5.5 aparecen en la tabla de precios general de Copilot pero no están confirmados como disponibles en el plan Student a la fecha de verificación; no los recomiendes para Student sin comprobarlo en el selector.

## Auto model selection: niveles
Desde septiembre de 2026, Auto admite tres niveles de preferencia costo/calidad, disponibles en VS Code, Copilot CLI y la app de Copilot:
| Nivel | Prioridad | Uso típico |
|---|---|---|
| Efficiency | Costo | tareas rápidas y simples |
| Balance | Costo, calidad y latencia | trabajo cotidiano |
| Intelligence | Calidad | tareas complejas |

Los tres niveles eligen del mismo conjunto de modelos habilitados; Intelligence no garantiza el modelo más caro si la tarea es trivial. En planes de pago, usar Auto (cualquier nivel) da un 10% de descuento sobre el costo del modelo elegido.

## Retiros recientes y próximos (verifica antes de recomendar)
GitHub retira modelos con relativa frecuencia. A la fecha de verificación, GPT-5.4 mini, GPT-5 mini, Kimi K2.7 Code y MAI-Code-1-Flash ya se retiraron en 2026, y había retiros anunciados para mediados de noviembre de 2026 (Claude Opus 4.8, Claude Opus 5, GPT-5.6 Terra). No asumas que un modelo sigue disponible solo porque aparece en este documento: compruébalo en el selector o en la documentación oficial.
