---
name: ingenieria-cloud
description: Diseña recursos de nube - cómputo, red, identidad, almacenamiento, resiliencia, costo e infraestructura como código. Úsala al diseñar o revisar infraestructura cloud; hardening en ciberseguridad-defensiva, CI/CD en ingenieria-devops, fiabilidad en site-reliability-engineering.
---

# Ingeniería en la nube

## Flujo
1. **Recupera** proveedor, entorno y región de la infraestructura y configuración existentes *antes* de preguntar. Aclara restricciones, presupuesto, carga, disponibilidad y requisitos de datos que afecten la decisión. Si el proveedor sigue indefinido, presenta criterios u opciones.
2. **Diseña** cómputo, red, identidad, almacenamiento y servicios gestionados con límites de confianza y permisos mínimos. Considera escalado, observabilidad, respaldo, recuperación, resiliencia, costo y dependencia del proveedor según el riesgo.
3. **Documentación oficial vigente** para nombres, límites y comportamiento de servicios.
4. **Infraestructura como código:** revisa el plan o diff disponible, los recursos reemplazados, la exposición de red, los permisos y la recuperación.
5. **Autorización:** poder diseñar no implica poder aplicar. Si el usuario ya autorizó el despliegue en ese entorno, conserva ese alcance sin pedirlo de nuevo.

**Perfil de modelo:** E; P para diseño de red e identidad multi-cuenta o migraciones entre proveedores.
