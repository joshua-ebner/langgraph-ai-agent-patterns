"""API tests for the pattern picker UI."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from agent_patterns.testing.mock_llm import ScriptedChatModel
from ui.api.main import app


@pytest.fixture
def client():
    mock_model = ScriptedChatModel(
        responses=[
            '["step one", "step two"]',
            "mock answer",
        ]
    )
    with patch("ui.api.runner.get_chat_model", return_value=mock_model):
        with TestClient(app) as test_client:
            yield test_client


def test_list_patterns(client: TestClient):
    response = client.get("/api/patterns")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 5
    assert {item["id"] for item in payload} == {"p01", "p02", "p03", "p04", "p05"}


def test_get_pattern(client: TestClient):
    response = client.get("/api/patterns/p01")
    assert response.status_code == 200
    assert response.json()["id"] == "p01"


def test_run_p01(client: TestClient):
    response = client.post(
        "/api/patterns/p01/run",
        json={"inputs": {"goal": "Test goal", "max_steps": 2}},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["pattern_id"] == "p01"
    assert payload["interrupted"] is False
    assert payload["state"]["step_count"] == 2
    assert payload["state"]["status"] == "done"


def test_unknown_pattern(client: TestClient):
    response = client.post("/api/patterns/unknown/run", json={"inputs": {}})
    assert response.status_code == 404
