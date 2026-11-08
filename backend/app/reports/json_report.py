from __future__ import annotations

from app.models.report import FullReport
from app.reports.base_report import BaseReport


class JsonReport(BaseReport):
    """Generates a JSON report from a ``FullReport``."""

    def generate(self, report: FullReport) -> bytes:
        return report.model_dump_json(indent=2).encode("utf-8")
