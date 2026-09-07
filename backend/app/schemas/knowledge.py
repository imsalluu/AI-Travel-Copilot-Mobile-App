from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    title: str
    destination: str
    category: str = "guide"
    source_type: str = "curated"
    source_url: Optional[str] = None
    author: Optional[str] = None
    content: str
    doc_metadata: Optional[Dict[str, Any]] = None


class KnowledgeSearchResult(BaseModel):
    chunk_id: str
    document_title: str
    destination: str
    section_title: Optional[str] = None
    content: str
    similarity_score: float
    source_url: Optional[str] = None
    category: str = "guide"


class KnowledgeQuery(BaseModel):
    query: str
    destination: Optional[str] = None
    category: Optional[str] = None
    top_k: int = 4
