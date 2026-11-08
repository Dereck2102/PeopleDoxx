"""
Database models using SQLAlchemy 2.0 async ORM.
All tables for PeopleDoxx user management and audit logging.
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


class Base(DeclarativeBase):
    pass


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    """Registered user of PeopleDoxx."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), nullable=False, default=UserRole.USER
    )

    # Account state
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    terms_accepted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    terms_accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # API key (for CLI/integrations)
    api_key: Mapped[str | None] = mapped_column(
        String(64), unique=True, nullable=True, index=True
    )

    # Quota — daily
    quota_daily: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    quota_daily_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quota_daily_reset_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    # Quota — monthly
    quota_monthly: Mapped[int] = mapped_column(Integer, default=500, nullable=False)
    quota_monthly_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quota_monthly_reset_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    # Permissions
    # JSON list of SOURCE_IDs the user can access, e.g. ["SRI", "SATJE"]
    # null = all sources allowed
    allowed_sources: Mapped[list | None] = mapped_column(JSON, nullable=True)
    can_download_pdf: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_download_json: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    # Relationships
    searches: Mapped[list[SearchHistory]] = relationship(
        "SearchHistory", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User {self.email} role={self.role}>"


class SearchHistory(Base):
    """Audit log of every search performed by a user."""

    __tablename__ = "search_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cedula: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    sources_queried: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    sources_successful: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sources_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    result_cached: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    # Relationship
    user: Mapped[User] = relationship("User", back_populates="searches")

    def __repr__(self) -> str:
        return f"<SearchHistory cedula={self.cedula} user={self.user_id}>"

