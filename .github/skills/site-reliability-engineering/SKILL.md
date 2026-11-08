---
name: site-reliability-engineering
description: Define SLIs/SLOs y presupuestos de error, y mejora observabilidad, alertas, capacidad, respaldos e incidentes de servicios en producción. Úsala ante caídas, post-mortems, diseño de alertas o metas de fiabilidad; los pipelines van en ingenieria-devops y la infraestructura en ingenieria-cloud.
---

# Site Reliability Engineering

## Flujo
1. **Aclara** usuarios, journeys críticos, impacto de interrupciones, arquitectura y datos operativos disponibles.
2. **SLIs y SLOs:** elige SLIs que representen experiencia o resultados observables y SLOs acordes al riesgo y a las expectativas. Usa presupuestos de error solo si ayudan a equilibrar fiabilidad y velocidad de cambio. No inventes umbrales: derívalos de evidencia, acuerdos o decisiones explícitas de sus responsables.
3. **Evalúa** observabilidad, alertas accionables, capacidad, degradación, dependencias, respaldos y recuperación. Cada alerta debe vincularse a un impacto y a una acción útil. Separa evidencia de hipótesis y asigna acciones con responsable y resultado esperado.
4. **Incidente:**
   - Acota primero inicio, impacto y último cambio.
   - Contrasta hipótesis con señales concretas.
   - Prioriza una mitigación **reversible** dentro del alcance autorizado.
   - Define cómo observar la recuperación y cuándo escalar.
   - Distingue *servicio recuperado* de *causa raíz demostrada*.
   - Aprendizaje sin culpas; preserva hechos y cronología.

Usa la autorización existente antes de cambiar alertas o producción. No declares SLOs acordados sin datos y decisión de sus responsables.

**Perfil de modelo:** E; P durante un incidente grave con causa poco clara.
