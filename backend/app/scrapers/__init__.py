# Import all scrapers so their @ScraperRegistry.register decorators fire
# and they appear in ScraperRegistry._scrapers before any caller asks for them.
from app.scrapers import cne, iess, mdt, satje, sri, supa  # noqa: F401

__all__ = ["cne", "iess", "mdt", "satje", "sri", "supa"]
