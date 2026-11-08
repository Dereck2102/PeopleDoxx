# PeopleDoxx

> **Plataforma de código abierto para consulta de información pública gubernamental ecuatoriana**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)](https://docker.com)

PeopleDoxx agrega información **públicamente disponible** desde portales del Estado ecuatoriano usando un número de cédula. Consulta múltiples fuentes en paralelo y genera reportes consolidados en PDF o JSON.

> **Aviso legal:** Esta herramienta consulta únicamente portales gubernamentales con acceso público sin autenticación. Su uso debe ser conforme a la [Ley Orgánica de Protección de Datos Personales (LOPDP)](https://www.registroficial.gob.ec/) del Ecuador. Destinada exclusivamente a investigadores privados licenciados, uso académico y verificación legal autorizada.

---

## Fuentes consultadas

| Fuente | Entidad | Datos |
|---|---|---|
| **SRI** | Servicio de Rentas Internas | Nombre, RUC, estado tributario, actividad económica |
| **SATJE** | Función Judicial | Causas judiciales (actor / demandado) |
| **SUPA** | Ministerio de Finanzas | Nómina pública, cargo, institución |
| **IESS** | Seguridad Social | Afiliación, empleador, historial |
| **CNE** | Consejo Nacional Electoral | Padrón electoral, recinto de votación |
| **MDT** | Ministerio del Trabajo | Avisos de entrada/salida laboral |

---

## Arquitectura

```
PeopleDoxx/
├── backend/          # FastAPI + Scraper Engine + Auth + Admin API (Python 3.12)
├── frontend/         # Next.js 14 (TypeScript + Tailwind) — usuario final
├── admin-panel/      # React + Vite (TypeScript + Tailwind) — panel maestro (puerto 4000)
├── cli/              # CLI (Python Click)
├── nginx/            # Reverse proxy config
├── docs/             # ADRs y guías
├── docker-compose.yml
└── docker-compose.dev.yml
```

**Sistema de usuarios y permisos:**
- Autenticación dual: JWT (web/app) + API Key (CLI/integraciones)
- Términos de servicio obligatorios en primer login
- Cuotas por usuario: diaria + mensual (configurables por admin)
- Permisos granulares: fuentes habilitadas (SRI, SATJE…), descarga PDF/JSON
- Expiración de cuenta
- Historial de búsquedas completo por usuario (auditoría)

**Principios SOLID aplicados:**
- **SRP:** Cada scraper gestiona una sola fuente; cada módulo una responsabilidad
- **OCP:** Nuevas fuentes sin modificar el orquestador (Registry Pattern)
- **LSP:** Todos los scrapers son intercambiables vía `BaseScraper`
- **ISP:** Interfaz mínima `async fetch(cedula) → ScraperResult`
- **DIP:** Orquestador depende de abstracciones, no de clases concretas

---

## Inicio rápido

### Requisitos
- Docker & Docker Compose
- (Opcional) Python 3.12+ para CLI local

### 1. Clonar y configurar

```bash
git clone https://github.com/tu-usuario/PeopleDoxx.git
cd PeopleDoxx
cp .env.example .env
# IMPORTANTE: edita .env y cambia JWT_SECRET_KEY, ADMIN_PASSWORD y API_KEY
```

### 2. Levantar con Docker Compose

```bash
docker compose up -d
```

### 3. Accesos
| Servicio | URL |
|---|---|
| **App usuario final** | http://localhost |
| **Panel de administración** | http://localhost:4000 |
| **API + Docs OpenAPI** | http://localhost:8000/docs |

**Credenciales de admin por defecto** (cambiar en `.env` antes de producción):
- Email: `admin@peopledoxx.local`
- Contraseña: `ChangeMe!2024`

### 4. Flujo de un nuevo usuario
1. Admin crea el usuario desde el Panel Maestro (puerto 4000)
2. Usuario hace login en la web → acepta términos de servicio
3. Usuario busca por cédula (dentro de su cuota y fuentes permitidas)
4. Admin monitorea uso, ajusta cuotas y permisos en tiempo real

### 4. Usar el CLI

```bash
# Buscar por cédula (formato tabla)
docker compose run --rm cli search --cedula 1713175071

# Generar reporte PDF
docker compose run --rm cli search --cedula 1713175071 --format pdf --output ./reporte.pdf

# Verificar fuentes disponibles
docker compose run --rm cli sources

# Health check
docker compose run --rm cli health
```

### 5. API REST (OpenAPI)

Documentación interactiva disponible en: [http://localhost:8000/docs](http://localhost:8000/docs)

```bash
# Buscar por cédula
curl -X POST http://localhost:8000/api/v1/search \
  -H "X-API-Key: tu-api-key" \
  -H "Content-Type: application/json" \
  -d '{"cedula": "1713175071"}'

# Descargar reporte PDF
curl -H "X-API-Key: tu-api-key" \
  http://localhost:8000/api/v1/reports/1713175071/pdf \
  --output reporte.pdf
```

---

## Contribuir

Consulta [docs/CONTRIBUTING.md](./docs/CONTRIBUTING.md) para agregar nuevas fuentes gubernamentales.

**Requisito fundamental:** Solo se aceptan scrapers de portales **públicos** (accesibles sin autenticación por cualquier ciudadano).

---

## Créditos

Proyecto de portafolio académico — Tecnología Superior en Ciberseguridad.

---

## Licencia

[MIT](./LICENSE) — Uso libre con responsabilidad ética y legal.

