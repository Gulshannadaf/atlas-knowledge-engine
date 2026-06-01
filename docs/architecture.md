# Atlas Architecture

## Overview

Atlas is designed as a modular monolith with clear separation of concerns. This document outlines the system architecture, data flows, and key design decisions.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                  CLIENT LAYER                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                 │
│  │   Web Browser   │  │   API Client    │  │    CLI Tool     │                 │
│  │   (Next.js)     │  │   (SDK)         │  │   (Future)      │                 │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY (FastAPI)                               │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐    │
│  │    Auth    │ │   Rate     │ │  Logging   │ │   Error    │ │  Request   │    │
│  │ Middleware │ │  Limiter   │ │ Middleware │ │  Handler   │ │    ID      │    │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘ └────────────┘    │
│                                                                                  │
│  Routes: /auth  /documents  /chat  /evaluation  /health  /metrics               │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                ┌─────────────────────┼─────────────────────┐
                ▼                     ▼                     ▼
┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────┐
│   RETRIEVAL MODULE    │ │    AGENT MODULE       │ │   INGESTION MODULE    │
│                       │ │                       │ │                       │
│ • Vector Search       │ │ • LangGraph State     │ │ • Document Parser     │
│ • BM25 Search         │ │ • Tool Registry       │ │ • Text Chunker        │
│ • Hybrid Fusion (RRF) │ │ • Retrieval Tool      │ │ • Embedding Generator │
│ • Cohere Reranker     │ │ • Web Search Tool     │ │ • Vector Indexer      │
│ • Citation Builder    │ │ • Calculator Tool     │ │                       │
└───────────────────────┘ └───────────────────────┘ └───────────────────────┘
                │                     │                     │
                └─────────────────────┼─────────────────────┘
                                      │
                ┌─────────────────────┼─────────────────────┐
                ▼                     ▼                     ▼
┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────┐
│     PostgreSQL        │ │       Qdrant          │ │        Redis          │
│                       │ │                       │ │                       │
│ • Users               │ │ • Document Vectors    │ │ • Session Cache       │
│ • Documents           │ │ • Payload Metadata    │ │ • Rate Limits         │
│ • Conversations       │ │                       │ │ • Task Queue          │
│ • Messages            │ │                       │ │ • BM25 Index          │
│ • Evaluations         │ │                       │ │                       │
└───────────────────────┘ └───────────────────────┘ └───────────────────────┘
```

## Data Flows

### Document Ingestion Flow

```
Upload Request
      │
      ▼
┌─────────────────┐
│ Validate File   │ ─── Reject if invalid
│ (type, size)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Store File      │
│ Create Record   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Queue Task      │ ─── Celery + Redis
│ Return 202      │
└────────┬────────┘
         │
         ▼ (Async Worker)
┌─────────────────┐
│ Parse Document  │ ─── unstructured library
│ Extract Text    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Chunk Text      │ ─── 512 tokens, 50 overlap
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate        │ ─── OpenAI text-embedding-3-small
│ Embeddings      │
└────────┬────────┘
         │
         ├──────────────────┐
         ▼                  ▼
┌─────────────────┐ ┌─────────────────┐
│ Store Vectors   │ │ Build BM25      │
│ (Qdrant)        │ │ Index (Redis)   │
└────────┬────────┘ └────────┬────────┘
         │                   │
         └─────────┬─────────┘
                   ▼
         ┌─────────────────┐
         │ Update Status   │
         │ (Completed)     │
         └─────────────────┘
```

### Query Processing Flow

```
User Query
      │
      ▼
┌─────────────────┐
│ Route Decision  │ ─── Does query need retrieval?
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
  Yes        No
    │         │
    │         └──► Direct LLM Response
    ▼
┌─────────────────┐
│ Hybrid Search   │
│ Vector + BM25   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ RRF Fusion      │ ─── Combine scores
│ (top 20)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Rerank          │ ─── Cohere Rerank
│ (top 5)         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Build Context   │ ─── Format for LLM
│ Add Citations   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate        │ ─── GPT-4o-mini
│ Response        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Stream to User  │ ─── SSE
│ Store Message   │
└─────────────────┘
```

## Module Details

### Retrieval Module

The retrieval module implements a hybrid search strategy:

1. **Vector Search**: Semantic similarity using Qdrant
2. **BM25 Search**: Keyword matching using rank_bm25
3. **Fusion**: Reciprocal Rank Fusion (RRF) combines results
4. **Reranking**: Cohere Rerank for final ordering

### Agent Module

Built with LangGraph for explicit state management:

- **States**: analyze, retrieve, search_web, generate, cite
- **Tools**: Knowledge search, web search, calculator
- **Control**: Conditional edges based on query classification

### Ingestion Module

Handles document processing pipeline:

- **Parser**: unstructured library for multi-format support
- **Chunker**: Token-based with configurable size/overlap
- **Embedder**: OpenAI embeddings with batching

## Database Schema

See [database.md](./database.md) for detailed schema documentation.

## Security Considerations

- JWT tokens with short expiry (15 min access, 7 day refresh)
- Bcrypt password hashing (cost factor 12)
- Rate limiting per user and IP
- Input validation via Pydantic
- SQL injection prevention via SQLAlchemy ORM

## Scalability

Current design supports horizontal scaling:

- **Backend**: Stateless, can run multiple instances
- **Celery Workers**: Scale independently
- **Qdrant**: Supports sharding
- **Redis**: Can use Redis Cluster
- **PostgreSQL**: Read replicas for scaling reads
