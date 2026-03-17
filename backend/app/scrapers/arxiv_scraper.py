"""arXiv Atom feed scraper."""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone

import feedparser
import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

ARXIV_API_URL = "https://export.arxiv.org/api/query"


async def fetch_arxiv_papers(
    categories: list[str],
    days_back: int,
    max_results: int,
) -> list[dict]:
    """Fetch recent papers from arXiv for the given categories."""
    search_query = "+OR+".join(f"cat:{c}" for c in categories)
    params = {
        "search_query": search_query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": max_results,
    }

    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)

    # Build URL manually — httpx would percent-encode : and + which arXiv requires as literals
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{ARXIV_API_URL}?{qs}"
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            logger.error("arXiv request failed: %s", e)
            return []

    feed = feedparser.parse(resp.text)
    papers = []

    for entry in feed.entries:
        try:
            published_at = datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except (ValueError, AttributeError):
            continue

        if published_at < cutoff:
            continue

        pdf_url = None
        for link in getattr(entry, "links", []):
            if getattr(link, "rel", "") == "related" and getattr(link, "type", "") == "application/pdf":
                pdf_url = link.href
                break

        papers.append({
            "id": entry.id.split("/abs/")[-1],
            "source": "arxiv",
            "title": entry.title.replace("\n", " ").strip(),
            "authors": json.dumps([a.name for a in getattr(entry, "authors", [])]),
            "abstract": entry.summary.replace("\n", " ").strip(),
            "url": entry.link,
            "pdf_url": pdf_url,
            "published_at": published_at,
            "categories": ", ".join(t.term for t in getattr(entry, "tags", [])),
        })

    return papers


async def save_papers(papers: list[dict], db: AsyncSession) -> tuple[int, int]:
    """Insert new papers; skip duplicates. Returns (new_count, skipped_count)."""
    from app.database import Paper

    new_count = 0
    skipped_count = 0

    for paper_data in papers:
        result = await db.execute(
            text("SELECT 1 FROM papers WHERE id = :id"),
            {"id": paper_data["id"]},
        )
        if result.fetchone():
            skipped_count += 1
            continue

        db.add(Paper(**paper_data))
        new_count += 1

    return new_count, skipped_count
