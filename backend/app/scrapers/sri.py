from __future__ import annotations

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
class SriScraper(BaseScraper):
    """
    Scraper for SRI (Servicio de Rentas Internas).

    Queries the public RUC/cédula lookup at srienlinea.sri.gob.ec and
    extracts contributor details from the HTML response.
    """

    SOURCE_ID = "SRI"
    SOURCE_NAME = "Servicio de Rentas Internas"
    BASE_URL = "https://srienlinea.sri.gob.ec/sri-en-linea/SriRucWeb/ConsultaRuc/Consultas/consultaRuc"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def fetch(self, cedula: str) -> ScraperResult:  # noqa: D102
        start = time.monotonic()
        try:
            async with await self._get_client() as client:
                import asyncio
                await asyncio.sleep(self._delay)
                response = await client.get(
                    self.BASE_URL,
                    params={"numero": cedula},
                )
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            data = self._parse(soup, cedula)
            duration_ms = round((time.monotonic() - start) * 1000, 2)

            logger.info("SRI fetch completed", cedula=cedula, duration_ms=duration_ms)
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
                "SRI fetch failed",
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
        """
        Extract relevant fields from the SRI HTML response.

        The public SRI page renders a table with rows like:
          <td class="...">Nombre / Razón Social</td>
          <td class="...">JUAN PEREZ</td>

        We build a label→value map from all adjacent cell pairs and then
        pick the fields we care about.
        """
        data: dict = {
            "cedula_consultada": cedula,
            "nombre_razon_social": None,
            "numero_ruc": None,
            "estado_contribuyente": None,
            "tipo_contribuyente": None,
            "actividad_economica": None,
            "obligaciones": [],
        }

        # Try to find the main data table
        tables = soup.find_all("table")
        label_value_map: dict[str, str] = {}

        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                # Rows with two cells: label | value
                if len(cells) == 2:
                    label = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    label_value_map[label] = value

        def _get(keys: list[str]) -> str | None:
            for key in keys:
                for lbl, val in label_value_map.items():
                    if key in lbl:
                        return val or None
            return None

        data["nombre_razon_social"] = _get(
            ["nombre", "razón social", "razon social"]
        )
        data["numero_ruc"] = _get(["ruc", "número ruc", "numero ruc"])
        data["estado_contribuyente"] = _get(["estado"])
        data["tipo_contribuyente"] = _get(["tipo"])
        data["actividad_economica"] = _get(["actividad"])

        # Obligations may appear as a list inside a nested table or multi-row block
        obligations: list[str] = []
        for lbl, val in label_value_map.items():
            if "obligacion" in lbl and val:
                obligations.append(val)
        data["obligaciones"] = obligations

        # If nothing was found, mark as not found
        if not any(
            [
                data["nombre_razon_social"],
                data["numero_ruc"],
                data["estado_contribuyente"],
            ]
        ):
            data["found"] = False
            data["message"] = (
                "No se encontró información para esta cédula en el SRI."
            )
        else:
            data["found"] = True

        return data
