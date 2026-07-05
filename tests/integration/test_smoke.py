"""Optional live API smoke tests."""

from __future__ import annotations

import pytest

from agent_patterns.llm import get_chat_model
from agent_patterns.patterns.p05_testing_debugging.graph import build_debug_graph


@pytest.mark.integration
def test_debug_graph_live_smoke():
    graph = build_debug_graph(get_chat_model())
    result = graph.invoke(
        {
            "question": "Reply with exactly: ok",
            "answer": "",
            "mode": "",
            "latency_ms": 0.0,
        }
    )
    assert result["answer"]
    assert result["latency_ms"] >= 0
