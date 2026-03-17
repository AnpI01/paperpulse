"""PaperPulse FastAPI application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routers import digests, papers, pipeline, stats

# Absolute path to the React production build, regardless of working directory.
_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup/shutdown tasks."""
    await init_db()
    yield


app = FastAPI(title="PaperPulse", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.allowed_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(papers.router, prefix="/api")
app.include_router(digests.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(pipeline.router, prefix="/api")


@app.get("/health")
async def health() -> dict:
    """Health check (kept at /health so it doesn't conflict with the SPA)."""
    return {"status": "ok"}


# --- Static file serving (production only) ---
# Activated only when the frontend has been built; dev uses the Vite server.
if _DIST.exists():
    app.mount("/assets", StaticFiles(directory=_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str) -> FileResponse:
        """Catch-all: serve index.html for all non-API routes (SPA routing)."""
        index = _DIST / "index.html"
        return FileResponse(index)
