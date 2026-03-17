# PaperPulse — AI Research Paper Digest

## Project Overview
An AI-powered research paper aggregator. Scrapes arXiv + Semantic Scholar,
uses Gemini to summarize/classify, serves via FastAPI + React dashboard,
and sends daily email digests.

## Tech Stack
- Backend: Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL
- Frontend: React (Vite), Tailwind CSS
- AI: Google Gemini 2.5 Flash via `google-genai`
- Email: Gmail SMTP
- Deployment: Render.com

## Project Structure
- `backend/app/` — FastAPI application
- `backend/app/scrapers/` — arXiv and Semantic Scholar scrapers
- `backend/app/agents/` — Gemini-powered summarization and curation
- `backend/app/services/` — Email and pipeline orchestration
- `backend/app/routers/` — API route handlers
- `frontend/src/` — React dashboard

## Code Style
- Use type hints on all function signatures
- Use async/await for I/O operations (scrapers, DB, API calls)
- Use Pydantic models for all API request/response schemas
- Use environment variables via `python-dotenv`, never hardcode secrets
- Keep functions small (<30 lines), one responsibility each
- Use descriptive variable names, add docstrings to all public functions

## Commands
- `cd backend && uvicorn app.main:app --reload` — Run backend
- `cd frontend && npm run dev` — Run frontend
- `cd backend && python -m app.services.pipeline` — Run pipeline manually
- `pip install -r requirements.txt` — Install Python deps
- `cd frontend && npm install` — Install frontend deps

## Key Constraints
- Gemini free tier: max 250 requests/day, 10 RPM — batch and rate-limit calls
- arXiv API: max 1 request per 3 seconds
- Semantic Scholar: 10 req/sec without key, 100 req/sec with key
- Keep all API calls wrapped in try/except with retries
- Use SQLite for local dev, PostgreSQL for production (via DATABASE_URL)

## Do NOT
- Hardcode any API keys or secrets
- Make changes to files not related to the current task
- Skip error handling on external API calls
- Generate overly verbose comments — keep them concise
