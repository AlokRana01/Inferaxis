"""Unit tests for Groq, Gemini, and NVIDIA NIM LLM provider client configuration."""

import pytest
from app.core.config import Settings
from app.core.llm import (
    LLMConfigurationError,
    configure_gemini,
    get_groq_client,
    get_nvidia_client,
    get_nvidia_parse_client,
)


def test_groq_client_missing_key_raises_error():
    """Verify missing GROQ_API_KEY raises LLMConfigurationError."""
    settings = Settings(DATABASE_URL="sqlite+aiosqlite:///test.db", GROQ_API_KEY="")
    with pytest.raises(LLMConfigurationError, match="GROQ_API_KEY is not configured"):
        get_groq_client(settings=settings)


def test_gemini_client_missing_key_raises_error():
    """Verify missing GEMINI_API_KEY raises LLMConfigurationError."""
    settings = Settings(DATABASE_URL="sqlite+aiosqlite:///test.db", GEMINI_API_KEY="")
    with pytest.raises(LLMConfigurationError, match="GEMINI_API_KEY is not configured"):
        configure_gemini(settings=settings)


def test_nvidia_client_missing_key_raises_error():
    """Verify missing NVIDIA_API_KEY raises LLMConfigurationError."""
    settings = Settings(DATABASE_URL="sqlite+aiosqlite:///test.db", NVIDIA_API_KEY="")
    with pytest.raises(LLMConfigurationError, match="NVIDIA_API_KEY is not configured"):
        get_nvidia_client(settings=settings)


def test_nvidia_parse_client_missing_key_raises_error():
    """Verify missing NVIDIA_PARSE_API_KEY and NVIDIA_API_KEY raises LLMConfigurationError."""
    settings = Settings(
        DATABASE_URL="sqlite+aiosqlite:///test.db",
        NVIDIA_API_KEY="",
        NVIDIA_PARSE_API_KEY="",
    )
    with pytest.raises(LLMConfigurationError, match="NVIDIA_PARSE_API_KEY is not configured"):
        get_nvidia_parse_client(settings=settings)

