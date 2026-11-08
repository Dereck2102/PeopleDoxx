from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone

from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.logger import get_logger
from app.models.report import ScraperResult
from app.scrapers.base import BaseScraper
from app.scrapers.registry import ScraperRegistry

logger = get_logger(__name__)


@ScraperRegistry.register
class SupaScraper(BaseScraper):
    """
    Scraper for SUPA (Sistema Unificado de Pagos del sector público).

    Posts a cédula to the Ministerio de Finanzas payroll lookup page and
    extracts the person's public-sector salary information if available.
    """

    SOURCE_ID = "SUPA"
    SOURCE_NAME = "Sistema Unificado de Pagos (Ministerio de Finanzas)"
    BASE_URL = (
        "http://www.finanzas.gob.ec/wp-content/plugins/"
        "planilla-mensual-de-sueldos/planilla_sueldos.php"
    )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def fetch(self, cedula: str) -> ScraperResult:  # noqa: D102
        start = time.monotonic()
        try:
            await asyncio.sleep(self._delay)
            async with await self._get_client() as client:
                response = await client.post(
                    self.BASE_URL,
                    data={"cedula": cedula, "action": "buscar"},
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Referer": "http://www.finanzas.gob.ec/planilla-de-sueldos/",
                    },
                )
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            data = self._parse(soup, cedula)
            duration_ms = round((time.monotonic() - start) * 1000, 2)

            logger.info("SUPA fetch completed", cedula=cedula, duration_ms=duration_ms)
            return ScraperResult(
                source=self.SOURCE_ID,
                source_name=self.SOURCE_NAME,
                success=True,
                data=data,
                fetched_at=datetime.now(tz=timezone.utc),
                duration_ms=duration_ms,
            )

        except Exception as exc:  # noqa: BLE001
            duration_ms = round((time.monotonic() - start) * 1000, 2)
            logger.warning(
                "SUPA fetch failed",
                cedula=cedula,
                error=str(exc),
                duration_ms=duration_ms,
            )
            return ScraperResult(
                source=self.SOURCE_ID,
                source_name=self.SOURCE_NAME,
                success=False,
                data={},
                fetched_at=datetime.now(tz=timezone.utc),
                error=f"{type(exc).__name__}: {exc}",
                duration_ms=duration_ms,
            )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _parse(self, soup: BeautifulSoup, cedula: str) -> dict:
        data: dict = {
            "cedula_consultada": cedula,
            "found": False,
            "registros": [],
        }

        # Look for a table with payroll data
        table = soup.find("table")
        if table is None:
            # Check for "not found" message in the page text
            text = soup.get_text(separator=" ", strip=True).lower()
            if any(
                phrase in text
                for phrase in ["no se encontr", "no existe", "no hay datos"]
            ):
                data["message"] = (
                    "No se encontró información en el sistema de sueldos públicos."
                )
            return data

        rows = table.find_all("tr")
        if len(rows) < 2:
            data["message"] = "Tabla vacía en la respuesta del servidor."
            return data

        # First row is the header
        headers = [th.get_text(strip=True).lower() for th in rows[0].find_all(["th", "td"])]
        records: list[dict] = []

        for row in rows[1:]:
            cells = row.find_all("td")
            if not cells:
                continue
            record: dict = {}
            for idx, cell in enumerate(cells):
                key = headers[idx] if idx < len(headers) else f"col_{idx}"
                record[key] = cell.get_text(strip=True)

            # Normalise to canonical field names
            records.append(
                {
                    "nombre": _extract(record, ["nombre", "nombres"]),
                    "cargo": _extract(record, ["cargo", "denominación", "denominacion"]),
                    "institucion": _extract(
                        record, ["institución", "institucion", "entidad"]
                    ),
                    "remuneracion_mensual": _extract(
                        record, ["remuneración", "remuneracion", "sueldo", "salario"]
                    ),
                    "anio": _extract(record, ["año", "anio", "año"]),
                    "mes": _extract(record, ["mes"]),
                }
            )

        data["found"] = len(records) > 0
        data["registros"] = records
        return data


def _extract(record: dict, keys: list[str]) -> str | None:
    for key in keys:
        for k, v in record.items():
            if key in k:
                return v or None
    return None
