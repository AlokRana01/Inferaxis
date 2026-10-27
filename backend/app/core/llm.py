"""LLM client and model initialization for Groq, Google Gemini, and NVIDIA NIM."""

from __future__ import annotations

import logging
from typing import Any

from app.core.config import Settings, get_settings

logger = logging.getLogger("inferaxis.core.llm")


class LLMConfigurationError(RuntimeError):
    """Raised when an LLM provider is misconfigured or missing credentials."""


def get_groq_client(settings: Settings | None = None) -> Any:
    """Initialize and return a Groq client instance.

    Raises:
        LLMConfigurationError: If GROQ_API_KEY is not configured.
    """
    if settings is None:
        settings = get_settings()

    if not settings.GROQ_API_KEY:
        raise LLMConfigurationError(
            "GROQ_API_KEY is not configured. Please set GROQ_API_KEY in your environment or .env file."
        )

    try:
        from groq import Groq

        return Groq(api_key=settings.GROQ_API_KEY)
    except ImportError as err:
        raise LLMConfigurationError(
            "The 'groq' package is not installed. Install it with: pip install groq"
        ) from err


def configure_gemini(settings: Settings | None = None) -> Any:
    """Configure and return Google Generative AI client/module.

    Raises:
        LLMConfigurationError: If GEMINI_API_KEY is not configured.
    """
    if settings is None:
        settings = get_settings()

    if not settings.GEMINI_API_KEY:
        raise LLMConfigurationError(
            "GEMINI_API_KEY is not configured. Please set GEMINI_API_KEY in your environment or .env file."
        )

    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.GEMINI_API_KEY)
        return genai
    except ImportError as err:
        raise LLMConfigurationError(
            "The 'google-generativeai' package is not installed. Install it with: pip install google-generativeai"
        ) from err


def get_nvidia_client(settings: Settings | None = None) -> Any:
    """Initialize and return an OpenAI-compatible client configured for NVIDIA NIM.

    Raises:
        LLMConfigurationError: If NVIDIA_API_KEY is not configured.
    """
    if settings is None:
        settings = get_settings()

    if not settings.NVIDIA_API_KEY:
        raise LLMConfigurationError(
            "NVIDIA_API_KEY is not configured. Please set NVIDIA_API_KEY in your environment or .env file."
        )

    try:
        from openai import OpenAI

        return OpenAI(
            base_url=settings.NVIDIA_BASE_URL,
            api_key=settings.NVIDIA_API_KEY,
        )
    except ImportError as err:
        raise LLMConfigurationError(
            "The 'openai' package is not installed for NVIDIA NIM access. Install it with: pip install openai"
        ) from err


def get_nvidia_parse_client(settings: Settings | None = None) -> Any:
    """Initialize and return an OpenAI-compatible client for NVIDIA Nemotron Parse.

    Raises:
        LLMConfigurationError: If NVIDIA_PARSE_API_KEY (or NVIDIA_API_KEY) is not configured.
    """
    if settings is None:
        settings = get_settings()

    api_key = settings.NVIDIA_PARSE_API_KEY or settings.NVIDIA_API_KEY
    if not api_key:
        raise LLMConfigurationError(
            "NVIDIA_PARSE_API_KEY is not configured. Please set NVIDIA_PARSE_API_KEY in your environment or .env file."
        )

    try:
        from openai import OpenAI

        return OpenAI(
            base_url=settings.NVIDIA_PARSE_BASE_URL,
            api_key=api_key,
        )
    except ImportError as err:
        raise LLMConfigurationError(
            "The 'openai' package is not installed for NVIDIA Parse access. Install it with: pip install openai"
        ) from err

