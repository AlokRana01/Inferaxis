"""Unified LLM router managing specialized provider execution and automatic fallback.

Routing Strategy:
  - 'fast' / 'tool' / 'code': Dispatched to Groq (Llama 3.3 70B) for sub-second execution.
  - 'reasoning' / 'statistical': Dispatched to NVIDIA NIM (Llama 3.3 70B / Nemotron).
  - 'synthesis' / 'report': Dispatched to Google Gemini (Gemini 1.5 Pro) for high context.
  - Automatic Failover: If the primary engine errors (e.g. 429 rate limit), the request
    automatically falls back across the provider chain.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any

from app.core.config import Settings, get_settings
from app.core.llm import (
    LLMConfigurationError,
    configure_gemini,
    get_groq_client,
    get_nvidia_client,
)

logger = logging.getLogger("inferaxis.services.llm_router")


class LLMTaskType(str, Enum):
    """Categorization of agentic analytical workloads for optimal provider dispatch."""

    FAST = "fast"
    REASONING = "reasoning"
    SYNTHESIS = "synthesis"


class LLMRoutingError(RuntimeError):
    """Raised when all available providers fail to complete an LLM request."""


class LLMRouter:
    """Intelligent multi-provider LLM coordinator with automatic resilience failover."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def _call_groq(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        """Execute chat completion via Groq."""
        client = get_groq_client(self.settings)
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=self.settings.GROQ_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return str(response.choices[0].message.content)

    def _call_nvidia(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        """Execute chat completion via NVIDIA NIM."""
        client = get_nvidia_client(self.settings)
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=self.settings.NVIDIA_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return str(response.choices[0].message.content)

    def _call_gemini(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        """Execute content generation via Google Gemini."""
        genai = configure_gemini(self.settings)
        model = genai.GenerativeModel(
            model_name=self.settings.GEMINI_MODEL,
            system_instruction=system_prompt if system_prompt else None,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            },
        )
        response = model.generate_content(prompt)
        return str(response.text)

    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        task_type: LLMTaskType = LLMTaskType.FAST,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        """Route request according to task tier with automatic multi-provider fallback.

        Execution Priority Chains:
          - FAST: Groq -> NVIDIA NIM -> Gemini
          - REASONING: NVIDIA NIM -> Groq -> Gemini
          - SYNTHESIS: Gemini -> NVIDIA NIM -> Groq
        """
        if task_type == LLMTaskType.FAST:
            chain = [
                ("groq", self._call_groq),
                ("nvidia", self._call_nvidia),
                ("gemini", self._call_gemini),
            ]
        elif task_type == LLMTaskType.REASONING:
            chain = [
                ("nvidia", self._call_nvidia),
                ("groq", self._call_groq),
                ("gemini", self._call_gemini),
            ]
        else:  # SYNTHESIS
            chain = [
                ("gemini", self._call_gemini),
                ("nvidia", self._call_nvidia),
                ("groq", self._call_groq),
            ]

        errors: list[str] = []

        for provider_name, runner in chain:
            try:
                logger.info(
                    "Executing LLM task (type='%s') with provider '%s'",
                    task_type.value,
                    provider_name,
                )
                result = runner(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return result
            except (LLMConfigurationError, Exception) as err:
                logger.warning(
                    "Provider '%s' failed for task '%s': %s. Trying next provider in fallback chain.",
                    provider_name,
                    task_type.value,
                    err,
                )
                errors.append(f"{provider_name}: {err}")

        raise LLMRoutingError(
            f"All configured providers failed for task '{task_type.value}': {'; '.join(errors)}"
        )


_router_instance: LLMRouter | None = None


def get_llm_router() -> LLMRouter:
    """Retrieve singleton LLMRouter instance."""
    global _router_instance
    if _router_instance is None:
        _router_instance = LLMRouter()
    return _router_instance
