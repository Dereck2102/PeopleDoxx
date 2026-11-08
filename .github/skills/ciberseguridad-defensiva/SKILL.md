---
name: ciberseguridad-defensiva
description: Revisa y corrige la seguridad de código y diseños sin pentest activo - autorización, inyecciones, secretos, dependencias, modelado de amenazas, hardening e incidentes. Úsala al escribir, revisar o arreglar código con implicaciones de seguridad.
---

# Ciberseguridad defensiva

Cubre implementación segura, revisión estática, modelado de amenazas, hardening y respuesta a incidentes. Una revisión de código autorizada puede empezar con los archivos disponibles. Aclara objetivos y efectos permitidos antes de pruebas activas cuyo alcance no esté definido. Un cambio ordinario o una revisión estática **no** requieren lanzar un scan.

## Flujo
1. **Sigue el dato** desde la entrada no confiable hasta el uso sensible (consulta, renderizado, archivo, proceso, petición de red, cambio de estado). Valida, parametriza y codifica en el punto correcto; un filtro genérico no lo sustituye.
2. **Autorización por operación, objeto y tenant**, incluidos los campos que se devuelven y se pueden modificar. Un ID conocido, una interfaz oculta o un rol comprobado solo en el navegador no prueban autorización en el servidor.
3. **Secretos, permisos, dependencias y logs:** revisa solo los componentes afectados. Mitiga según impacto y uso real, no según el nombre de un patrón.
4. **Al corregir**, elimina la causa, considera rutas equivalentes y prueba casos permitidos y denegados con datos de prueba. Distingue evidencia estática, reproducción local y verificación en el entorno afectado.
5. **Incidentes:** preserva evidencias y cronología; prioriza contención y recuperación según impacto; actúa dentro de la autorización existente y pide solo la que falte.

## Entregable por hallazgo
```
Ubicación: archivo:línea
Condición de explotación: …
Impacto: …
Evidencia: [estática | reproducción local | verificado en entorno]
Mitigación: …
Estado: [sospecha | confirmado | corregido | verificado]
```
Una sospecha o la salida de un escáner no es explotación confirmada hasta revisar la evidencia.

## Cuándo derivar
Vulnerabilidades, versiones o controles vigentes → fuentes primarias. Pentest o validación activa solicitados y delimitados → skills del paquete opcional Strix. Evaluar un marco formal → `cumplimiento-iso-itil-cobit-nist` (una mejora técnica no acredita conformidad).

**Perfil de modelo:** P para auditar autorización o revisar cambios sensibles; E para correcciones ordinarias.
