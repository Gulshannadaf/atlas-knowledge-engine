# Atlas API Documentation

## Overview

Atlas provides a RESTful API for document management, chat, and evaluation. All API endpoints are prefixed with `/api/v1`.

## Authentication

Atlas uses JWT (JSON Web Token) authentication.

### Obtaining Tokens

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### Using Tokens

Include the access token in the Authorization header:

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJ..."
```

### Refreshing Tokens

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJ..."}'
```

---

## Endpoints

### Health

#### GET /health

Check system health.

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development",
  "services": {
    "postgres": {"status": "healthy"},
    "redis": {"status": "healthy"},
    "qdrant": {"status": "healthy"}
  }
}
```

---

### Documents

#### POST /api/v1/documents/upload

Upload a document for processing.

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@document.pdf"
```

Response (202 Accepted):
```json
{
  "id": "uuid",
  "filename": "document.pdf",
  "status": "pending",
  "message": "Document queued for processing"
}
```

#### GET /api/v1/documents

List all documents.

```bash
curl http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer TOKEN"
```

Query Parameters:
- `status_filter`: Filter by status (pending, processing, completed, failed)
- `limit`: Max results (default: 50)
- `offset`: Pagination offset (default: 0)

Response:
```json
{
  "documents": [
    {
      "id": "uuid",
      "filename": "document.pdf",
      "file_type": "pdf",
      "file_size": 1024000,
      "status": "completed",
      "chunk_count": 42,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

#### GET /api/v1/documents/{id}

Get document details.

#### DELETE /api/v1/documents/{id}

Delete a document.

---

### Chat

#### POST /api/v1/chat

Send a message and receive a response.

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How does authentication work?",
    "conversation_id": null,
    "include_sources": true,
    "stream": false
  }'
```

Response:
```json
{
  "conversation_id": "uuid",
  "message_id": "uuid",
  "content": "Authentication in this codebase uses JWT tokens...",
  "citations": [
    {
      "document_id": "uuid",
      "document_name": "auth.py",
      "chunk_id": "uuid",
      "content": "def verify_token(token: str)...",
      "relevance_score": 0.95
    }
  ],
  "token_count": 150,
  "latency_ms": 1234
}
```

#### Streaming Response

Set `stream: true` to receive a Server-Sent Events stream:

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "...", "stream": true}'
```

Response (SSE):
```
data: {"content": "Auth", "done": false}
data: {"content": "entication", "done": false}
data: {"content": " works", "done": false}
...
data: {"content": "", "done": true, "citations": [...]}
data: [DONE]
```

#### GET /api/v1/chat/conversations

List conversations.

#### GET /api/v1/chat/conversations/{id}

Get conversation with messages.

#### DELETE /api/v1/chat/conversations/{id}

Delete a conversation.

---

### Evaluation

#### POST /api/v1/evaluation

Create and run an evaluation.

```bash
curl -X POST http://localhost:8000/api/v1/evaluation \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weekly Evaluation",
    "description": "Evaluation of RAG quality"
  }'
```

Response (202 Accepted):
```json
{
  "id": "uuid",
  "name": "Weekly Evaluation",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### GET /api/v1/evaluation

List evaluations.

#### GET /api/v1/evaluation/{id}

Get evaluation details.

#### GET /api/v1/evaluation/{id}/results

Get evaluation results.

#### GET /api/v1/evaluation/metrics/latest

Get metrics from the latest completed evaluation.

Response:
```json
{
  "context_precision": 0.85,
  "context_recall": 0.78,
  "faithfulness": 0.92,
  "answer_relevancy": 0.88,
  "total_queries": 50,
  "average_latency_ms": 1500,
  "average_cost_usd": 0.012
}
```

---

## Error Responses

All errors return a consistent format:

```json
{
  "detail": "Error message here",
  "code": "ERROR_CODE"
}
```

Common status codes:
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error

---

## Rate Limiting

- Authenticated users: 60 requests/minute
- Unauthenticated: 10 requests/minute

Rate limit headers:
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp
