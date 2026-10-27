"""Unit tests for configuration loading and validation."""

from app.core.config import Settings


def test_settings_defaults():
    """Verify default configuration values."""
    settings = Settings(DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db")
    assert settings.PROJECT_NAME == "Inferaxis Backend"
    assert settings.VERSION == "0.1.0"
    assert settings.JWT_ALGORITHM == "HS256"
    assert not settings.is_sqlite


def test_cors_origins_parsing():
    """Verify comma-separated string parsing for ALLOWED_ORIGINS."""
    settings = Settings(
        ALLOWED_ORIGINS="http://localhost:3000, http://localhost:5173 , https://app.inferaxis.com"
    )
    assert settings.ALLOWED_ORIGINS == [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://app.inferaxis.com",
    ]


def test_is_sqlite_detection():
    """Verify SQLite detection helper."""
    sqlite_settings = Settings(DATABASE_URL="sqlite+aiosqlite:///inferaxis.db")
    assert sqlite_settings.is_sqlite is True

    pg_settings = Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db"
    )
    assert pg_settings.is_sqlite is False
