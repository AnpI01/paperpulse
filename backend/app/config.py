"""Application configuration loaded from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration values read from .env or environment."""

    database_url: str = "sqlite+aiosqlite:///./paperpulse.db"

    gemini_api_key: str = ""
    semantic_scholar_api_key: str = ""

    my_email: str = ""
    app_password: str = ""
    digest_recipients: str = ""

    allowed_origins: str = "http://localhost:5173"

    arxiv_categories: str = "cs.CL,cs.AI,cs.LG,cs.CV,cs.RO"
    max_papers_per_run: int = 50
    days_lookback: int = 1

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
