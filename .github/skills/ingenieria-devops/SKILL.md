---
name: ingenieria-devops
description: Construye y revisa pipelines CI/CD, builds, releases, artefactos y despliegues reproducibles con rollback. Úsala para GitHub Actions, GitLab CI, Jenkins y similares; los procesos de negocio van en automatizacion-de-procesos y la fiabilidad en site-reliability-engineering.
---

# Ingeniería DevOps

Cubre el ciclo de construcción, integración, release y despliegue de software. Diseño de recursos de nube → `ingenieria-cloud`.

## Flujo
1. **Aclara** repositorios, entornos, herramientas, flujo de cambios, requisitos de release y restricciones. Revisa los pipelines y convenciones existentes antes de sustituirlos.
2. **Diseña** build, integración, despliegue y rollback reproducibles: dependencias y artefactos, secretos, permisos mínimos, controles de calidad, cachés, promoción entre entornos y trazabilidad. Automatización idempotente y segura ante fallos parciales.
3. **Revisa** permisos de contribuciones externas, exposición de secretos y que el artefacto desplegado sea el que superó los controles.
4. **Valida** el archivo del pipeline y los comandos afectados con las herramientas existentes cuando sea viable. Distingue *validación local*, *ejecución del pipeline* y *despliegue verificado*, y conserva enlaces o resultados que lo acrediten.
5. Usa documentación oficial vigente para herramientas y servicios concretos.

## Autorización
Ejecuta la preparación y los cambios ya autorizados. Un encargo de CI/CD no concede por sí solo un despliegue productivo: usa la autorización existente para ese entorno y pide solo la que falte. Explica recuperación y riesgos materiales.

**Perfil de modelo:** E.
