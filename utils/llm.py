"""Provider-agnostic LLM factory.

The rest of the codebase never imports a concrete LLM client. It calls
`get_llm()` and gets back something with a `.invoke(prompt) -> str`-ish
interface (LangChain chat model). Switching between a local model (Ollama)
and a hosted API (Anthropic / OpenAI) is a `.env` change, not a code change.

If no provider is configured or its package/keys are missing, `get_llm()`
returns a `StubLLM` so the whole graph still runs end-to-end for demos and
tests, emitting clearly-marked placeholder text instead of crashing.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from config import settings


class StubLLM:
    """Deterministic stand-in used when no real provider is available.

    Mirrors the tiny slice of the LangChain chat-model interface the agents
    rely on: `.invoke(str | messages) -> object with .content`.
    """

    def __init__(self, label: str = "stub") -> None:
        self.label = label

    def invoke(self, prompt: Any, **_: Any) -> "StubMessage":
        text = prompt if isinstance(prompt, str) else str(prompt)
        preview = text.strip().splitlines()[0][:120] if text.strip() else ""
        return StubMessage(
            f"[STUB LLM - no provider configured]\n"
            f"Prompt received (first line): {preview}\n"
            f"Configure LLM_PROVIDER in .env to generate real output."
        )


class StubMessage:
    def __init__(self, content: str) -> None:
        self.content = content


@lru_cache(maxsize=None)
def get_llm(temperature: float | None = None) -> Any:
    """Return a chat model for the configured provider (cached per temperature)."""
    provider = settings.llm_provider.lower()
    temp = settings.temperature if temperature is None else temperature

    try:
        if provider == "ollama":
            from langchain_ollama import ChatOllama

            return ChatOllama(model=settings.llm_model, temperature=temp,
                              base_url=settings.ollama_base_url)

        if provider == "anthropic":
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(model=settings.llm_model, temperature=temp,
                                 api_key=settings.anthropic_api_key)

        if provider == "openai":
            from langchain_openai import ChatOpenAI

            kwargs: dict[str, Any] = {}
            if settings.openai_base_url:
                # Local server (llama.cpp/LM Studio): any non-empty key works.
                kwargs["base_url"] = settings.openai_base_url
            return ChatOpenAI(
                model=settings.llm_model, temperature=temp,
                api_key=settings.openai_api_key or "sk-local", **kwargs,
            )
    except Exception as exc:  # missing package / bad key / server down
        print(f"[llm] falling back to StubLLM ({provider}): {exc}")
        return StubLLM(label=provider)

    print(f"[llm] unknown provider {provider!r}; using StubLLM")
    return StubLLM(label="unknown")
