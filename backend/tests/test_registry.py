"""
Tests for ScraperRegistry.

Importing app.scrapers triggers all @ScraperRegistry.register decorators.
"""
from __future__ import annotations

import pytest

import app.scrapers  # noqa: F401 — side-effect: registers all scrapers
from app.scrapers.cne import CneScraper
from app.scrapers.iess import IessScraper
from app.scrapers.mdt import MdtScraper
from app.scrapers.registry import ScraperRegistry
from app.scrapers.satje import SatjeScraper
from app.scrapers.sri import SriScraper
from app.scrapers.supa import SupaScraper


# ---------------------------------------------------------------------------
# Registration presence
# ---------------------------------------------------------------------------

EXPECTED_SOURCE_IDS = ["CNE", "IESS", "MDT", "SATJE", "SRI", "SUPA"]


@pytest.mark.parametrize("source_id", EXPECTED_SOURCE_IDS)
def test_scraper_is_registered(source_id: str) -> None:
    assert source_id in ScraperRegistry.registered_ids(), (
        f"{source_id} was not found in the registry. "
        "Check that app/scrapers/__init__.py imports it."
    )


def test_all_expected_scrapers_registered() -> None:
    registered = set(ScraperRegistry.registered_ids())
    expected = set(EXPECTED_SOURCE_IDS)
    assert expected.issubset(registered), (
        f"Missing scrapers: {expected - registered}"
    )


# ---------------------------------------------------------------------------
# get_all()
# ---------------------------------------------------------------------------

def test_get_all_returns_all_scrapers() -> None:
    scrapers = ScraperRegistry.get_all(delay=0.0)
    registered_count = len(ScraperRegistry.registered_ids())
    assert len(scrapers) == registered_count


def test_get_all_returns_base_scraper_instances() -> None:
    from app.scrapers.base import BaseScraper
    for scraper in ScraperRegistry.get_all(delay=0.0):
        assert isinstance(scraper, BaseScraper)


def test_get_all_respects_delay() -> None:
    scrapers = ScraperRegistry.get_all(delay=2.5)
    for scraper in scrapers:
        assert scraper._delay == 2.5


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "source_id, expected_type",
    [
        ("SRI", SriScraper),
        ("SATJE", SatjeScraper),
        ("SUPA", SupaScraper),
        ("IESS", IessScraper),
        ("CNE", CneScraper),
        ("MDT", MdtScraper),
    ],
)
def test_get_returns_correct_type(source_id: str, expected_type: type) -> None:
    scraper = ScraperRegistry.get(source_id, delay=0.0)
    assert scraper is not None
    assert isinstance(scraper, expected_type)


def test_get_unknown_source_returns_none() -> None:
    result = ScraperRegistry.get("NONEXISTENT", delay=0.0)
    assert result is None


def test_get_respects_delay() -> None:
    scraper = ScraperRegistry.get("SRI", delay=3.7)
    assert scraper is not None
    assert scraper._delay == 3.7


# ---------------------------------------------------------------------------
# SOURCE_ID / SOURCE_NAME class attributes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "scraper_cls, expected_id",
    [
        (SriScraper, "SRI"),
        (SatjeScraper, "SATJE"),
        (SupaScraper, "SUPA"),
        (IessScraper, "IESS"),
        (CneScraper, "CNE"),
        (MdtScraper, "MDT"),
    ],
)
def test_source_id_attribute(scraper_cls: type, expected_id: str) -> None:
    assert scraper_cls.SOURCE_ID == expected_id


@pytest.mark.parametrize("scraper_cls", [SriScraper, SatjeScraper, SupaScraper, IessScraper, CneScraper, MdtScraper])
def test_source_name_is_non_empty(scraper_cls: type) -> None:
    assert scraper_cls.SOURCE_NAME and isinstance(scraper_cls.SOURCE_NAME, str)


# ---------------------------------------------------------------------------
# registered_ids() ordering
# ---------------------------------------------------------------------------

def test_registered_ids_are_sorted() -> None:
    ids = ScraperRegistry.registered_ids()
    assert ids == sorted(ids)
