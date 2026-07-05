"""Chat model factory."""

from __future__ import annotations

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from agent_patterns.config import get_model_name, get_model_provider, require_api_key


def get_chat_model(
    *,
    provider: str | None = None,
    model: str | None = None,
    temperature: float = 0.0,
) -> BaseChatModel:
    """Return a configured chat model for the selected provider."""
    selected_provider = (provider or get_model_provider()).lower()
    selected_model = model or get_model_name()
    require_api_key(selected_provider)

    if selected_provider == "anthropic":
        return ChatAnthropic(model=selected_model, temperature=temperature)
    if selected_provider == "openai":
        return ChatOpenAI(model=selected_model, temperature=temperature)
    raise ValueError(f"Unsupported model provider: {selected_provider}")
