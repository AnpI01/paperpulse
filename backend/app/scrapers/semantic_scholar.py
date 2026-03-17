"""Semantic Scholar REST scraper."""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

SS_API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
SS_FIELDS = "paperId,title,authors,abstract,year,url,openAccessPdf,publicationDate,fieldsOfStudy"


async def fetch_semantic_scholar_papers(
    queries: list[str],
    days_back: int,
    max_results: int,
    api_key: str = "",
) -> list[dict]:
    """Fetch papers from Semantic Scholar for the given search queries."""
    headers = {"x-api-key": api_key} if api_key else {}
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    current_year = datetime.now(timezone.utc).year
    papers: list[dict] = []

    async with httpx.AsyncClient(timeout=30) as client:
        for query in queries:
            params = {
                "query": query,
                "fields": SS_FIELDS,
                "limit": max_results,
            }

            try:
                resp = await _get_with_retry(client, SS_API_URL, params, headers)
            except httpx.HTTPError as e:
                logger.error("Semantic Scholar request failed for query '%s': %s", query, e)
                await asyncio.sleep(0.1)
                continue

            data = resp.json()

            for paper in data.get("data", []):
                pub_date_str = paper.get("publicationDate")
                if pub_date_str:
                    try:
                        pub_date = datetime.strptime(pub_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                    except ValueError:
                        pub_date = None
                else:
                    pub_date = None

                # Date filter: use publicationDate if available, else fall back to year
                if pub_date is not None:
                    if pub_date < cutoff:
                        continue
                elif paper.get("year") != current_year:
                    continue

                abstract = paper.get("abstract") or ""
                if not abstract:
                    continue

                papers.append({
                    "id": "ss_" + paper["paperId"],
                    "source": "semantic_scholar",
                    "title": paper.get("title", "").strip(),
                    "authors": json.dumps([a["name"] for a in paper.get("authors", [])]),
                    "abstract": abstract,
                    "url": paper.get("url") or f"https://www.semanticscholar.org/paper/{paper['paperId']}",
                    "pdf_url": (paper.get("openAccessPdf") or {}).get("url"),
                    "published_at": pub_date or datetime(current_year, 1, 1, tzinfo=timezone.utc),
                    "categories": ", ".join(paper.get("fieldsOfStudy") or []),
                })

            await asyncio.sleep(0.1)

    return papers


async def _get_with_retry(
    client: httpx.AsyncClient,
    url: str,
    params: dict,
    headers: dict,
) -> httpx.Response:
    """GET with one retry on HTTP errors."""
    try:
        resp = await client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        return resp
    except httpx.HTTPStatusError:
        await asyncio.sleep(1)
        resp = await client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        return resp


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
