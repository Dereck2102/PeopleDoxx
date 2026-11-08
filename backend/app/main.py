from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncIterator

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import admin as admin_router
from app.api.v1 import auth as auth_router
from app.api.v1 import reports as reports_router
from app.api.v1 import search as search_router
from app.core.config import get_settings
from app.core.logger import get_logger
from app.core.security import generate_api_key, hash_password
from app.db.models import Base, User, UserRole
from app.db.session import AsyncSessionLocal, engine

logger = get_logger(__name__)
settings = get_settings()


# ---------------------------------------------------------------------------
# Lifespan — startup / shutdown
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    1. Connect to Redis.
    2. Create all DB tables (idempotent).
    3. Bootstrap the first admin user if the DB is empty.
    """
    # Redis
    logger.info("Connecting to Redis", url=settings.REDIS_URL)
    redis_client = aioredis.from_url(
        settings.REDIS_URL, encoding="utf-8", decode_responses=True
    )
    try:
        await redis_client.ping()
        logger.info("Redis connection established")
    except Exception as exc:
        logger.warning("Redis unavailable — caching disabled", error=str(exc))

    app.state.redis = redis_client

    # Database — create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified/created")

    # Bootstrap admin
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.role == UserRole.ADMIN))
        if result.scalar_one_or_none() is None:
            admin = User(
                email=settings.ADMIN_EMAIL,
                password_hash=hash_password(settings.ADMIN_PASSWORD),
                full_name="Administrator",
                role=UserRole.ADMIN,
                is_active=True,
                terms_accepted=True,
                terms_accepted_at=datetime.now(tz=timezone.utc),
                api_key=generate_api_key(),
            )
            db.add(admin)
            await db.commit()
            await db.refresh(admin)
            logger.info(
                "Bootstrap admin created",
                email=settings.ADMIN_EMAIL,
                api_key=admin.api_key,
            )

    yield

    logger.info("Closing Redis connection")
    await redis_client.aclose()


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    app = FastAPI(
        title="PeopleDoxx API",
        description=(
            "Open-source platform for aggregating publicly available information "
            "from Ecuadorian government portals (SRI, SATJE, SUPA, IESS, CNE, MDT) "
            "using a cédula number. Designed for licensed private investigators, "
            "legal verification and academic use. "
            "\n\n**Aviso legal / Legal notice:** Use must comply with Ecuador's "
            "Ley Orgánica de Protección de Datos Personales (LOPDP)."
        ),
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ---- CORS (permissive for dev; restrict origins in production via env) --
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---- Routers ------------------------------------------------------------
    app.include_router(auth_router.router)
    app.include_router(search_router.router)
    app.include_router(reports_router.router)
    app.include_router(admin_router.router)

    # ---- Health check -------------------------------------------------------
    @app.get("/health", tags=["ops"], summary="Health check", response_model=dict)
    async def health() -> dict:
        return {
            "status": "ok",
            "environment": settings.ENVIRONMENT,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "version": "2.0.0",
        }

    return app


app = create_app()
