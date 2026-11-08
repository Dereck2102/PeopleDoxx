---
name: arquitectura-de-software
description: Diseña o revisa arquitectura, límites de componentes, contratos, integraciones y decisiones (ADR) cuando un cambio afecta cómo se parte o evoluciona un sistema. Úsala ante dudas de diseño, trade-offs entre alternativas o planes de transición.
---

# Arquitectura de software

## Cuándo no usarla
Una corrección local no necesita rediseño: basta `qa-buenas-practicas`. Amenazas → `ciberseguridad-defensiva`. Interfaces → `ux-principios-diseno`. Detalle de nube, datos, base de datos u operación → su skill de ingeniería.

## Flujo
1. **Aclara** problema, usuarios, límites del sistema, restricciones y atributos de calidad prioritarios. Inspecciona solo los documentos y componentes pertinentes.
2. **Separa hechos de supuestos** y márcalos, porque una decisión construida sobre un supuesto no verificado es la primera que se rompe.
3. **Compara alternativas** solo si hay una decisión real. Evalúa consecuencias en complejidad, seguridad, disponibilidad, rendimiento, costo, operabilidad y evolución. No añadas patrones ni infraestructura sin necesidad demostrada.
4. **Si el cambio toca código**, aplica SOLID como heurística: responsabilidades cohesionadas, extensión sin modificar lo estable, sustitución segura, interfaces enfocadas, inversión de dependencias donde reduzca acoplamiento. Pondera también complejidad, duplicación, testabilidad y costo de mantenimiento. No fuerces abstracciones.
5. **Comprueba contratos** y responsabilidades en los puntos de integración afectados.
6. No impongas proveedor, lenguaje ni patrón sin requisitos que lo justifiquen.

## Entregable
Al nivel que ayude a decidir: límites y responsabilidades, flujos de datos e integraciones, riesgos, decisiones pendientes y plan de transición. Usa Mermaid si aclara.

Para una decisión relevante, registra un ADR breve vinculado a archivos o interfaces reales:

```
# ADR-NNN: <título>
Contexto: …
Decisión: …
Alternativas descartadas: …
Consecuencias: …
Se revisa si: <condición observable>
Afecta a: <archivos / interfaces>
```

**Perfil de modelo:** P para diseño multi-componente; E para ajustar o documentar un diseño ya decidido.
