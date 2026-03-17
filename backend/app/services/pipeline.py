"""Pipeline orchestrator: scrape → annotate → curate → email."""

import json
import logging
from datetime import datetime, timezone

from sqlalchemy import update

from app.agents.curator_agent import curate_papers
from app.agents.digest_agent import annotate_papers
from app.config import settings
from app.database import AsyncSessionLocal, Digest, Paper
from app.scrapers.arxiv_scraper import fetch_arxiv_papers
from app.scrapers.arxiv_scraper import save_papers as arxiv_save
from app.scrapers.semantic_scholar import fetch_semantic_scholar_papers
from app.scrapers.semantic_scholar import save_papers as ss_save
from app.services.email_service import build_digest_html, send_digest_email

logger = logging.getLogger(__name__)


def _parse_recipients(raw: str) -> list[str]:
    return [r.strip() for r in raw.split(",") if r.strip()]


async def _scrape_step(db, s) -> tuple[int, int]:
    """Run both scrapers. Either can fail independently."""
    arxiv_new = 0
    ss_new = 0
    categories = [c.strip() for c in s.arxiv_categories.split(",") if c.strip()]

    try:
        papers = await fetch_arxiv_papers(
            categories=categories,
            days_back=s.days_lookback,
            max_results=s.max_papers_per_run,
        )
        new, _ = await arxiv_save(papers, db)
        arxiv_new = new
        logger.info("arXiv: %d new papers", arxiv_new)
    except Exception as exc:
        logger.warning("arXiv scrape failed: %s", exc)

    try:
        papers = await fetch_semantic_scholar_papers(
            queries=categories,
            days_back=s.days_lookback,
            max_results=s.max_papers_per_run,
            api_key=s.semantic_scholar_api_key,
        )
        new, _ = await ss_save(papers, db)
        ss_new = new
        logger.info("Semantic Scholar: %d new papers", ss_new)
    except Exception as exc:
        logger.warning("Semantic Scholar scrape failed: %s", exc)

    return arxiv_new, ss_new


async def _annotate_step(db, s) -> tuple[int, int]:
    """Annotate unannotated papers. Returns (annotated, skipped)."""
    try:
        annotated, skipped = await annotate_papers(
            db, s.gemini_api_key, batch_size=s.max_papers_per_run
        )
        logger.info("Annotation: %d annotated, %d skipped", annotated, skipped)
        return annotated, skipped
    except Exception as exc:
        logger.warning("Annotation step failed: %s", exc)
        return 0, 0


async def _curate_step(db, s) -> dict:
    """Rank and group annotated papers."""
    result = await curate_papers(db, days_back=s.days_lookback, top_n=10)
    logger.info(
        "Curation: %d top papers from %d annotated",
        len(result["top_papers"]),
        result["total_annotated"],
    )
    return result


async def _save_digest(db, curation_result: dict, email_html: str) -> Digest:
    """Flush (not commit) a new Digest row. Returns the instance."""
    digest = Digest(
        sent_at=datetime.now(timezone.utc),
        paper_count=len(curation_result["top_papers"]),
        email_html=email_html,
        top_papers=json.dumps([p.id for p in curation_result["top_papers"]]),
    )
    db.add(digest)
    await db.flush()
    return digest


async def _mark_papers_sent(db, paper_ids: list[str]) -> None:
    """Bulk-update digest_sent=True for the given paper IDs."""
    await db.execute(
        update(Paper).where(Paper.id.in_(paper_ids)).values(digest_sent=True)
    )


async def run_pipeline() -> dict:
    """Run the full scrape → annotate → curate → email pipeline."""
    result: dict = {
        "arxiv_new": 0,
        "ss_new": 0,
        "annotated": 0,
        "skipped": 0,
        "top_papers": 0,
        "digest_id": None,
        "email_sent": False,
        "errors": [],
    }

    async with AsyncSessionLocal() as db:
        # Step 1: Scrape
        try:
            result["arxiv_new"], result["ss_new"] = await _scrape_step(db, settings)
            await db.commit()
        except Exception as exc:
            result["errors"].append(f"scrape: {exc}")
            logger.error("Scrape step failed: %s", exc)

        # Step 2: Annotate
        result["annotated"], result["skipped"] = await _annotate_step(db, settings)
        await db.commit()

        # Step 3: Curate
        curation = await _curate_step(db, settings)
        top_papers: list[Paper] = curation["top_papers"]
        result["top_papers"] = len(top_papers)

        if not top_papers:
            logger.info("No annotated papers available — skipping email.")
            return result

        # Step 4: Build HTML + save Digest row
        html = build_digest_html(curation)
        digest = await _save_digest(db, curation, html)
        result["digest_id"] = digest.id

        # Step 5: Send email
        recipients = _parse_recipients(settings.digest_recipients)
        if not recipients:
            logger.info("No recipients configured — skipping email send.")
            await db.commit()
            return result

        try:
            await send_digest_email(
                html_body=html,
                recipients=recipients,
                sender_email=settings.my_email,
                app_password=settings.app_password,
            )
            await _mark_papers_sent(db, [p.id for p in top_papers])
            result["email_sent"] = True
        except Exception as exc:
            result["errors"].append(f"email: {exc}")
            logger.error("Email send failed: %s", exc)

        await db.commit()

    logger.info("Pipeline complete: %s", result)
    return result


if __name__ == "__main__":
    import asyncio
    import logging as _logging

    _logging.basicConfig(
        level=_logging.INFO,
        format="%(levelname)s %(name)s — %(message)s",
    )
    print(asyncio.run(run_pipeline()))
