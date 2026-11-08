# Contribuir a PeopleDoxx

¡Gracias por tu interés en contribuir! Este documento explica cómo agregar nuevas fuentes de datos, reportar bugs y proponer mejoras.

---

## Agregar un nuevo Scraper

1. Crea `backend/app/scrapers/nombre_fuente.py`
2. Implementa `BaseScraper`:

```python
from app.scrapers.base import BaseScraper
from app.scrapers.registry import ScraperRegistry
from app.models.report import ScraperResult
import httpx, asyncio
from datetime import datetime, timezone

@ScraperRegistry.register
class MiFuenteScraper(BaseScraper):
    SOURCE_ID = "MIFUENTE"
    SOURCE_NAME = "Nombre Completo de la Entidad"
    BASE_URL = "https://portal.entidad.gob.ec/consulta"

    async def fetch(self, cedula: str) -> ScraperResult:
        start = datetime.now(timezone.utc)
        await asyncio.sleep(self._delay)
        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                response = await client.get(self.BASE_URL, params={"cedula": cedula})
                response.raise_for_status()
                # ... parsear respuesta ...
                data = {"campo": "valor"}
            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            return ScraperResult(
                source=self.SOURCE_ID,
                source_name=self.SOURCE_NAME,
                success=True,
                data=data,
                fetched_at=datetime.now(timezone.utc),
                duration_ms=duration,
            )
        except Exception as e:
            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            return ScraperResult(
                source=self.SOURCE_ID,
                source_name=self.SOURCE_NAME,
                success=False,
                data={},
                fetched_at=datetime.now(timezone.utc),
                error=str(e),
                duration_ms=duration,
            )
```

3. Importa en `backend/app/scrapers/__init__.py`:
```python
from app.scrapers import mi_fuente  # noqa: F401
```

4. Agrega tests en `backend/tests/test_mi_fuente.py` usando `respx` para mockear HTTP.

---

## Requisitos éticos para nuevas fuentes

- Permitido: Solo portales públicos sin autenticación (accesibles por cualquier ciudadano)
- Obligatorio: Implementar `asyncio.sleep(self._delay)` antes de cada request (mínimo 1s)
- Obligatorio: Respetar HTTP 429 con backoff exponencial (tenacity)
- Prohibido: No implementar scrapers que requieran credenciales o bypass de autenticación
- Prohibido: No implementar scrapers de fuentes privadas o semiprivadas

---

## Código de conducta

Este proyecto se rige por el [Contributor Covenant](https://www.contributor-covenant.org/).

