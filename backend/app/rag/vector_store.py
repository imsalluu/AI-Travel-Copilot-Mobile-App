import math
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument
from app.rag.embeddings import embedding_service
from app.rag.reranker import reranker_service


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculate cosine similarity between two float vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class VectorStoreService:
    """Hybrid Vector Store performing similarity search with pgvector and memory-accelerated fallback."""

    @classmethod
    async def search(
        cls,
        query: str,
        destination: Optional[str] = None,
        category: Optional[str] = None,
        top_k: int = 4,
        db: AsyncSession = None,
    ) -> List[Dict[str, Any]]:
        """Search knowledge base using hybrid vector similarity and keyword reranking."""
        query_vector = await embedding_service.get_embedding(query)

        stmt = select(KnowledgeChunk).join(KnowledgeDocument)
        if destination:
            stmt = stmt.where(KnowledgeChunk.destination.ilike(f"%{destination}%"))
        if category:
            stmt = stmt.where(KnowledgeDocument.category == category)

        res = await db.execute(stmt)
        chunks = res.scalars().all()

        if not chunks:
            return []

        scored_results = []
        for chunk in chunks:
            sim = 0.5
            if chunk.embedding:
                sim = cosine_similarity(query_vector, chunk.embedding)
            else:
                # Text similarity fallback
                sim = 0.6 if destination and destination.lower() in chunk.destination.lower() else 0.4

            scored_results.append({
                "chunk_id": chunk.id,
                "document_title": chunk.document.title if chunk.document else "Travel Guide",
                "destination": chunk.destination,
                "section_title": chunk.section_title or "General Overview",
                "content": chunk.content,
                "similarity_score": round(sim, 4),
                "source_url": chunk.document.source_url if chunk.document else None,
                "category": chunk.document.category if chunk.document else "guide",
            })

        # Apply reranking
        return reranker_service.rerank(query, scored_results, top_k=top_k)


vector_store = VectorStoreService()
