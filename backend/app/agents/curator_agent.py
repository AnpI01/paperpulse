"""Pure-Python curator: ranks and groups annotated papers for the digest."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Paper


def rank_papers(papers: list[Paper], top_n: int = 10) -> list[Paper]:
    """Return top N papers sorted by impact_score descending."""
    scored = [p for p in papers if p.impact_score is not None]
    scored.sort(key=lambda p: p.impact_score, reverse=True)
    return scored[:top_n]


def group_by_subfield(papers: list[Paper]) -> dict[str, list[Paper]]:
    """Group papers by subfield, preserving impact score order within each group."""
    groups: dict[str, list[Paper]] = {}
    for paper in papers:
        key = paper.subfield or "Other"
        groups.setdefault(key, []).append(paper)
    return groups


async def curate_papers(
    db: AsyncSession,
    days_back: int = 1,
    top_n: int = 10,
) -> dict:
    """Fetch annotated papers from DB, rank and group. Returns curation result."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)

    result = await db.execute(
        select(Paper).where(
            Paper.summary.is_not(None),
            Paper.digest_sent.is_(False),
            Paper.published_at >= cutoff,
        )
    )
    papers = result.scalars().all()

    top_papers = rank_papers(papers, top_n=top_n)
    by_subfield = group_by_subfield(top_papers)

    return {
        "top_papers": top_papers,
        "by_subfield": by_subfield,
        "total_annotated": len(papers),
    }
