"""Deterministic chat models for unit tests."""

from __future__ import annotations

from typing import Any

from langchain_core.language_models.fake_chat_models import FakeListChatModel


class ScriptedChatModel(FakeListChatModel):
    """Fake chat model with scripted responses for deterministic tests."""

    tool_calls_sequence: list[list[dict[str, Any]]] | None = None

    def bind_tools(self, tools: Any, **kwargs: Any) -> ScriptedChatModel:
        return self
