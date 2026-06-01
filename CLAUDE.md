# Atlas - AI Codebase Knowledge Assistant

## Project Overview

Atlas is a production-grade RAG (Retrieval-Augmented Generation) system for querying codebases and documentation. It combines hybrid retrieval, LLM-powered synthesis, and agent capabilities.

## Tech Stack

- **Backend**: FastAPI, Python 3.12, SQLAlchemy, Pydantic
- **Frontend**: Next.js 15, TypeScript, Tailwind CSS, shadcn/ui
- **AI/ML**: LangChain, LangGraph, OpenAI, Cohere
- **Databases**: PostgreSQL (primary), Qdrant (vectors), Redis (cache/queue)
- **Observability**: LangSmith, Prometheus, Grafana

## Project Structure

```
backend/app/
├── api/routes/       # FastAPI endpoints
├── api/middleware/   # Auth, rate limiting, logging
├── core/             # Business logic (retrieval, agent, ingestion)
├── models/           # SQLAlchemy ORM models
├── schemas/          # Pydantic request/response schemas
├── services/         # External service integrations
├── repositories/     # Database operations
├── workers/          # Celery background tasks
└── observability/    # Logging and metrics

frontend/app/
├── auth/            # Login/signup pages
├── dashboard/       # Main application pages
└── components/      # React components
```

## Development Commands

```bash
# Start services
cd docker && docker compose up -d

# Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
pytest tests/ -v

# Frontend
cd frontend
npm run dev
npm run lint
```

## Key Files

- `backend/app/main.py` - FastAPI application entry
- `backend/app/config.py` - Environment configuration
- `backend/app/models/database.py` - All database models
- `backend/app/api/routes/` - API endpoints
- `frontend/app/dashboard/` - Main UI pages

## Development Phases

- **Phase 0** (Current): Project setup, Docker, CI/CD
- **Phase 1**: Basic RAG pipeline (ingestion, retrieval, generation)
- **Phase 2**: Hybrid search + reranking
- **Phase 3**: LangGraph agent with tools
- **Phase 4**: RAGAS evaluation framework
- **Phase 5**: Observability (LangSmith, Prometheus)

## Architecture Decisions

1. **Modular Monolith**: Single deployable unit with clear module boundaries
2. **Repository Pattern**: Separate database logic from business logic
3. **Async First**: All database operations are async
4. **JWT Auth**: Short-lived access tokens (15min), long-lived refresh tokens (7d)

## Environment Variables

See `.env.example` for all configuration options. Critical ones:
- `OPENAI_API_KEY` - Required for embeddings and chat
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key (min 32 chars)
