import math
import hashlib
from typing import List
import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Embedding generator with multi-provider support and deterministic fallback."""

    def __init__(self, dimension: int = 1536):
        self.dimension = dimension

    async def get_embedding(self, text: str) -> List[float]:
        """Compute normalized dense vector for input text."""
        cleaned = text.strip()
        if not cleaned:
            return [0.0] * self.dimension

        # If OpenAI API key is configured and provider is openai
        if settings.OPENAI_API_KEY and settings.EMBEDDING_PROVIDER == "openai":
            try:
                async with httpx.AsyncClient(timeout=8.0) as client:
                    resp = await client.post(
                        "https://api.openai.com/v1/embeddings",
                        headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                        json={"input": cleaned, "model": settings.EMBEDDING_MODEL},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["data"][0]["embedding"]
            except Exception as e:
                logger.warning(f"OpenAI embedding error, falling back to local dense vector: {e}")

        # High-entropy deterministic dense vector representation for local RAG
        return self._generate_dense_vector(cleaned)

    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Compute embeddings for a batch of strings."""
        return [await self.get_embedding(t) for t in texts]

    def _generate_dense_vector(self, text: str) -> List[float]:
        """Generate high-dimension deterministic pseudo-semantic vector using word hashing."""
        words = text.lower().split()
        vector = [0.0] * self.dimension

        for word in words:
            # Hash word into bucket indices
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            for i in range(4):
                idx = (h + i * 37) % self.dimension
                val = (((h >> (i * 8)) & 0xFF) / 255.0) - 0.5
                vector[idx] += val

        # Normalize vector to unit length (L2 norm)
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [round(x / norm, 6) for x in vector]
        return vector


embedding_service = EmbeddingService()
