import hashlib
import math
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from config import settings


VECTOR_SIZE = 64


def get_client() -> QdrantClient:
    return QdrantClient(url=settings.QDRANT_URL)


def text_to_vector(text: str) -> list[float]:
    vector = [0.0] * VECTOR_SIZE
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = digest[0] % VECTOR_SIZE
        weight = 1.0 if digest[1] % 2 == 0 else -1.0
        vector[index] += weight

    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def ensure_collection(client: QdrantClient | None = None) -> None:
    client = client or get_client()
    if client.collection_exists(settings.QDRANT_COLLECTION):
        return
    client.create_collection(
        collection_name=settings.QDRANT_COLLECTION,
        vectors_config=qmodels.VectorParams(size=VECTOR_SIZE, distance=qmodels.Distance.COSINE),
    )


def upsert_article(article) -> str | None:
    client = get_client()
    ensure_collection(client)
    point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, article.id))
    text = f"{article.title}\n{article.content or ''}"
    client.upsert(
        collection_name=settings.QDRANT_COLLECTION,
        points=[
            qmodels.PointStruct(
                id=point_id,
                vector=text_to_vector(text),
                payload={
                    "article_id": article.id,
                    "politician_id": article.politician_id,
                    "title": article.title,
                    "source": article.source,
                    "source_owner": article.source_owner,
                    "url": article.url,
                    "published_at": article.published_at.isoformat() if article.published_at else None,
                    "consensus_valid": article.consensus_valid,
                },
            )
        ],
    )
    return point_id


def search_evidence(query: str, limit: int = 5) -> list[dict]:
    client = get_client()
    ensure_collection(client)
    try:
        hits = client.search(
            collection_name=settings.QDRANT_COLLECTION,
            query_vector=text_to_vector(query),
            limit=limit,
        )
    except AttributeError:
        hits = client.query_points(
            collection_name=settings.QDRANT_COLLECTION,
            query=text_to_vector(query),
            limit=limit,
        ).points

    return [
        {
            "score": hit.score,
            "payload": hit.payload,
        }
        for hit in hits
    ]
