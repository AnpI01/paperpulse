"""Gemini-powered annotation agent: summary, subfield, impact score, key takeaway."""

import asyncio
import json
import logging
from typing import Optional

from google import genai
from google.genai import types
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Paper

logger = logging.getLogger(__name__)

SUBFIELDS = [
    "NLP", "LLM", "CV", "RL", "Robotics",
    "Graph ML", "Time Series", "Multimodal", "AI Safety", "Other"
]

PROMPT_TEMPLATE = """Analyse this research paper and respond with a JSON object containing exactly these keys:
- "summary": 2-3 sentence plain-English summary aimed at a technical but non-specialist reader
- "subfield": one of {subfields} — pick the closest match
- "impact_score": integer 1-10 (10 = landmark result, 1 = incremental/low relevance)
- "key_takeaway": one punchy sentence (≤20 words) capturing the core contribution

Title: {title}
Abstract: {abstract}"""


def get_gemini_client(api_key: str) -> genai.Client:
    """Initialise and return a Gemini client."""
    return genai.Client(api_key=api_key)


async def annotate_paper(
    paper: Paper,
    client: genai.Client,
) -> Optional[dict]:
    """Call Gemini once for a single paper. Returns parsed annotation dict or None on error."""
    prompt = PROMPT_TEMPLATE.format(
        subfields=SUBFIELDS,
        title=paper.title,
        abstract=paper.abstract or "",
    )
    try:
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        annotation = json.loads(response.text)

        # Validate and normalise fields
        if annotation.get("subfield") not in SUBFIELDS:
            annotation["subfield"] = "Other"

        score = annotation.get("impact_score")
        try:
            annotation["impact_score"] = max(1, min(10, int(score)))
        except (TypeError, ValueError):
            annotation["impact_score"] = 5

        return annotation
    except Exception as exc:
        logger.warning("Failed to annotate paper %s: %s", paper.id, exc)
        return None


async def annotate_papers(
    db: AsyncSession,
    api_key: str,
    batch_size: int = 50,
) -> tuple[int, int]:
    """Annotate unannotated papers in DB. Returns (annotated, skipped)."""
    result = await db.execute(
        select(Paper).where(Paper.summary.is_(None)).limit(batch_size)
    )
    papers = result.scalars().all()

    annotated = 0
    skipped = 0

    for i, paper in enumerate(papers):
        annotation = await annotate_paper(paper, get_gemini_client(api_key))

        if annotation is None:
            skipped += 1
        else:
            await db.execute(
                update(Paper)
                .where(Paper.id == paper.id)
                .values(
                    summary=annotation.get("summary"),
                    subfield=annotation.get("subfield"),
                    impact_score=annotation.get("impact_score"),
                    key_takeaway=annotation.get("key_takeaway"),
                )
            )
            annotated += 1

        # Commit every 10 papers to limit data loss on interruption
        if (i + 1) % 10 == 0:
            await db.commit()

        # Rate limit: ≤10 RPM on free tier
        await asyncio.sleep(6)

    await db.commit()
    return annotated, skipped
