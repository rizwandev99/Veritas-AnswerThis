"""
Unit tests for Veritas core configuration engine (Pydantic v2 BaseSettings).
"""
import pytest
from app.core.config import Settings


def test_settings_defaults() -> None:
    """Verifies default settings are initialized correctly."""
    settings = Settings()
    assert settings.PROJECT_NAME == "Veritas API"
    assert settings.VERSION == "0.1.0"
    assert settings.PORT == 8000
    assert settings.VECTOR_STORE_BACKEND in ("pgvector", "faiss")
    assert "http://localhost:3000" in settings.CORS_ORIGINS


def test_settings_cors_origins_csv_parsing() -> None:
    """Verifies that comma-separated CORS_ORIGINS strings are parsed into clean lists."""
    settings = Settings(CORS_ORIGINS="http://localhost:3000, https://veritas.app , http://127.0.0.1:3000")
    assert settings.CORS_ORIGINS == [
        "http://localhost:3000",
        "https://veritas.app",
        "http://127.0.0.1:3000",
    ]


def test_settings_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies environment variables override default settings."""
    monkeypatch.setenv("PORT", "9000")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("VECTOR_STORE_BACKEND", "faiss")

    settings = Settings()
    assert settings.PORT == 9000
    assert settings.ENVIRONMENT == "production"
    assert settings.VECTOR_STORE_BACKEND == "faiss"
