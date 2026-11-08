from __future__ import annotations

import asyncio

from app.core.logger import get_logger
from app.models.report import ScraperResult
from app.scrapers.registry import ScraperRegistry

logger = get_logger(__name__)


class ScraperOrchestrator:
    """
    Runs all registered scrapers concurrently for a given cédula.

    Depends on the ``ScraperRegistry`` abstraction, not on any concrete
    scraper — satisfying the Dependency Inversion Principle.
    """

    def __init__(
        self,
        registry: type[ScraperRegistry],
        delay: float = 1.0,
        source_ids: list[str] | None = None,
    ) -> None:
        self._registry = registry
        self._delay = delay
        self._source_ids = source_ids  # None = all registered

    async def run(self, cedula: str) -> list[ScraperResult]:
        """
        Execute scrapers concurrently and return all results.
        If *source_ids* was provided at construction time, only those
        sources are queried — honoring per-user source permissions.

        Individual scraper exceptions are caught inside each scraper's
        ``fetch`` method (they return a failed ``ScraperResult``).  Any
        unexpected exception that leaks out is caught here and converted
        to a failed result so a single broken scraper never aborts the
        whole run.
        """
        if self._source_ids is not None:
            scrapers = [
                s for s in self._registry.get_all(delay=self._delay)
                if s.SOURCE_ID in self._source_ids
            ]
        else:
            scrapers = self._registry.get_all(delay=self._delay)
        logger.info(
            "Orchestrator starting",
            cedula=cedula,
            scraper_count=len(scrapers),
        )

        tasks = [scraper.fetch(cedula) for scraper in scrapers]
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

        results: list[ScraperResult] = []
        for scraper, outcome in zip(scrapers, raw_results):
            if isinstance(outcome, ScraperResult):
                results.append(outcome)
            else:
                # An unexpected exception escaped the scraper — wrap it
                exc = outcome
                logger.error(
                    "Unexpected scraper exception",
                    source=scraper.SOURCE_ID,
                    error=str(exc),
                )
                results.append(
                    ScraperResult(
                        source=scraper.SOURCE_ID,
                        source_name=scraper.SOURCE_NAME,
                        success=False,
                        data={},
                        error=f"{type(exc).__name__}: {exc}",
                    )
                )

        successful = sum(1 for r in results if r.success)
        logger.info(
            "Orchestrator finished",
            cedula=cedula,
            total=len(results),
            successful=successful,
            failed=len(results) - successful,
        )
        return results
