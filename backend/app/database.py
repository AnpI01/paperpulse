"""SQLAlchemy async engine, session factory, and ORM models."""

import json
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config import settings

def _async_db_url(url: str) -> str:
    """Rewrite sync postgres:// URLs to the asyncpg driver scheme."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


engine = create_async_engine(_async_db_url(settings.database_url), echo=False)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    source: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    authors: Mapped[str] = mapped_column(Text, nullable=False)         # JSON list of names
    abstract: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    pdf_url: Mapped[str | None] = mapped_column(String)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    categories: Mapped[str | None] = mapped_column(String)
    # AI-generated (Phase 2)
    summary: Mapped[str | None] = mapped_column(Text)
    subfield: Mapped[str | None] = mapped_column(String)
    impact_score: Mapped[float | None] = mapped_column(Float)
    key_takeaway: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    digest_sent: Mapped[bool] = mapped_column(Boolean, default=False)


class Digest(Base):
    __tablename__ = "digests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    paper_count: Mapped[int] = mapped_column(Integer)
    email_html: Mapped[str | None] = mapped_column(Text)
    top_papers: Mapped[str | None] = mapped_column(Text)               # JSON list of paper IDs


async def get_db() -> AsyncSession:
    """FastAPI dependency that yields a database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """Create all tables (used in development; production uses Alembic)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
