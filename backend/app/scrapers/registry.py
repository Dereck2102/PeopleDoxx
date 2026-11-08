from __future__ import annotations

from app.scrapers.base import BaseScraper


class ScraperRegistry:
    """
    Registry that maps SOURCE_ID strings to BaseScraper subclasses.

    Scrapers self-register by decorating their class with
    ``@ScraperRegistry.register``.
    """

    _scrapers: dict[str, type[BaseScraper]] = {}

    @classmethod
    def register(cls, scraper_cls: type[BaseScraper]) -> type[BaseScraper]:
        """Class decorator that registers *scraper_cls* by its SOURCE_ID."""
        if not hasattr(scraper_cls, "SOURCE_ID") or not scraper_cls.SOURCE_ID:
            raise ValueError(
                f"{scraper_cls.__name__} must define a non-empty SOURCE_ID."
            )
        cls._scrapers[scraper_cls.SOURCE_ID] = scraper_cls
        return scraper_cls

    @classmethod
    def get_all(cls, delay: float = 1.0) -> list[BaseScraper]:
        """Return instantiated instances of every registered scraper."""
        return [scraper_cls(delay=delay) for scraper_cls in cls._scrapers.values()]

    @classmethod
    def get(cls, source_id: str, delay: float = 1.0) -> BaseScraper | None:
        """Return an instance of the scraper with the given SOURCE_ID, or None."""
        scraper_cls = cls._scrapers.get(source_id)
        if scraper_cls is None:
            return None
        return scraper_cls(delay=delay)

    @classmethod
    def registered_ids(cls) -> list[str]:
        """Return a sorted list of all registered SOURCE_IDs."""
        return sorted(cls._scrapers.keys())
