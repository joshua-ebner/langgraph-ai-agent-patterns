"""Models for human-in-the-loop structured output workflow."""

from __future__ import annotations

from agent_patterns.patterns.p03_structured_outputs.models import (
    AgentBrief,
    ReviewStatus,
    StructuredOutputState,
    ToolAction,
    WorkflowStatus,
)

__all__ = [
    "AgentBrief",
    "HitlState",
    "ReviewStatus",
    "ToolAction",
    "WorkflowStatus",
]


class HitlState(StructuredOutputState, total=False):
    review_status: ReviewStatus
    human_feedback: str
    requires_escalation: bool
    confidence_threshold: float
