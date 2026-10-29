"""
Veritas Core Configuration
Loads environment variables with robust validation and sensible defaults using Pydantic v2.
"""
from functools import lru_cache
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Project Metadata
    PROJECT_NAME: str = "Veritas API"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database & Persistence
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/veritas",
        description="Async PostgreSQL connection string"
    )
    DB_POOL_MIN_SIZE: int = 2
    DB_POOL_MAX_SIZE: int = 10
    DB_POOL_TIMEOUT_SECONDS: float = 10.0

    # Vector Storage
    VECTOR_STORE_BACKEND: str = Field(
        default="pgvector",
        description="Vector store backend: 'pgvector' or 'faiss'"
    )
    EMBEDDING_DIMENSION: int = 384

    # CORS Configuration
    CORS_ORIGINS: Union[List[str], str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins"
    )

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # External Provider Identifiers & Keys (100% Free Tier)
    OPENALEX_MAILTO: str = Field(
        default="team@veritas.local",
        description="Polite-pool identification email for OpenAlex API"
    )
    SEMANTIC_SCHOLAR_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    LLM_PROVIDER: str = "gemini"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_HOURLY_REVIEW_LIMIT: int = 5

    # Pipeline Tuning Parameters
    MAX_CANDIDATE_PAPERS: int = 25
    TOP_N_RANKED_PAPERS: int = 12
    CHUNK_WINDOW_SENTENCES: int = 3
    CHUNK_OVERLAP_SENTENCES: int = 1
    VERIFICATION_SEMAPHORE_LIMIT: int = 5


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton settings instance."""
    return Settings()


settings = get_settings()
