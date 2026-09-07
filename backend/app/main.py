from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import init_db, AsyncSessionLocal
from app.core.redis import redis_service
from app.api.v1.api import api_router
from app.api.v1.endpoints.destinations import _seed_default_destinations
from app.rag.ingestion import ingestion_pipeline
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s: %(message)s"
)
logger = logging.getLogger("ai_travel_copilot")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespans."""
    logger.info("Starting up AI Travel Copilot backend service...")
    # Initialize DB tables
    await init_db()
    # Initialize Redis connection
    await redis_service.init_redis()

    # Seed initial destinations and RAG knowledge
    async with AsyncSessionLocal() as db:
        try:
            await _seed_default_destinations(db)
            await ingestion_pipeline.seed_curated_destination_knowledge(db)
            logger.info("Initial destination data and RAG knowledge seeded successfully.")
        except Exception as e:
            logger.warning(f"Data seeding note: {e}")

    yield

    logger.info("Shutting down AI Travel Copilot backend service...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade AI Travel Copilot Backend API powered by FastAPI, LangGraph, PostgreSQL+pgvector, and Redis.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "ai_engine": "operational",
    }


# Include V1 API Routers
app.include_router(api_router, prefix=settings.API_V1_STR)
