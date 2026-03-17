"""Manual pipeline trigger endpoint."""

from fastapi import APIRouter

from app.models import PipelineRunResponse
from app.services.pipeline import run_pipeline

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/run", response_model=PipelineRunResponse)
async def run_pipeline_endpoint() -> PipelineRunResponse:
    """Manually trigger the scrape → annotate → curate → email pipeline."""
    result = await run_pipeline()
    errors = result.get("errors", [])
    return PipelineRunResponse(
        status="completed",
        papers_scraped=result.get("arxiv_new", 0) + result.get("ss_new", 0),
        papers_annotated=result.get("annotated", 0),
        digest_sent=result.get("email_sent", False),
        error="; ".join(errors) if errors else None,
    )
