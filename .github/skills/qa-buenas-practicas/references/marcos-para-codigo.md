# Marcos de referencia para calidad y seguridad de código

Léelo solo cuando debas **elegir un estándar** o justificar controles. Usa únicamente los criterios aplicables al cambio, y confirma el nombre y la versión vigentes en la fuente oficial antes de citarlos: aquí no se fijan versiones a propósito.

| Necesidad | Marco habitual | Úsalo como |
|---|---|---|
| Riesgos web más comunes | OWASP Top 10 | lista de concienciación, no checklist exhaustivo |
| Requisitos verificables de seguridad de aplicaciones | OWASP ASVS | catálogo de requisitos por nivel |
| APIs | OWASP API Security Top 10 | checklist de riesgos de API |
| Tipos de debilidad en código | CWE | vocabulario común para clasificar hallazgos |
| Desarrollo seguro de software | NIST SSDF | prácticas de ciclo de vida |
| Cadena de suministro | SLSA | niveles de integridad de build y artefactos |
| Accesibilidad | WCAG | criterios con nivel A/AA/AAA; indica versión y nivel evaluados |
| Atributos de calidad del producto | ISO/IEC 25010 | modelo para nombrar atributos (mantenibilidad, fiabilidad…) |

Reglas de uso:
- Un marco es checklist de apoyo, no garantía ni certificación.
- No declares cumplimiento por haber aplicado un control aislado.
- Un cambio rutinario no se detiene por no haber definido una norma.
- Si necesitas evaluar un marco formal completo, usa `cumplimiento-iso-itil-cobit-nist`.
