from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ScraperResult(BaseModel):
    """Result produced by a single scraper."""

    source: str
    source_name: str
    success: bool
    data: dict[str, Any] = Field(default_factory=dict)
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    error: str | None = None
    duration_ms: float = 0.0


class ReportMetadata(BaseModel):
    """Metadata for a generated report."""

    cedula: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    total_sources: int
    successful_sources: int
    failed_sources: int


class FullReport(BaseModel):
    """Complete report containing metadata and all scraper results."""

    metadata: ReportMetadata
    results: list[ScraperResult]

    @classmethod
    def from_results(cls, cedula: str, results: list[ScraperResult]) -> "FullReport":
        successful = sum(1 for r in results if r.success)
        return cls(
            metadata=ReportMetadata(
                cedula=cedula,
                total_sources=len(results),
                successful_sources=successful,
                failed_sources=len(results) - successful,
            ),
            results=results,
        )
