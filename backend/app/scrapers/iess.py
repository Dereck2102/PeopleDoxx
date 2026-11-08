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
class IessScraper(BaseScraper):
    """
    Scraper for IESS (Instituto Ecuatoriano de Seguridad Social).

    Queries the public affiliate lookup and extracts affiliation status,
    current employer, and insurance type.
    """

    SOURCE_ID = "IESS"
    SOURCE_NAME = "Instituto Ecuatoriano de Seguridad Social"
    BASE_URL = "https://www.iess.gob.ec/empleado.php"

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
                response = await client.get(
                    self.BASE_URL,
                    params={"ci": cedula},
                    headers={"Referer": "https://www.iess.gob.ec/"},
                )
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            data = self._parse(soup, cedula)
            duration_ms = round((time.monotonic() - start) * 1000, 2)

            logger.info("IESS fetch completed", cedula=cedula, duration_ms=duration_ms)
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
                "IESS fetch failed",
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
            "nombre_completo": None,
            "empleador_actual": None,
            "fecha_afiliacion": None,
            "estado_afiliacion": None,
            "tipo_seguro": None,
        }

        page_text = soup.get_text(separator=" ", strip=True).lower()

        # Detect explicit "not found" responses
        not_found_phrases = [
            "no se encontr",
            "no existe",
            "no está afiliado",
            "no esta afiliado",
            "cédula no válida",
            "cedula no valida",
        ]
        if any(phrase in page_text for phrase in not_found_phrases):
            data["message"] = (
                "La persona no está afiliada al IESS o no se encontró información."
            )
            return data

        # Build a label→value map from table cells
        label_map: dict[str, str] = {}
        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) == 2:
                    label_map[cells[0].get_text(strip=True).lower()] = (
                        cells[1].get_text(strip=True)
                    )

        def _get(keys: list[str]) -> str | None:
            for key in keys:
                for lbl, val in label_map.items():
                    if key in lbl:
                        return val or None
            return None

        data["nombre_completo"] = _get(["nombre", "afiliado"])
        data["empleador_actual"] = _get(["empleador", "empresa", "patrono"])
        data["fecha_afiliacion"] = _get(["fecha", "afiliación", "afiliacion", "inicio"])
        data["estado_afiliacion"] = _get(["estado"])
        data["tipo_seguro"] = _get(["tipo", "seguro"])

        data["found"] = any(
            [
                data["nombre_completo"],
                data["empleador_actual"],
                data["estado_afiliacion"],
            ]
        )
        return data
