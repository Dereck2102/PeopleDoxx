"""
Search endpoints — now user-aware with quota enforcement, source filtering and audit logging.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Annotated

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.dependencies import enforce_quota, filter_sources_for_user
from app.core.logger import get_logger
from app.core.orchestrator import ScraperOrchestrator
from app.db.models import SearchHistory, User
from app.db.session import get_db
from app.models.cedula import CedulaRequest, CedulaResponse
from app.models.report import ScraperResult
from app.scrapers import cne, iess, mdt, satje, sri, supa  # noqa: F401
from app.scrapers.registry import ScraperRegistry

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/search", tags=["search"])
settings = get_settings()


# ---------------------------------------------------------------------------
# Redis helpers
# ---------------------------------------------------------------------------

def _redis_key(cedula: str) -> str:
    return f"result:{cedula}"


async def _get_redis(request: Request) -> aioredis.Redis:
    return request.app.state.redis


async def _cache_get(redis: aioredis.Redis, cedula: str) -> list[ScraperResult] | None:
    raw = await redis.get(_redis_key(cedula))
    if raw is None:
        return None
    try:
        return [ScraperResult(**item) for item in json.loads(raw)]
    except Exception as exc:
        logger.warning("Cache deserialisation failed", cedula=cedula, error=str(exc))
        return None


async def _cache_set(redis: aioredis.Redis, cedula: str, results: list[ScraperResult]) -> None:
    payload = json.dumps([r.model_dump(mode="json") for r in results])
    await redis.set(_redis_key(cedula), payload, ex=settings.CACHE_TTL_SECONDS)


# ---------------------------------------------------------------------------
# Audit helper
# ---------------------------------------------------------------------------

async def _log_search(
    db: AsyncSession,
    user: User,
    cedula: str,
    results: list[ScraperResult],
    cached: bool,
    request: Request,
) -> None:
    history = SearchHistory(
        user_id=user.id,
        cedula=cedula,
        sources_queried=[r.source for r in results],
        sources_successful=sum(1 for r in results if r.success),
        sources_total=len(results),
        result_cached=cached,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(history)
    await db.commit()


# ---------------------------------------------------------------------------
# Shared fetch helper (source-filtered)
# ---------------------------------------------------------------------------

async def _fetch_results(
    cedula: str,
    redis: aioredis.Redis,
    allowed_sources: list[str] | None,
) -> tuple[list[ScraperResult], bool]:
    """Return (results, was_cached). Filters sources by user permission."""
    all_ids = ScraperRegistry.registered_ids()
    source_ids = allowed_sources if allowed_sources is not None else all_ids

    # Cache key includes source filter so different users get correct slices
    cache_key = f"result:{cedula}:{','.join(sorted(source_ids))}"
    raw = await redis.get(cache_key)
    if raw is not None:
        try:
            cached_results = [ScraperResult(**item) for item in json.loads(raw)]
            logger.info("Cache hit", cedula=cedula, sources=source_ids)
            return cached_results, True
        except Exception:
            pass

    orchestrator = ScraperOrchestrator(
        registry=ScraperRegistry,
        delay=settings.REQUEST_DELAY_SECONDS,
        source_ids=source_ids,
    )
    results = await orchestrator.run(cedula)
    payload = json.dumps([r.model_dump(mode="json") for r in results])
    await redis.set(cache_key, payload, ex=settings.CACHE_TTL_SECONDS)
    return results, False


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=CedulaResponse,
    summary="Search a cédula across allowed public portals",
)
async def search_cedula(
    request: Request,
    body: CedulaRequest,
    user: Annotated[User, Depends(enforce_quota)],
    db: AsyncSession = Depends(get_db),
) -> CedulaResponse:
    """
    Validate cédula, run scrapers concurrently (filtered by user permissions),
    cache result, log to audit history and return consolidated response.
    """
    redis = await _get_redis(request)
    all_ids = ScraperRegistry.registered_ids()
    allowed = filter_sources_for_user(user, all_ids)

    results, was_cached = await _fetch_results(body.cedula, redis, allowed)
    await _log_search(db, user, body.cedula, results, was_cached, request)
    return CedulaResponse.from_results(body.cedula, results)


@router.get(
    "/{cedula}",
    response_model=CedulaResponse,
    summary="Retrieve (or refresh) results for a cédula",
)
async def get_cedula(
    request: Request,
    cedula: str,
    user: Annotated[User, Depends(enforce_quota)],
    db: AsyncSession = Depends(get_db),
) -> CedulaResponse:
    """Return cached results if available; otherwise run a fresh query."""
    try:
        validated = CedulaRequest(cedula=cedula)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    redis = await _get_redis(request)
    all_ids = ScraperRegistry.registered_ids()
    allowed = filter_sources_for_user(user, all_ids)

    results, was_cached = await _fetch_results(validated.cedula, redis, allowed)
    await _log_search(db, user, validated.cedula, results, was_cached, request)
    return CedulaResponse.from_results(validated.cedula, results)


@router.get("/sources", summary="List all registered scraper sources")
async def list_sources(
    user: Annotated[User, Depends(enforce_quota.__wrapped__ if hasattr(enforce_quota, '__wrapped__') else enforce_quota)],
) -> list[dict]:
    """Return the list of sources available to the authenticated user."""
    all_ids = ScraperRegistry.registered_ids()
    all_scrapers = ScraperRegistry.get_all()
    scraper_map = {s.SOURCE_ID: s for s in all_scrapers}
    allowed = filter_sources_for_user(user, all_ids)
    return [
        {
            "source_id": sid,
            "source_name": scraper_map[sid].SOURCE_NAME if sid in scraper_map else sid,
            "base_url": scraper_map[sid].BASE_URL if sid in scraper_map else "",
            "enabled": sid in allowed,
        }
        for sid in all_ids
    ]


@router.get("/me/history", summary="My search history")
async def my_history(
    user: Annotated[User, Depends(enforce_quota.__wrapped__ if hasattr(enforce_quota, '__wrapped__') else enforce_quota)],
    db: AsyncSession = Depends(get_db),
    limit: int = 20,
) -> list[dict]:
    """Return the last N searches for the authenticated user."""
    from sqlalchemy import select
    result = await db.execute(
        select(SearchHistory)
        .where(SearchHistory.user_id == user.id)
        .order_by(SearchHistory.created_at.desc())
        .limit(limit)
    )
    rows = result.scalars().all()
    return [
        {
            "cedula": h.cedula,
            "sources_total": h.sources_total,
            "sources_successful": h.sources_successful,
            "result_cached": h.result_cached,
            "created_at": h.created_at.isoformat(),
        }
        for h in rows
    ]
