from typing import List, Dict, Any


class RerankerService:
    """Reranker service for boosting retrieval precision using BM25 keyword matching and query relevance."""

    @staticmethod
    def rerank(
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """Rerank retrieved document chunks by combining semantic vector score with exact keyword density."""
        if not results:
            return []

        query_terms = set(query.lower().split())

        scored_items = []
        for item in results:
            content = item.get("content", "").lower()
            title = (item.get("document_title", "") + " " + item.get("section_title", "")).lower()
            
            # Base semantic vector score
            base_score = item.get("similarity_score", 0.5)

            # Keyword matching bonus
            term_matches = sum(1 for term in query_terms if term in content)
            title_matches = sum(2 for term in query_terms if term in title)
            keyword_ratio = (term_matches + title_matches) / max(len(query_terms), 1)

            # Combined hybrid score (70% semantic, 30% keyword match)
            final_score = (base_score * 0.70) + (min(keyword_ratio, 1.0) * 0.30)

            scored_items.append({
                **item,
                "similarity_score": round(final_score, 4),
            })

        # Sort descending by final score
        scored_items.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_items[:top_k]


reranker_service = RerankerService()
