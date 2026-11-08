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
class CneScraper(BaseScraper):
    """
    Scraper for CNE (Consejo Nacional Electoral).

    Retrieves the electoral roll data for a cédula: registered voting
    location, province, canton, parroquia, recinto, zona and junta.
    """

    SOURCE_ID = "CNE"
    SOURCE_NAME = "Consejo Nacional Electoral"
    BASE_URL = "https://app5.cne.gob.ec/src/lotaip/consultaCiudadano.php"

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
                    params={"cedula": cedula},
                    headers={"Referer": "https://app5.cne.gob.ec/"},
                )
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            data = self._parse(soup, cedula)
            duration_ms = round((time.monotonic() - start) * 1000, 2)

            logger.info("CNE fetch completed", cedula=cedula, duration_ms=duration_ms)
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
                "CNE fetch failed",
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
            "nombre": None,
            "provincia": None,
            "canton": None,
            "parroquia": None,
            "recinto": None,
            "zona": None,
            "junta": None,
            "digito": None,
        }

        page_text = soup.get_text(separator=" ", strip=True).lower()
        not_found_phrases = [
            "no se encontr",
            "no existe",
            "cédula incorrecta",
            "cedula incorrecta",
            "no válida",
            "no valida",
        ]
        if any(phrase in page_text for phrase in not_found_phrases):
            data["message"] = (
                "No se encontró información electoral para esta cédula."
            )
            return data

        # Build label → value map from every two-column table row
        label_map: dict[str, str] = {}
        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) == 2:
                    label_map[cells[0].get_text(strip=True).lower()] = (
                        cells[1].get_text(strip=True)
                    )

        # Also try definition lists (<dt>/<dd>) sometimes used in the portal
        for dl in soup.find_all("dl"):
            dts = dl.find_all("dt")
            dds = dl.find_all("dd")
            for dt, dd in zip(dts, dds):
                label_map[dt.get_text(strip=True).lower()] = dd.get_text(strip=True)

        def _get(keys: list[str]) -> str | None:
            for key in keys:
                for lbl, val in label_map.items():
                    if key in lbl:
                        return val or None
            return None

        data["nombre"] = _get(["nombre", "apellidos", "ciudadano"])
        data["provincia"] = _get(["provincia"])
        data["canton"] = _get(["cantón", "canton"])
        data["parroquia"] = _get(["parroquia"])
        data["recinto"] = _get(["recinto"])
        data["zona"] = _get(["zona"])
        data["junta"] = _get(["junta"])
        data["digito"] = _get(["dígito", "digito"])

        data["found"] = any(
            [data["nombre"], data["provincia"], data["canton"]]
        )
        return data
