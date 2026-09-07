from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.knowledge import KnowledgeDocument, KnowledgeChunk
from app.rag.embeddings import embedding_service
from app.schemas.knowledge import DocumentCreate
import logging

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Document Ingestion Pipeline: Parse -> Clean -> Chunk -> Embed -> Save."""

    CHUNK_SIZE = 600  # characters per chunk
    CHUNK_OVERLAP = 100

    @classmethod
    def chunk_text(cls, text: str) -> List[str]:
        """Split text into overlapping character chunks preserving sentence boundaries."""
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""

        for p in paragraphs:
            cleaned_p = p.strip()
            if not cleaned_p:
                continue

            if len(current_chunk) + len(cleaned_p) < cls.CHUNK_SIZE:
                current_chunk += ("\n\n" if current_chunk else "") + cleaned_p
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = cleaned_p

        if current_chunk:
            chunks.append(current_chunk)

        return chunks if chunks else [text]

    @classmethod
    async def ingest_document(cls, doc_in: DocumentCreate, db: AsyncSession) -> KnowledgeDocument:
        """Process and index a knowledge document with vector embeddings."""
        doc = KnowledgeDocument(
            title=doc_in.title,
            destination=doc_in.destination,
            category=doc_in.category,
            source_type=doc_in.source_type,
            source_url=doc_in.source_url,
            author=doc_in.author or "Travel Editorial",
            content=doc_in.content,
            doc_metadata=doc_in.doc_metadata or {},
        )
        db.add(doc)
        await db.flush()

        chunks_text = cls.chunk_text(doc_in.content)
        doc.chunk_count = len(chunks_text)

        for idx, text in enumerate(chunks_text):
            embedding = await embedding_service.get_embedding(text)
            chunk = KnowledgeChunk(
                document_id=doc.id,
                chunk_index=idx,
                content=text,
                destination=doc.destination,
                section_title=f"{doc.title} - Part {idx + 1}",
                embedding=embedding,
                token_count=len(text.split()),
                meta_info={"category": doc.category, "source": doc.source_type},
            )
            db.add(chunk)

        await db.commit()
        await db.refresh(doc)
        return doc

    @classmethod
    async def seed_curated_destination_knowledge(cls, db: AsyncSession):
        """Seed rich travel knowledge guides for key tourist destinations."""
        stmt = select(KnowledgeDocument)
        res = await db.execute(stmt)
        if res.first():
            return  # Already seeded

        guides = [
            DocumentCreate(
                title="Cox's Bazar Complete Travel & Safety Guide",
                destination="Cox's Bazar",
                category="guide",
                content="""Cox's Bazar is home to the world's longest unbroken natural sea beach, extending 120 km. 
Local Rules & Customs: Dress moderately in public bazaar areas. Modest swimwear is recommended on public beaches like Laboni. 
Transportation: Green CNG auto-rickshaws, Chander Gari (open jeeps), and TomToms (battery-run electric rickshaws) are the main local transport. The Marine Drive is best experienced by hiring a Chander Gari.
Safety & Emergencies: Tourist Police Bangladesh maintains 24/7 patrol booths along Laboni, Sugandha, and Kolatoli beaches. Lifeguards (Sea Safe) are stationed at designated flags. Always obey red danger flags during rough high tides.
Best Seafood Spots: Visit Jhaubon, Casablanca, and Poushee for authentic Rupchanda, Loitta fry, and dried fish (Shutki) vhorta delicacies.
Best Sunset: Laboni Beach Point and Inani Coral Beach provide majestic views between 5:15 PM and 6:00 PM.""",
            ),
            DocumentCreate(
                title="Sylhet Nature, Tea Estates & Swamp Forest Guide",
                destination="Sylhet",
                category="guide",
                content="""Sylhet offers lush rainforests, cascading rivers from Meghalaya, and expansive tea gardens.
Ratargul Swamp Forest: Visit in the early morning for quiet wooden boat rides through freshwater submerged Hijol and Koroch trees.
Bisnakandi & Jaflong: Known for crystal-clear cold mountain water flowing over millions of smooth river pebbles. Boat rides cost approximately 800 - 1500 BDT depending on group size.
Culinary Highlights: Don't miss Panshi and Woondaal restaurants for authentic Shatkora Beef, seven-layer tea at Sreemangal, and local smoked dry fish delicacies.
Weather & Clothing: Heavy rainfall is common between May and August. Carry waterproof bags, light rain jackets, and non-slip trekking footwear.""",
            ),
            DocumentCreate(
                title="Sajek Valley Cloud Kingdom & Hill Trekking Guide",
                destination="Sajek",
                category="guide",
                content="""Sajek Valley is nestled 1,800 feet above sea level in the Chittagong Hill Tracts, famous for dynamic ocean-of-clouds phenomena (Helipad viewpoints).
Military Escort Rules: All tourists must travel with Bangladesh Army vehicle escorts from Dighinala to Sajek at designated escort times: 10:30 AM and 3:30 PM.
Accommodation: Eco-cottages and bamboo resorts line the ridgeline (e.g., Meghpunji, Resort RungRang, Sajek Resort).
Local Etiquette: Respect indigenous Chakma, Lusai, and Tripura traditions. Always ask permission before photographing local village elders and children.""",
            ),
        ]

        for g in guides:
            await cls.ingest_document(g, db)
        logger.info("Curated destination knowledge guides successfully ingested and indexed.")


ingestion_pipeline = IngestionPipeline()
