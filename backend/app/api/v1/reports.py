from __future__ import annotations

import json
from typing import Annotated

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.responses import Response, StreamingResponse

from app.core.config import get_settings
from app.core.limiter import limiter
from app.core.logger import get_logger
from app.core.orchestrator import ScraperOrchestrator
from app.models.cedula import CedulaRequest
from app.models.report import FullReport, ScraperResult
from app.reports.json_report import JsonReport
from app.reports.pdf_report import PdfReport
from app.scrapers import cne, iess, mdt, satje, sri, supa  # noqa: F401
from app.scrapers.registry import ScraperRegistry

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/reports", tags=["reports"])
settings = get_settings()

_pdf_generator = PdfReport()
_json_generator = JsonReport()


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------

async def _require_api_key(
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header.",
        )


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _redis_key(cedula: str) -> str:
    return f"result:{cedula}"


async def _get_redis(request: Request) -> aioredis.Redis:
    return request.app.state.redis


async def _resolve_results(
    cedula: str, redis: aioredis.Redis
) -> list[ScraperResult]:
    """Return cached results or trigger a fresh scraping run."""
    raw = await redis.get(_redis_key(cedula))
    if raw is not None:
        try:
            items = json.loads(raw)
            return [ScraperResult(**item) for item in items]
        except Exception as exc:  # noqa: BLE001
            logger.warning("Cache read error in reports", cedula=cedula, error=str(exc))

    # Cache miss — run scrapers and store result
    orchestrator = ScraperOrchestrator(
        registry=ScraperRegistry,
        delay=settings.REQUEST_DELAY_SECONDS,
    )
    results = await orchestrator.run(cedula)
    payload = json.dumps([r.model_dump(mode="json") for r in results])
    await redis.set(_redis_key(cedula), payload, ex=settings.CACHE_TTL_SECONDS)
    return results


def _validate_cedula(cedula: str) -> str:
    try:
        return CedulaRequest(cedula=cedula).cedula
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/{cedula}/pdf",
    summary="Download a PDF report for a cédula",
    response_class=Response,
    dependencies=[Depends(_require_api_key)],
)
@limiter.limit(settings.RATE_LIMIT)
async def download_pdf(
    request: Request,
    cedula: str,
) -> StreamingResponse:
    """
    Generate and stream a PDF report for the given *cedula*.  Uses cached
    data if available; otherwise triggers a fresh scraping run.
    """
    validated = _validate_cedula(cedula)
    redis = await _get_redis(request)
    results = await _resolve_results(validated, redis)
    report = FullReport.from_results(validated, results)
    pdf_bytes = _pdf_generator.generate(report)

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="peopledoxx_{validated}.pdf"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )


@router.get(
    "/{cedula}/json",
    summary="Download a JSON report for a cédula",
    response_class=Response,
    dependencies=[Depends(_require_api_key)],
)
@limiter.limit(settings.RATE_LIMIT)
async def download_json(
    request: Request,
    cedula: str,
) -> Response:
    """
    Return a full JSON report for the given *cedula*.  Uses cached data
    if available; otherwise triggers a fresh scraping run.
    """
    validated = _validate_cedula(cedula)
    redis = await _get_redis(request)
    results = await _resolve_results(validated, redis)
    report = FullReport.from_results(validated, results)
    json_bytes = _json_generator.generate(report)

    return Response(
        content=json_bytes,
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="peopledoxx_{validated}.json"',
        },
    )
