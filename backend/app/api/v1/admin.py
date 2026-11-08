"""
Admin panel API — full CRUD for user management and system configuration.
Only accessible to users with role=admin.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_admin
from app.core.security import generate_api_key, hash_password
from app.db.models import SearchHistory, User, UserRole
from app.db.session import get_db

router = APIRouter(prefix="/admin", tags=["admin"])

# All routes require admin role
AdminUser = Annotated[User, Depends(require_admin)]


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.USER
    quota_daily: int = 50
    quota_monthly: int = 500
    allowed_sources: list[str] | None = None
    can_download_pdf: bool = True
    can_download_json: bool = True
    expires_at: datetime | None = None


class UserUpdateRequest(BaseModel):
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    quota_daily: int | None = None
    quota_monthly: int | None = None
    allowed_sources: list[str] | None = None
    can_download_pdf: bool | None = None
    can_download_json: bool | None = None
    expires_at: datetime | None = None


class UserAdminView(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    terms_accepted: bool
    quota_daily: int
    quota_daily_used: int
    quota_monthly: int
    quota_monthly_used: int
    allowed_sources: list[str] | None
    can_download_pdf: bool
    can_download_json: bool
    expires_at: datetime | None
    api_key: str | None
    created_at: datetime
    updated_at: datetime
    total_searches: int = 0

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    items: list[UserAdminView]
    total: int
    page: int
    page_size: int


class QuotaResetRequest(BaseModel):
    reset_daily: bool = True
    reset_monthly: bool = False


class SystemStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_searches_all_time: int
    searches_today: int


# ---------------------------------------------------------------------------
# User list + detail
# ---------------------------------------------------------------------------

@router.get("/users", response_model=UserListResponse)
async def list_users(
    _admin: AdminUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: UserRole | None = None,
    is_active: bool | None = None,
    search: str | None = None,
) -> dict:
    """List all users with optional filters."""
    query = select(User)
    if role is not None:
        query = query.where(User.role == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    if search:
        query = query.where(
            User.email.ilike(f"%{search}%") | User.full_name.ilike(f"%{search}%")
        )

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar_one()

    query = query.offset((page - 1) * page_size).limit(page_size).order_by(User.created_at.desc())
    result = await db.execute(query)
    users = result.scalars().all()

    # Enrich with search counts
    items = []
    for user in users:
        count_result = await db.execute(
            select(func.count()).where(SearchHistory.user_id == user.id)
        )
        total_searches = count_result.scalar_one()
        view = UserAdminView.model_validate(user)
        view.total_searches = total_searches
        items.append(view)

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/users/{user_id}", response_model=UserAdminView)
async def get_user(
    user_id: uuid.UUID,
    _admin: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> UserAdminView:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    count_result = await db.execute(
        select(func.count()).where(SearchHistory.user_id == user.id)
    )
    view = UserAdminView.model_validate(user)
    view.total_searches = count_result.scalar_one()
    return view


# ---------------------------------------------------------------------------
# Create / Update / Delete
# ---------------------------------------------------------------------------

@router.post("/users", response_model=UserAdminView, status_code=201)
async def create_user(
    body: UserCreateRequest,
    _admin: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> UserAdminView:
    """Admin can create a user with fully configured permissions."""
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered.")

    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        full_name=body.full_name,
        role=body.role,
        quota_daily=body.quota_daily,
        quota_monthly=body.quota_monthly,
        allowed_sources=body.allowed_sources,
        can_download_pdf=body.can_download_pdf,
        can_download_json=body.can_download_json,
        expires_at=body.expires_at,
        # Admin-created users auto-accept terms
        terms_accepted=True,
        terms_accepted_at=datetime.now(tz=timezone.utc),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    view = UserAdminView.model_validate(user)
    view.total_searches = 0
    return view


@router.patch("/users/{user_id}", response_model=UserAdminView)
async def update_user(
    user_id: uuid.UUID,
    body: UserUpdateRequest,
    _admin: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> UserAdminView:
    """Update any user attribute. Only provided fields are changed."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    user.updated_at = datetime.now(tz=timezone.utc)

    await db.commit()
    await db.refresh(user)

    count_result = await db.execute(
        select(func.count()).where(SearchHistory.user_id == user.id)
    )
    view = UserAdminView.model_validate(user)
    view.total_searches = count_result.scalar_one()
    return view


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: uuid.UUID,
    _admin: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    await db.delete(user)
    await db.commit()


# ---------------------------------------------------------------------------
# Quota management
# ---------------------------------------------------------------------------

@router.post("/users/{user_id}/reset-quota", response_model=UserAdminView)
async def reset_quota(
    user_id: uuid.UUID,
    body: QuotaResetRequest,
    _admin: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> UserAdminView:
    """Manually reset a user's daily and/or monthly quota."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    now = datetime.now(tz=timezone.utc)
    if body.reset_daily:
        user.quota_daily_used = 0
        user.quota_daily_reset_at = now
    if body.reset_monthly:
        user.quota_monthly_used = 0
        user.quota_monthly_reset_at = now

    await db.commit()
    await db.refresh(user)
    view = UserAdminView.model_validate(user)
    view.total_searches = 0
    return view


@router.post("/users/{user_id}/generate-api-key", response_model=UserAdminView)
async def admin_generate_api_key(
    user_id: uuid.UUID,
    _admin: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> UserAdminView:
    """Generate or regenerate an API key for any user."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.api_key = generate_api_key()
    await db.commit()
    await db.refresh(user)
    view = UserAdminView.model_validate(user)
    return view


# ---------------------------------------------------------------------------
# Search history
# ---------------------------------------------------------------------------

@router.get("/users/{user_id}/history")
async def get_user_history(
    user_id: uuid.UUID,
    _admin: AdminUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    """Full search history for a user."""
    query = (
        select(SearchHistory)
        .where(SearchHistory.user_id == user_id)
        .order_by(SearchHistory.created_at.desc())
    )
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar_one()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": [
            {
                "id": str(h.id),
                "cedula": h.cedula,
                "sources_queried": h.sources_queried,
                "sources_successful": h.sources_successful,
                "sources_total": h.sources_total,
                "result_cached": h.result_cached,
                "ip_address": h.ip_address,
                "created_at": h.created_at.isoformat(),
            }
            for h in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# ---------------------------------------------------------------------------
# System stats
# ---------------------------------------------------------------------------

@router.get("/stats", response_model=SystemStatsResponse)
async def get_stats(
    _admin: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Aggregate usage statistics."""
    from datetime import timedelta
    today_start = datetime.now(tz=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    total_users = (await db.execute(select(func.count(User.id)))).scalar_one()
    active_users = (
        await db.execute(select(func.count(User.id)).where(User.is_active == True))  # noqa: E712
    ).scalar_one()
    total_searches = (await db.execute(select(func.count(SearchHistory.id)))).scalar_one()
    searches_today = (
        await db.execute(
            select(func.count(SearchHistory.id)).where(
                SearchHistory.created_at >= today_start
            )
        )
    ).scalar_one()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_searches_all_time": total_searches,
        "searches_today": searches_today,
    }

