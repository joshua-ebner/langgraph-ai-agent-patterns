"""Unit tests for Module 04 confidence routing and review decisions."""

from agent_patterns.patterns.p03_structured_outputs.models import AgentBrief
from agent_patterns.patterns.p04_human_in_the_loop.graph import (
    check_confidence,
    route_after_confidence,
    route_after_review,
)


def test_check_confidence_flags_low_score():
    brief = AgentBrief(
        summary="A sufficiently long summary for testing.",
        key_points=["one"],
        confidence=0.4,
        sources=["docs"],
    )
    result = check_confidence({"final_brief": brief, "confidence_threshold": 0.7})
    assert result["requires_escalation"] is True


def test_check_confidence_passes_high_score():
    brief = AgentBrief(
        summary="A sufficiently long summary for testing.",
        key_points=["one"],
        confidence=0.9,
        sources=["docs"],
    )
    result = check_confidence({"final_brief": brief, "confidence_threshold": 0.7})
    assert result["requires_escalation"] is False


def test_route_after_confidence():
    assert route_after_confidence({"requires_escalation": True}) == "escalate_review"
    assert route_after_confidence({"requires_escalation": False}) == "human_review"


def test_route_after_review():
    assert route_after_review({"review_status": "approved"}) == "finalize"
    assert route_after_review({"review_status": "edited"}) == "finalize"
    assert route_after_review({"review_status": "rejected"}) == "retry"
    assert route_after_review({"review_status": "pending"}) == "wait"
