"""Central configuration, loaded from environment / .env.

Keeps every tunable in one typed place so agents and tools never read
`os.environ` directly.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # dotenv optional; env vars may already be set
    pass


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


@dataclass(frozen=True)
class Settings:
    # ---- LLM -------------------------------------------------------------
    # LLM_PROVIDER: ollama | anthropic | openai
    llm_provider: str = field(default_factory=lambda: _env("LLM_PROVIDER", "ollama"))
    llm_model: str = field(default_factory=lambda: _env("LLM_MODEL", "qwen2.5:7b"))
    temperature: float = field(default_factory=lambda: float(_env("LLM_TEMPERATURE", "0.3")))
    ollama_base_url: str = field(default_factory=lambda: _env("OLLAMA_BASE_URL", "http://localhost:11434"))

    anthropic_api_key: str = field(default_factory=lambda: _env("ANTHROPIC_API_KEY"))
    openai_api_key: str = field(default_factory=lambda: _env("OPENAI_API_KEY"))
    # Point the OpenAI provider at a local server (llama.cpp, LM Studio, ...).
    openai_base_url: str = field(default_factory=lambda: _env("OPENAI_BASE_URL"))

    # ---- Tools -----------------------------------------------------------
    tavily_api_key: str = field(default_factory=lambda: _env("TAVILY_API_KEY"))
    github_token: str = field(default_factory=lambda: _env("GITHUB_TOKEN"))

    # ---- Runtime ---------------------------------------------------------
    # Fan the specialist agents out in parallel (True) or run sequentially.
    parallel_agents: bool = field(default_factory=lambda: _env("PARALLEL_AGENTS", "true").lower() == "true")
    # Pause for human approval of the final report before finishing.
    human_approval: bool = field(default_factory=lambda: _env("HUMAN_APPROVAL", "false").lower() == "true")

    # ---- Paths -----------------------------------------------------------
    reports_dir: str = field(default_factory=lambda: _env("REPORTS_DIR", "reports"))
    memory_db: str = field(default_factory=lambda: _env("MEMORY_DB", "memory/venture.sqlite"))


settings = Settings()
