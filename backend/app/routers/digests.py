"""Digest list endpoint."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Digest, get_db
from app.models import DigestResponse

router = APIRouter(prefix="/digests", tags=["digests"])


@router.get("", response_model=list[DigestResponse])
async def list_digests(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[DigestResponse]:
    """List past digests ordered by most recent first."""
    stmt = select(Digest).order_by(Digest.sent_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return result.scalars().all()
