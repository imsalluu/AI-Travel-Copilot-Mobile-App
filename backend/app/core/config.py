import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # App info
    APP_NAME: str = "AI Travel Copilot"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = "supersecretjwtkeychangeinproductionmustbe64byteslengthforsecurity12345"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/travel_copilot_db"
    SYNC_DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/travel_copilot_db"
    SQLITE_FALLBACK_URL: str = "sqlite+aiosqlite:///./travel_copilot.db"
    USE_SQLITE_FALLBACK: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False

    # LLM & AI Engine
    AI_PROVIDER: str = "openai"  # openai, anthropic, gemini, or mock
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"

    # Embeddings & RAG
    EMBEDDING_PROVIDER: str = "mock"  # openai, local, mock
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536

    # Weather
    OPEN_METEO_API_URL: str = "https://api.open-meteo.com/v1"

    # Maps
    MAP_PROVIDER: str = "osm"
    MAPBOX_ACCESS_TOKEN: str = ""
    GOOGLE_MAPS_API_KEY: str = ""

    # Voice
    VOICE_STT_PROVIDER: str = "openai"
    VOICE_TTS_PROVIDER: str = "openai"


settings = Settings()
