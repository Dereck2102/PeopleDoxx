from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator

import httpx

from app.models.report import ScraperResult

_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

_DEFAULT_HEADERS = {
    "User-Agent": _BROWSER_UA,
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "es-EC,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


class BaseScraper(ABC):
    """
    Abstract base class that every portal scraper must implement.

    Subclasses MUST define:
      - SOURCE_ID   : short machine-readable identifier (e.g. "SRI")
      - SOURCE_NAME : human-readable name  (e.g. "Servicio de Rentas Internas")
      - BASE_URL    : root URL of the portal being scraped
    """

    SOURCE_ID: str
    SOURCE_NAME: str
    BASE_URL: str

    def __init__(self, delay: float = 1.0) -> None:
        self._delay = delay

    @abstractmethod
    async def fetch(self, cedula: str) -> ScraperResult:
        """Fetch data for a given cédula from the public portal."""
        ...

    async def _get_client(self) -> httpx.AsyncClient:
        """Return a configured async HTTP client with browser-like headers."""
        return httpx.AsyncClient(
            headers=_DEFAULT_HEADERS,
            timeout=httpx.Timeout(30.0, connect=10.0),
            follow_redirects=True,
        )

    @asynccontextmanager
    async def _timed_fetch(
        self, cedula: str
    ) -> AsyncGenerator[dict[str, object], None]:
        """
        Context manager that:
          - applies the courtesy delay
          - measures wall-clock duration
          - yields a mutable state dict so the caller can store results
          - catches any exception and converts it to a failed ScraperResult

        Usage::

            async with self._timed_fetch(cedula) as state:
                state["result"] = ScraperResult(...)

            return state["result"]
        """
        await asyncio.sleep(self._delay)
        start = time.monotonic()
        state: dict[str, object] = {"result": None}
        try:
            yield state
        except Exception as exc:  # noqa: BLE001
            duration_ms = (time.monotonic() - start) * 1000
            state["result"] = ScraperResult(
                source=self.SOURCE_ID,
                source_name=self.SOURCE_NAME,
                success=False,
                data={},
                fetched_at=datetime.now(tz=timezone.utc),
                error=f"{type(exc).__name__}: {exc}",
                duration_ms=round(duration_ms, 2),
            )
        finally:
            if state.get("result") is not None:
                result = state["result"]
                if isinstance(result, ScraperResult) and result.duration_ms == 0.0:
                    result.duration_ms = round(
                        (time.monotonic() - start) * 1000, 2
                    )
