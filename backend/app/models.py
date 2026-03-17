"""Pydantic response models for the API. ORM models live in database.py."""

import json
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class DailyCount(BaseModel):
    date: str
    count: int


class StatsResponse(BaseModel):
    total_papers: int
    annotated_count: int
    papers_by_subfield: dict[str, int]
    daily_counts: list[DailyCount]
    total_digests: int


class PipelineRunResponse(BaseModel):
    status: str
    papers_scraped: int
    papers_annotated: int
    digest_sent: bool
    error: str | None = None


class PaperResponse(BaseModel):
    id: str
    source: str
    title: str
    authors: list[str]
    abstract: str
    url: str
    pdf_url: str | None
    published_at: datetime
    categories: str | None
    summary: str | None
    subfield: str | None
    impact_score: float | None
    key_takeaway: str | None
    created_at: datetime
    digest_sent: bool

    @field_validator("authors", mode="before")
    @classmethod
    def parse_authors(cls, v: object) -> list[str]:
        if isinstance(v, str):
            return json.loads(v)
        return v  # type: ignore[return-value]

    model_config = ConfigDict(from_attributes=True)


class DigestResponse(BaseModel):
    id: int
    sent_at: datetime
    paper_count: int
    top_papers: list[str]

    @field_validator("top_papers", mode="before")
    @classmethod
    def parse_top_papers(cls, v: object) -> list[str]:
        if isinstance(v, str):
            return json.loads(v)
        return v  # type: ignore[return-value]

    model_config = ConfigDict(from_attributes=True)
