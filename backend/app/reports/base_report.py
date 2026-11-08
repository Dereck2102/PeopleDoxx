from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.report import FullReport


class BaseReport(ABC):
    """Abstract base class for report generators."""

    @abstractmethod
    def generate(self, report: FullReport) -> bytes:
        """
        Generate a report from *report* and return the raw bytes.

        The concrete format (PDF, JSON, CSV, …) is determined by the
        implementing subclass.
        """
        ...
