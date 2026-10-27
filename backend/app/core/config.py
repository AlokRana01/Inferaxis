"""Application configuration loaded from environment variables using Pydantic Settings."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for Inferaxis Backend."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    PROJECT_NAME: str = "Inferaxis Backend"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Server & Networking
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    ALLOWED_ORIGINS: str | list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # Security (placeholders for dev, required in production)
    JWT_SECRET_KEY: str = (
        "inferaxis_default_development_secret_key_change_in_production"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://inferaxis_user:replace_with_secure_password@localhost:5432/inferaxis_db"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # LLM Providers (Groq, Google Gemini, and NVIDIA NIM)
    LLM_PROVIDER: str = "groq"
    LLM_FALLBACK_PROVIDER: str = "gemini"
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-1.5-pro"
    NVIDIA_API_KEY: str | None = None
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_MODEL: str = "meta/llama-3.3-70b-instruct"

    # NVIDIA Document & Table Parsing (Nemotron Parse)
    NVIDIA_PARSE_API_KEY: str | None = None
    NVIDIA_PARSE_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_PARSE_MODEL: str = "nvidia/nemotron-3.5-parse"

    # Storage
    STORAGE_PATH: str = "./storage"
    DATASET_STORAGE_PATH: str = "./storage/datasets"
    MAX_UPLOAD_SIZE_BYTES: int = 52428800  # 50MB

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def is_sqlite(self) -> bool:
        """Helper to determine if the active database is SQLite."""
        return "sqlite" in self.DATABASE_URL.lower()


@lru_cache
def get_settings() -> Settings:
    """Retrieve cached instance of application settings."""
    return Settings()
