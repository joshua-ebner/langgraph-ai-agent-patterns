"""Unit tests for Module 03 validation and routing."""

from agent_patterns.patterns.p03_structured_outputs.graph import (
    route_after_validation,
    validate_output,
)
from agent_patterns.patterns.p03_structured_outputs.models import AgentBrief


def test_validate_accepts_valid_brief():
    state = {
        "draft_brief": {
            "summary": "A sufficiently long summary for testing.",
            "key_points": ["one"],
            "confidence": 0.8,
            "sources": ["docs"],
        }
    }
    result = validate_output(state)
    assert result["status"] == "valid"
    assert isinstance(result["final_brief"], AgentBrief)


def test_validate_rejects_short_summary():
    state = {
        "draft_brief": {
            "summary": "short",
            "key_points": ["one"],
            "confidence": 0.8,
            "sources": [],
        }
    }
    result = validate_output(state)
    assert result["status"] == "invalid"
    assert result["validation_errors"]


def test_route_retries_when_invalid():
    state = {"status": "invalid", "retry_count": 0, "max_retries": 2}
    assert route_after_validation(state) == "retry"


def test_route_escalates_at_max_retries():
    state = {"status": "invalid", "retry_count": 2, "max_retries": 2}
    assert route_after_validation(state) == "escalate"


def test_route_done_when_valid():
    state = {"status": "valid", "retry_count": 0, "max_retries": 2}
    assert route_after_validation(state) == "done"
