"""Environment and runtime configuration."""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL_PROVIDER = "openai"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
DEFAULT_LANGSMITH_PROJECT = "langgraph-ai-agent-patterns"


@lru_cache
def get_model_provider() -> str:
    return os.getenv("MODEL_PROVIDER", DEFAULT_MODEL_PROVIDER).lower()


@lru_cache
def get_model_name() -> str:
    explicit = os.getenv("MODEL_NAME")
    if explicit:
        return explicit
    if get_model_provider() == "anthropic":
        return os.getenv("ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL)
    return os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)


@lru_cache
def get_langsmith_project() -> str:
    return os.getenv("LANGSMITH_PROJECT", DEFAULT_LANGSMITH_PROJECT)


def require_api_key(provider: str | None = None) -> None:
    """Raise if the selected provider's API key is missing."""
    selected = provider or get_model_provider()
    if selected == "anthropic":
        key = os.getenv("ANTHROPIC_API_KEY")
        label = "ANTHROPIC_API_KEY"
    else:
        key = os.getenv("OPENAI_API_KEY")
        label = "OPENAI_API_KEY"
    if not key:
        raise RuntimeError(f"Missing {label} for provider '{selected}'")
