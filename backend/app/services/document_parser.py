"""Document and table parsing service utilizing NVIDIA Nemotron Parse."""

from __future__ import annotations

import base64
import logging
from typing import Any

from app.core.config import Settings, get_settings
from app.core.llm import get_nvidia_parse_client

logger = logging.getLogger("inferaxis.services.document_parser")


class DocumentParsingError(Exception):
    """Raised when document or table parsing via Nemotron Parse fails."""


class DocumentParserService:
    """Extracts tables, structured layouts, and text from document images and PDFs."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def parse_document_image(
        self,
        image_bytes: bytes,
        mime_type: str = "image/png",
    ) -> dict[str, Any]:
        """Extract layout and tabular data from an encoded document image.

        Args:
            image_bytes: Raw binary bytes of the image/scanned page.
            mime_type: Mime type of the image (e.g. 'image/png', 'image/jpeg').

        Returns:
            Dictionary containing extracted tables and layout markdown.

        Raises:
            DocumentParsingError: If client execution fails.
        """
        try:
            client = get_nvidia_parse_client(self.settings)
            base64_img = base64.b64encode(image_bytes).decode("utf-8")
            image_url = f"data:{mime_type};base64,{base64_img}"

            response = client.chat.completions.create(
                model=self.settings.NVIDIA_PARSE_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Extract all tables, tabular figures, and structured data from this document. "
                                    "Return extracted tables formatted cleanly in markdown and structured JSON."
                                ),
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url},
                            },
                        ],
                    }
                ],
                temperature=0.1,
                max_tokens=4096,
            )

            content = response.choices[0].message.content or ""
            return {
                "model": self.settings.NVIDIA_PARSE_MODEL,
                "parsed_content": content,
                "raw_response": response.model_dump() if hasattr(response, "model_dump") else {},
            }

        except Exception as err:
            logger.error("Failed to parse document with Nemotron Parse: %s", err)
            raise DocumentParsingError(f"Document parsing failed: {err}") from err


_parser_instance: DocumentParserService | None = None


def get_document_parser() -> DocumentParserService:
    """Retrieve singleton DocumentParserService instance."""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = DocumentParserService()
    return _parser_instance
