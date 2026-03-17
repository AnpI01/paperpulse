"""Aggregate stats endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Digest, Paper, get_db
from app.models import DailyCount, StatsResponse

router = APIRouter(prefix="/stats", tags=["stats"])

_DAILY_TREND_DAYS = 14


@router.get("", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)) -> StatsResponse:
    """Return aggregate paper counts, subfield breakdown, and daily trends."""
    total = (await db.execute(select(func.count()).select_from(Paper))).scalar_one()

    annotated = (
        await db.execute(
            select(func.count()).select_from(Paper).where(Paper.summary.is_not(None))
        )
    ).scalar_one()

    subfield_rows = (
        await db.execute(
            select(Paper.subfield, func.count().label("cnt"))
            .where(Paper.subfield.is_not(None))
            .group_by(Paper.subfield)
            .order_by(func.count().desc())
        )
    ).all()
    papers_by_subfield = {row.subfield: row.cnt for row in subfield_rows}

    daily_rows = (
        await db.execute(
            select(
                func.date(Paper.published_at).label("day"),
                func.count().label("cnt"),
            )
            .group_by(func.date(Paper.published_at))
            .order_by(func.date(Paper.published_at).desc())
            .limit(_DAILY_TREND_DAYS)
        )
    ).all()
    daily_counts = [
        DailyCount(date=str(row.day), count=row.cnt) for row in reversed(daily_rows)
    ]

    total_digests = (
        await db.execute(select(func.count()).select_from(Digest))
    ).scalar_one()

    return StatsResponse(
        total_papers=total,
        annotated_count=annotated,
        papers_by_subfield=papers_by_subfield,
        daily_counts=daily_counts,
        total_digests=total_digests,
    )
