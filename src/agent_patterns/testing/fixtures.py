"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from agent_patterns.testing.mock_llm import ScriptedChatModel


@pytest.fixture
def mock_llm() -> ScriptedChatModel:
    return ScriptedChatModel(responses=["mock response"])
