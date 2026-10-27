"""Unit tests for unified LLMRouter and DocumentParserService with fallback verification."""

from unittest.mock import MagicMock, patch
import pytest

from app.core.config import Settings
from app.services.document_parser import DocumentParserService
from app.services.llm_router import LLMRouter, LLMTaskType


@pytest.fixture
def mock_settings():
    return Settings(
        DATABASE_URL="sqlite+aiosqlite:///test.db",
        GROQ_API_KEY="gsk_test_groq_key",
        GEMINI_API_KEY="test_gemini_key",
        NVIDIA_API_KEY="nvapi_test_nvidia_key",
        NVIDIA_PARSE_API_KEY="nvapi_test_parse_key",
    )


@pytest.mark.asyncio
async def test_llm_router_fast_routes_to_groq(mock_settings):
    """Verify FAST task routes to Groq first."""
    router = LLMRouter(settings=mock_settings)

    with patch.object(router, "_call_groq", return_value="Groq response") as mock_groq:
        result = await router.complete("Hello", task_type=LLMTaskType.FAST)
        assert result == "Groq response"
        mock_groq.assert_called_once()


@pytest.mark.asyncio
async def test_llm_router_fast_falls_back_to_nvidia(mock_settings):
    """Verify FAST task falls back to NVIDIA NIM if Groq raises an error."""
    router = LLMRouter(settings=mock_settings)

    with (
        patch.object(router, "_call_groq", side_effect=RuntimeError("Groq 429 Rate Limit")),
        patch.object(router, "_call_nvidia", return_value="NVIDIA NIM fallback response") as mock_nvidia,
    ):
        result = await router.complete("Hello", task_type=LLMTaskType.FAST)
        assert result == "NVIDIA NIM fallback response"
        mock_nvidia.assert_called_once()


@pytest.mark.asyncio
async def test_llm_router_synthesis_routes_to_gemini(mock_settings):
    """Verify SYNTHESIS task routes to Google Gemini first."""
    router = LLMRouter(settings=mock_settings)

    with patch.object(router, "_call_gemini", return_value="Gemini synthesis") as mock_gemini:
        result = await router.complete("Analyze dataset", task_type=LLMTaskType.SYNTHESIS)
        assert result == "Gemini synthesis"
        mock_gemini.assert_called_once()


def test_document_parser_service_parses_image(mock_settings):
    """Verify DocumentParserService builds proper OpenAI-compatible vision payload for Nemotron Parse."""
    parser = DocumentParserService(settings=mock_settings)

    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "| Col1 | Col2 |\n| --- | --- |\n| Val1 | Val2 |"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    with patch("app.services.document_parser.get_nvidia_parse_client", return_value=mock_client):
        result = parser.parse_document_image(b"fake_image_bytes", mime_type="image/png")
        assert "| Col1 | Col2 |" in result["parsed_content"]
        assert result["model"] == "nvidia/nemotron-3.5-parse"
        mock_client.chat.completions.create.assert_called_once()
