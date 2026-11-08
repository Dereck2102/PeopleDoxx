---
name: automatizacion-de-procesos
description: Automatiza flujos operativos o de negocio (disparadores, reglas, integraciones, reintentos, idempotencia, supervisión humana). Úsala al convertir un proceso manual en automático; los pipelines de build y despliegue van en ingenieria-devops.
---

# Automatización de procesos

No automatices un flujo defectuoso sin señalarlo: acelerarlo solo multiplica el defecto. Para CI/CD usa `ingenieria-devops`; para mapear o rediseñar el proceso antes de automatizarlo, `gestion-de-procesos`.

## Flujo
1. **Define** disparador, entradas, reglas, salidas, sistemas, volumen, responsables y excepciones. Estima beneficios y costos solo con supuestos explícitos.
2. **Descubre qué herramientas o conectores existen** antes de comprometer una ejecución. Reutiliza automatizaciones existentes. Distingue *preparar* el flujo de *activarlo*; si falta una herramienta, entrega lo implementable y nombra la dependencia concreta.
3. **Diseña para fallar bien:** errores, reintentos, duplicados, idempotencia, observabilidad, trazabilidad, permisos mínimos, privacidad, reversión y supervisión humana.
   - Operaciones repetibles: usa una identidad estable para reconocer duplicados.
   - Reintenta solo fallos transitorios y con límite; separa datos inválidos (rechazar), fallos recuperables (reintentar) y casos que requieren una persona.
   - Si una escritura termina con resultado desconocido, consulta su estado antes de repetirla.
   - Documenta límites, dependencias y el modo manual de recuperación.
4. **Autorización:** usa la ya expresada y no la repitas para lo cubierto. Ante una acción externa material que la exceda, prepara el resultado revisable y pide solo lo que falta.
5. **Comprueba** el camino principal y los fallos relevantes con datos de prueba o modo simulación. Escribir el código o la configuración no es un flujo operativo: registra qué ejecutaste, qué observaste y qué falta para activarlo.

## Entregable
Diagrama, lógica, campos o pasos según lo pedido; proporcional al riesgo. Distingue siempre *diseño propuesto* de *automatización implementada y operativa*. Nunca expongas secretos en código, logs ni documentación.

**Perfil de modelo:** E.
