"""
FastAPI dependencies for authentication and quota enforcement.

Dependency hierarchy:
  get_current_user_from_jwt   ← Bearer token (web/mobile)
  get_current_user_from_key   ← X-API-Key header (CLI/integrations)
  get_current_user            ← tries JWT first, then API key
  require_active_user         ← ensures account is active + not expired
  require_admin               ← requires role == admin
  enforce_quota               ← checks + increments daily/monthly quota
  require_pdf_permission      ← checks can_download_pdf
  require_json_permission     ← checks can_download_json
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.models import User, UserRole
from app.db.session import get_db

_bearer = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

async def _get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def _get_user_by_api_key(db: AsyncSession, api_key: str) -> User | None:
    result = await db.execute(select(User).where(User.api_key == api_key))
    return result.scalar_one_or_none()


# ---------------------------------------------------------------------------
# Primary auth dependencies
# ---------------------------------------------------------------------------

async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)] = None,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Try JWT Bearer first, then fall back to X-API-Key header.
    Raises HTTP 401 if neither is provided or valid.
    """
    # --- JWT path ---
    if credentials is not None:
        try:
            payload = decode_token(credentials.credentials)
            if payload.get("type") != "access":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type.")
            user_id = uuid.UUID(payload["sub"])
        except (JWTError, ValueError, KeyError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired JWT token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = await _get_user_by_id(db, user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
        return user

    # --- API key path ---
    if x_api_key is not None:
        user = await _get_user_by_api_key(db, x_api_key)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key.",
            )
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Provide Bearer token or X-API-Key header.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def require_active_user(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Ensures the account is active and not expired."""
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled.")
    if not user.terms_accepted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must accept the terms of service before using PeopleDoxx.",
        )
    if user.expires_at and datetime.now(tz=timezone.utc) > user.expires_at:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account has expired.")
    return user


async def require_admin(
    user: Annotated[User, Depends(require_active_user)],
) -> User:
    """Requires admin role."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return user


# ---------------------------------------------------------------------------
# Quota enforcement
# ---------------------------------------------------------------------------

def _reset_quota_if_needed(user: User) -> None:
    """Reset daily/monthly quota counters in-place if the period has elapsed."""
    now = datetime.now(tz=timezone.utc)

    # Daily reset (every 24 h from last reset)
    if now >= user.quota_daily_reset_at + timedelta(hours=24):
        user.quota_daily_used = 0
        user.quota_daily_reset_at = now

    # Monthly reset (every 30 days from last reset)
    if now >= user.quota_monthly_reset_at + timedelta(days=30):
        user.quota_monthly_used = 0
        user.quota_monthly_reset_at = now


async def enforce_quota(
    user: Annotated[User, Depends(require_active_user)],
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Check and increment daily + monthly search quotas.
    Admins bypass quota checks.
    """
    if user.role == UserRole.ADMIN:
        return user  # admins are unrestricted

    _reset_quota_if_needed(user)

    if user.quota_daily_used >= user.quota_daily:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily quota exhausted ({user.quota_daily} searches/day). Resets in 24h.",
        )
    if user.quota_monthly_used >= user.quota_monthly:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Monthly quota exhausted ({user.quota_monthly} searches/month). Resets in 30 days.",
        )

    user.quota_daily_used += 1
    user.quota_monthly_used += 1
    await db.commit()

    return user


# ---------------------------------------------------------------------------
# Permission checks
# ---------------------------------------------------------------------------

async def require_pdf_permission(
    user: Annotated[User, Depends(require_active_user)],
) -> User:
    if not user.can_download_pdf:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="PDF download is not enabled for your account.",
        )
    return user


async def require_json_permission(
    user: Annotated[User, Depends(require_active_user)],
) -> User:
    if not user.can_download_json:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="JSON download is not enabled for your account.",
        )
    return user


def filter_sources_for_user(user: User, all_source_ids: list[str]) -> list[str]:
    """
    Return only the SOURCE_IDs the user is allowed to query.
    None = no restriction (all allowed).
    """
    if user.allowed_sources is None:
        return all_source_ids
    return [s for s in all_source_ids if s in user.allowed_sources]

