"""Paper list and detail endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Paper, get_db
from app.models import PaperResponse

router = APIRouter(prefix="/papers", tags=["papers"])


@router.get("", response_model=list[PaperResponse])
async def list_papers(
    subfield: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    min_score: float | None = Query(None, ge=0.0, le=10.0),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[PaperResponse]:
    """List papers with optional filters."""
    stmt = select(Paper)
    if subfield:
        stmt = stmt.where(Paper.subfield == subfield)
    if date_from:
        stmt = stmt.where(Paper.published_at >= date_from)
    if date_to:
        stmt = stmt.where(Paper.published_at <= date_to)
    if min_score is not None:
        stmt = stmt.where(Paper.impact_score >= min_score)
    stmt = stmt.order_by(Paper.impact_score.desc(), Paper.published_at.desc())
    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(
    paper_id: str,
    db: AsyncSession = Depends(get_db),
) -> PaperResponse:
    """Get a single paper by ID."""
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper
