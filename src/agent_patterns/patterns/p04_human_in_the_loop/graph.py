"""Human-in-the-loop workflow built on structured outputs."""

from __future__ import annotations

import logging

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from agent_patterns.patterns.p03_structured_outputs.graph import (
    build_generate_node,
    escalate,
    finalize,
    increment_retry,
    route_after_validation,
    validate_output,
)
from agent_patterns.patterns.p04_human_in_the_loop.models import HitlState

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.7


def check_confidence(state: HitlState) -> dict:
    brief = state.get("final_brief")
    threshold = state.get("confidence_threshold", CONFIDENCE_THRESHOLD)
    if brief and brief.confidence < threshold:
        return {
            "requires_escalation": True,
            "human_feedback": (
                f"Low confidence ({brief.confidence:.2f} < {threshold:.2f}). "
                "Human review required before approval."
            ),
        }
    return {"requires_escalation": False}


def route_after_confidence(state: HitlState) -> str:
    if state.get("requires_escalation"):
        return "escalate_review"
    return "human_review"


def escalate_review(state: HitlState) -> dict:
    return {
        "status": "escalated",
        "review_status": "pending",
        "human_feedback": state.get("human_feedback", "Escalated for human review."),
    }


def human_review(state: HitlState) -> dict:
    """Checkpoint node — CLI/script supplies review decision before resume."""
    return {"review_status": state.get("review_status", "pending")}


def route_after_review(state: HitlState) -> str:
    status = state.get("review_status", "pending")
    if status == "approved":
        return "finalize"
    if status == "edited":
        return "finalize"
    if status == "rejected":
        return "retry"
    return "wait"


def apply_human_edits(state: HitlState) -> dict:
    if state.get("review_status") != "edited":
        return {}
    brief = state.get("final_brief")
    if brief is None:
        return {}
    return {"final_brief": brief, "status": "valid"}


def build_hitl_graph(model: BaseChatModel, *, checkpointer: MemorySaver | None = None):
    graph = StateGraph(HitlState)
    graph.add_node("generate", build_generate_node(model))
    graph.add_node("validate", validate_output)
    graph.add_node("retry", increment_retry)
    graph.add_node("escalate", escalate)
    graph.add_node("check_confidence", check_confidence)
    graph.add_node("escalate_review", escalate_review)
    graph.add_node("human_review", human_review)
    graph.add_node("apply_edits", apply_human_edits)
    graph.add_node("finalize", finalize)

    graph.set_entry_point("generate")
    graph.add_edge("generate", "validate")
    graph.add_conditional_edges(
        "validate",
        route_after_validation,
        {"done": "check_confidence", "retry": "retry", "escalate": "escalate"},
    )
    graph.add_edge("retry", "generate")
    graph.add_conditional_edges(
        "check_confidence",
        route_after_confidence,
        {"escalate_review": "escalate_review", "human_review": "human_review"},
    )
    graph.add_edge("escalate_review", "human_review")
    graph.add_conditional_edges(
        "human_review",
        route_after_review,
        {
            "finalize": "apply_edits",
            "retry": "retry",
            "wait": "human_review",
        },
    )
    graph.add_edge("apply_edits", "finalize")
    graph.add_edge("finalize", END)
    graph.add_edge("escalate", END)

    memory = checkpointer or MemorySaver()
    return graph.compile(
        checkpointer=memory,
        interrupt_before=["human_review"],
    )
