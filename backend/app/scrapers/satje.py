from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.logger import get_logger
from app.models.report import ScraperResult
from app.scrapers.base import BaseScraper
from app.scrapers.registry import ScraperRegistry

logger = get_logger(__name__)


@ScraperRegistry.register
class SatjeScraper(BaseScraper):
    """
    Scraper for SATJE / SACC (Sistema Automatizado de Trámites Judiciales del Ecuador).

    Queries the public judicial case API and returns a list of causes
    where the person appears as actor or defendant.
    """

    SOURCE_ID = "SATJE"
    SOURCE_NAME = "Sistema de Administración de Justicia (Función Judicial)"
    BASE_URL = (
        "https://consultas.funcionjudicial.gob.ec/SACC/api/consultas/informacionCausa"
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
                    params={
                        "cedula": cedula,
                        "numeroCausa": "",
                        "actor": "",
                        "demandado": "",
                    },
                    headers={
                        "Accept": "application/json, text/plain, */*",
                        "Referer": "https://consultas.funcionjudicial.gob.ec/",
                    },
                )
                response.raise_for_status()
                raw: Any = response.json()

            causes = self._parse(raw)
            duration_ms = round((time.monotonic() - start) * 1000, 2)

            logger.info(
                "SATJE fetch completed",
                cedula=cedula,
                causes_found=len(causes),
                duration_ms=duration_ms,
            )
            return ScraperResult(
                source=self.SOURCE_ID,
                source_name=self.SOURCE_NAME,
                success=True,
                data={
                    "cedula_consultada": cedula,
                    "total_causas": len(causes),
                    "causas": causes,
                },
                fetched_at=datetime.now(tz=timezone.utc),
                duration_ms=duration_ms,
            )

        except Exception as exc:  # noqa: BLE001
            duration_ms = round((time.monotonic() - start) * 1000, 2)
            logger.warning(
                "SATJE fetch failed",
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

    def _parse(self, raw: Any) -> list[dict]:
        """Normalise the JSON payload returned by the SACC API."""
        if not isinstance(raw, list):
            # Some responses wrap the list in a dict
            if isinstance(raw, dict):
                for key in ("data", "causas", "results", "items"):
                    if key in raw and isinstance(raw[key], list):
                        raw = raw[key]
                        break
                else:
                    return []
            else:
                return []

        causes: list[dict] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            causes.append(
                {
                    "causa_id": item.get("idJuicio") or item.get("causa_id") or item.get("id"),
                    "fecha_ingreso": item.get("fechaIngreso") or item.get("fecha_ingreso"),
                    "materia": item.get("materia") or item.get("nombreMateria"),
                    "tipo_juicio": item.get("tipoJuicio") or item.get("tipo_juicio"),
                    "actor": item.get("actor") or item.get("nombreActor"),
                    "demandado": item.get("demandado") or item.get("nombreDemandado"),
                    "estado_proceso": item.get("estadoProceso") or item.get("estado"),
                    "judicatura": item.get("judicatura") or item.get("nombreJudicatura"),
                }
            )
        return causes
