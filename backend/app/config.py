"""
Application configuration using Pydantic Settings.

Loads configuration from environment variables with sensible defaults.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==========================================================================
    # Application
    # ==========================================================================
    app_name: str = "Atlas"
    app_version: str = "0.1.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    secret_key: str = Field(default="change-me-in-production", min_length=32)

    # ==========================================================================
    # Server
    # ==========================================================================
    host: str = "0.0.0.0"
    port: int = 8000
    allowed_origins: list[str] = Field(default=["http://localhost:3000"])

    # ==========================================================================
    # Database (PostgreSQL)
    # ==========================================================================
    database_url: str = Field(default="postgresql://atlas:atlas_secret@localhost:5432/atlas")
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30

    # ==========================================================================
    # Redis
    # ==========================================================================
    redis_url: str = "redis://localhost:6379/0"
    redis_prefix: str = "atlas:"

    # ==========================================================================
    # Qdrant (Vector Database)
    # ==========================================================================
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "atlas_documents"
    qdrant_vector_size: int = 1536  # OpenAI text-embedding-3-small

    # ==========================================================================
    # OpenAI
    # ==========================================================================
    openai_api_key: str = Field(default="")
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"
    openai_timeout: int = 60

    # ==========================================================================
    # Cohere (Reranking)
    # ==========================================================================
    cohere_api_key: str = Field(default="")
    cohere_rerank_model: str = "rerank-english-v3.0"

    # ==========================================================================
    # LangSmith (Observability)
    # ==========================================================================
    langsmith_api_key: str = Field(default="")
    langsmith_project: str = "atlas"
    langsmith_tracing: bool = True

    # ==========================================================================
    # RAG Configuration
    # ==========================================================================
    chunk_size: int = 512
    chunk_overlap: int = 50
    retrieval_top_k: int = 20
    rerank_top_k: int = 5

    # ==========================================================================
    # Rate Limiting
    # ==========================================================================
    rate_limit_requests_per_minute: int = 60
    rate_limit_requests_per_hour: int = 1000

    # ==========================================================================
    # Authentication
    # ==========================================================================
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # ==========================================================================
    # File Upload
    # ==========================================================================
    upload_dir: str = "uploads"
    max_upload_size_mb: int = 50
    allowed_file_types: list[str] = Field(
        default=[".pdf", ".md", ".txt", ".docx", ".py", ".js", ".ts", ".java", ".go", ".rs"]
    )

    # ==========================================================================
    # Computed Properties
    # ==========================================================================
    @computed_field
    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @computed_field
    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export singleton instance
settings = get_settings()
