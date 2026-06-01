"""Qdrant vector database service."""

from functools import lru_cache

import structlog
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

from app.config import settings

logger = structlog.get_logger()


@lru_cache
def get_qdrant_client() -> QdrantClient:
    """Get cached Qdrant client instance."""
    return QdrantClient(
        host=settings.qdrant_host,
        port=settings.qdrant_port,
    )


async def init_qdrant() -> None:
    """Initialize Qdrant collection if it doesn't exist."""
    client = get_qdrant_client()

    collections = client.get_collections()
    collection_names = [c.name for c in collections.collections]

    if settings.qdrant_collection not in collection_names:
        logger.info(
            "Creating Qdrant collection",
            collection=settings.qdrant_collection,
            vector_size=settings.qdrant_vector_size,
        )

        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=qdrant_models.VectorParams(
                size=settings.qdrant_vector_size,
                distance=qdrant_models.Distance.COSINE,
            ),
        )

        # Create payload indexes for filtering
        client.create_payload_index(
            collection_name=settings.qdrant_collection,
            field_name="user_id",
            field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
        )

        client.create_payload_index(
            collection_name=settings.qdrant_collection,
            field_name="document_id",
            field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
        )

        logger.info("Qdrant collection created")
    else:
        logger.info("Qdrant collection already exists", collection=settings.qdrant_collection)


async def delete_vectors_by_document(document_id: str) -> None:
    """Delete all vectors associated with a document."""
    client = get_qdrant_client()

    client.delete(
        collection_name=settings.qdrant_collection,
        points_selector=qdrant_models.FilterSelector(
            filter=qdrant_models.Filter(
                must=[
                    qdrant_models.FieldCondition(
                        key="document_id",
                        match=qdrant_models.MatchValue(value=document_id),
                    )
                ]
            )
        ),
    )

    logger.info("Vectors deleted for document", document_id=document_id)
