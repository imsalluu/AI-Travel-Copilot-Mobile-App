from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User
from app.schemas.knowledge import DocumentCreate, KnowledgeSearchResult, KnowledgeQuery
from app.rag.ingestion import ingestion_pipeline
from app.rag.vector_store import vector_store
from app.api.deps import get_current_user, get_current_active_superuser

router = APIRouter()


@router.post("/search", response_model=List[KnowledgeSearchResult])
async def search_knowledge_base(
    query_in: KnowledgeQuery,
    db: AsyncSession = Depends(get_db),
):
    """Hybrid semantic vector + keyword search over grounded destination knowledge base."""
    # Ensure seed documents are present
    await ingestion_pipeline.seed_curated_destination_knowledge(db)

    results = await vector_store.search(
        query=query_in.query,
        destination=query_in.destination,
        category=query_in.category,
        top_k=query_in.top_k,
        db=db,
    )
    return [KnowledgeSearchResult(**r) for r in results]


@router.post("/documents", status_code=status.HTTP_201_CREATED)
async def ingest_document(
    doc_in: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Ingest a new travel guide into the vector store."""
    doc = await ingestion_pipeline.ingest_document(doc_in, db)
    return {"status": "success", "document_id": doc.id, "chunks_indexed": doc.chunk_count}
