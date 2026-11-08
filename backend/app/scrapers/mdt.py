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
class MdtScraper(BaseScraper):
    """
    Scraper for MDT (Ministerio del Trabajo) – Avisos de entrada/salida.

    Retrieves the history of employment notifications (avisos de entrada
    y salida) registered with the Ministry of Labour for a given cédula.
    """

    SOURCE_ID = "MDT"
    SOURCE_NAME = "Ministerio del Trabajo (Avisos de Entrada/Salida)"
    BASE_URL = (
        "https://sistemasweb.trabajo.gob.ec/siut/informacion_consulta/index.php"
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
                response = await client.get(
                    self.BASE_URL,
                    params={"cedula": cedula, "tipo": "aviso"},
                    headers={
                        "Referer": "https://sistemasweb.trabajo.gob.ec/",
                    },
                )
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            data = self._parse(soup, cedula)
            duration_ms = round((time.monotonic() - start) * 1000, 2)

            logger.info("MDT fetch completed", cedula=cedula, duration_ms=duration_ms)
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
                "MDT fetch failed",
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
            "total_avisos": 0,
            "avisos": [],
        }

        page_text = soup.get_text(separator=" ", strip=True).lower()
        not_found_phrases = [
            "no se encontr",
            "no existe",
            "no hay registros",
            "sin resultados",
        ]
        if any(phrase in page_text for phrase in not_found_phrases):
            data["message"] = (
                "No se encontraron avisos de entrada/salida para esta cédula."
            )
            return data

        table = soup.find("table")
        if table is None:
            return data

        rows = table.find_all("tr")
        if len(rows) < 2:
            return data

        headers = [
            th.get_text(strip=True).lower()
            for th in rows[0].find_all(["th", "td"])
        ]

        avisos: list[dict] = []
        for row in rows[1:]:
            cells = row.find_all("td")
            if not cells:
                continue
            raw: dict = {}
            for idx, cell in enumerate(cells):
                key = headers[idx] if idx < len(headers) else f"col_{idx}"
                raw[key] = cell.get_text(strip=True)

            avisos.append(
                {
                    "empleador": _extract(raw, ["empleador", "empresa", "razón", "razon"]),
                    "fecha_entrada": _extract(raw, ["entrada", "ingreso", "inicio"]),
                    "fecha_salida": _extract(raw, ["salida", "fin", "término", "termino"]),
                    "cargo": _extract(raw, ["cargo", "puesto", "función", "funcion"]),
                    "sector": _extract(raw, ["sector", "actividad"]),
                }
            )

        data["found"] = len(avisos) > 0
        data["total_avisos"] = len(avisos)
        data["avisos"] = avisos
        return data


def _extract(record: dict, keys: list[str]) -> str | None:
    for key in keys:
        for k, v in record.items():
            if key in k:
                return v or None
    return None
