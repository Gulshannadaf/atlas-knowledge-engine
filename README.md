# Atlas - AI Codebase Knowledge Assistant

<p align="center">
  <img src="docs/assets/atlas-logo.png" alt="Atlas Logo" width="120" />
</p>

<p align="center">
  <strong>Upload your codebase. Ask questions. Get answers with citations.</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#development">Development</a> •
  <a href="#deployment">Deployment</a>
</p>

---

## Overview

Atlas is a production-grade RAG (Retrieval-Augmented Generation) system that allows developers to upload repositories, technical documentation, and engineering knowledge bases, then query them using natural language. It combines advanced retrieval techniques with LLM-powered synthesis to provide accurate, cited answers.

### Example Queries

- "How does authentication work in this codebase?"
- "Which services interact with Redis?"
- "Explain the payment flow architecture"
- "What APIs are involved in user registration?"
- "Generate onboarding docs for new developers"

---

## Features

### Core Capabilities

- **Document Ingestion**: Upload PDF, Markdown, TXT, DOCX, and source code files
- **Hybrid Retrieval**: Combines vector search (semantic) with BM25 (keyword) for better results
- **Reranking**: Uses Cohere Rerank for improved relevance scoring
- **Citation Generation**: Every answer includes references to source documents
- **Conversational AI**: Multi-turn conversations with context awareness

### Advanced Features

- **LangGraph Agent**: Tool-using agent for complex queries
- **Evaluation Framework**: RAGAS metrics for measuring RAG quality
- **Cost Tracking**: Per-query token and cost monitoring
- **Observability**: LangSmith tracing, Prometheus metrics, Grafana dashboards

### Enterprise Ready

- **Authentication**: JWT-based authentication with refresh tokens
- **Rate Limiting**: Redis-based rate limiting per user/IP
- **Audit Logging**: Track all user actions
- **Async Processing**: Celery workers for document processing

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Next.js 15)                          │
│   Chat UI  •  Document Upload  •  Evaluation Dashboard  •  Settings     │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           BACKEND (FastAPI)                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │    Auth     │  │  Retrieval  │  │    Agent    │  │  Ingestion  │    │
│  │  Middleware │  │   Service   │  │   Service   │  │   Service   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
          │                  │                  │                │
          ▼                  ▼                  ▼                ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐
│  PostgreSQL  │    │    Qdrant    │    │    Redis     │    │  Celery  │
│   (Primary)  │    │  (Vectors)   │    │   (Cache)    │    │ (Tasks)  │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────┘
```

### Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, Python 3.12, SQLAlchemy, Pydantic |
| AI/ML | LangChain, LangGraph, OpenAI, Cohere Rerank |
| Databases | PostgreSQL, Qdrant, Redis |
| Observability | LangSmith, Prometheus, Grafana |
| Deployment | Docker, GitHub Actions, Railway/Render |

---

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+
- Node.js 20+
- OpenAI API key

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/atlas-knowledge-engine.git
cd atlas-knowledge-engine

# Copy environment file
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` and add your API keys:

```bash
OPENAI_API_KEY=sk-your-key-here
COHERE_API_KEY=your-cohere-key  # Optional, for reranking
LANGSMITH_API_KEY=your-langsmith-key  # Optional, for tracing
```

### 3. Start Services

```bash
# Start all services
cd docker
docker compose up -d

# Check status
docker compose ps
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

---

## Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -e ".[dev]"

# Run development server
uvicorn app.main:app --reload

# Run tests
pytest tests/ -v

# Run linter
ruff check .
ruff format .
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Type check
npm run type-check

# Lint
npm run lint
```

### Database Migrations

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Project Structure

```
atlas-knowledge-engine/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes and middleware
│   │   ├── core/          # Business logic (retrieval, agent, ingestion)
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # External service integrations
│   │   ├── repositories/  # Database operations
│   │   ├── workers/       # Celery tasks
│   │   └── observability/ # Logging, metrics, tracing
│   ├── tests/
│   └── Dockerfile
├── frontend/
│   ├── app/              # Next.js app router pages
│   ├── components/       # React components
│   ├── lib/              # Utilities and API client
│   └── Dockerfile
├── docker/
│   ├── docker-compose.yml
│   └── docker-compose.prod.yml
├── docs/
└── .github/workflows/
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/me` | Get current user |

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/documents/upload` | Upload document |
| GET | `/api/v1/documents` | List documents |
| GET | `/api/v1/documents/{id}` | Get document details |
| DELETE | `/api/v1/documents/{id}` | Delete document |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat` | Send message |
| GET | `/api/v1/chat/conversations` | List conversations |
| GET | `/api/v1/chat/conversations/{id}` | Get conversation |
| DELETE | `/api/v1/chat/conversations/{id}` | Delete conversation |

### Evaluation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/evaluation` | Run evaluation |
| GET | `/api/v1/evaluation` | List evaluations |
| GET | `/api/v1/evaluation/{id}` | Get evaluation results |
| GET | `/api/v1/evaluation/metrics/latest` | Get latest metrics |

---

## Deployment

### Railway

1. Connect your GitHub repository to Railway
2. Add environment variables from `.env.example`
3. Deploy backend and frontend as separate services
4. Add PostgreSQL, Redis, and configure Qdrant Cloud

### Docker Production

```bash
cd docker
docker compose -f docker-compose.prod.yml up -d
```

---

## Development Roadmap

- [x] **Phase 0**: Project setup, Docker, CI/CD
- [ ] **Phase 1**: Basic RAG pipeline
- [ ] **Phase 2**: Hybrid retrieval + reranking
- [ ] **Phase 3**: LangGraph agent with tools
- [ ] **Phase 4**: RAGAS evaluation framework
- [ ] **Phase 5**: Observability (LangSmith, Prometheus)
- [ ] **Phase 6**: Production deployment
- [ ] **Phase 7**: Enterprise features

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [LangChain](https://langchain.com/) - LLM orchestration
- [Qdrant](https://qdrant.tech/) - Vector database
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [Next.js](https://nextjs.org/) - Frontend framework
- [shadcn/ui](https://ui.shadcn.com/) - UI components
