import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.rag.ingestion import ingestion_pipeline
from app.rag.vector_store import vector_store
from app.rag.embeddings import embedding_service
from app.schemas.knowledge import DocumentCreate


@pytest.mark.asyncio
async def test_rag_pipeline(db_session: AsyncSession):
    # 1. Test Dense Vector Generation
    emb = await embedding_service.get_embedding("Cox's Bazar beach and coastal weather")
    assert len(emb) == 1536

    # 2. Ingest document
    doc_in = DocumentCreate(
        title="Custom Saint Martin Travel Guide",
        destination="Saint Martin",
        category="guide",
        content="Saint Martin is the only coral island in Bangladesh. Chera Dwip is the southernmost tip accessible by boat during low tide. Local law strictly forbids carrying live coral or sea shells away from the island.",
    )
    doc = await ingestion_pipeline.ingest_document(doc_in, db_session)
    assert doc.chunk_count >= 1

    # 3. Vector Hybrid Search
    results = await vector_store.search(
        query="coral rules in Saint Martin",
        destination="Saint Martin",
        db=db_session,
    )
    assert len(results) > 0
    assert "coral" in results[0]["content"].lower()
    assert results[0]["destination"] == "Saint Martin"
