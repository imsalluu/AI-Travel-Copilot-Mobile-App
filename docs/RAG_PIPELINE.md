# 📚 Grounded Travel Destination RAG Pipeline

## Architecture Overview

```mermaid
graph TD
    RawDoc[Destination Guide Document] --> Parser[Text Ingestion & Parsing]
    Parser --> Chunker[Chunking: 600 chars with 100 overlap]
    Chunker --> Embedder[Embedding Generator: 1536-dim Dense Vector]
    Embedder --> VectorDB[(PostgreSQL + pgvector)]
    
    Query[User Chat / Search Query] --> QEmbed[Query Embedding]
    QEmbed --> CosineSearch[pgvector Cosine Similarity Search]
    Query --> KeywordSearch[BM25 Exact Keyword Density Search]
    
    CosineSearch --> HybridRank[Hybrid Fusion: 70% Semantic + 30% Keyword]
    KeywordSearch --> HybridRank
    
    HybridRank --> Reranker[Cross-Scorer Reranking Top-K]
    Reranker --> GroundedPrompt[Context-Augmented LLM Prompt]
    GroundedPrompt --> FactCheckedOutput[Verified Structured Response]
```

## Features
- **Chunking**: Overlapping chunk strategy preserves context around boundaries and headings.
- **pgvector Cosine Index**: High-performance semantic indexing with fast vector distance calculations.
- **Hybrid Fusion**: Combines vector cosine similarity with exact keyword matching density to eliminate hallucinations on proper nouns, pricing, and locations.
- **Source Citations**: Every retrieved fact attaches document metadata, section titles, and source URLs.
