"""Structured output workflow with validation and retry."""

from __future__ import annotations

import json
import logging
import re

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from agent_patterns.patterns.p03_structured_outputs.models import (
    AgentBrief,
    StructuredOutputState,
    ToolAction,
)

logger = logging.getLogger(__name__)

GENERATE_PROMPT = """You produce structured research briefs.
Return JSON with keys: summary, key_points (array), confidence (0-1 float), sources (array).
Also include scratchpad (your reasoning) and actions (array of {name, detail}) in the JSON.
Topic: {topic}
{feedback}"""


def _extract_json(raw: str) -> dict:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


def build_generate_node(model: BaseChatModel):
    def generate(state: StructuredOutputState) -> dict:
        feedback = ""
        if state.get("validation_errors"):
            feedback = "Previous attempt errors:\n- " + "\n- ".join(state["validation_errors"])

        response = model.invoke(
            [
                SystemMessage(content="Return only JSON. No markdown."),
                HumanMessage(
                    content=GENERATE_PROMPT.format(
                        topic=state["topic"],
                        feedback=feedback,
                    )
                ),
            ]
        )
        payload = _extract_json(str(response.content))
        actions = [ToolAction.model_validate(item) for item in payload.get("actions", [])]
        draft = {
            "summary": payload.get("summary", ""),
            "key_points": payload.get("key_points", []),
            "confidence": payload.get("confidence", 0.0),
            "sources": payload.get("sources", []),
        }
        return {
            "scratchpad": payload.get("scratchpad", ""),
            "actions": actions,
            "draft_brief": draft,
            "status": "generating",
            "validation_errors": [],
        }

    return generate


def validate_output(state: StructuredOutputState) -> dict:
    draft = state.get("draft_brief") or {}
    try:
        brief = AgentBrief.model_validate(draft)
    except Exception as exc:
        logger.info("Validation failed: %s", exc)
        return {
            "status": "invalid",
            "validation_errors": [str(exc)],
            "final_brief": None,
        }
    return {
        "status": "valid",
        "validation_errors": [],
        "final_brief": brief,
    }


def route_after_validation(state: StructuredOutputState) -> str:
    if state.get("status") == "valid":
        return "done"
    if state.get("retry_count", 0) >= state.get("max_retries", 2):
        return "escalate"
    return "retry"


def increment_retry(state: StructuredOutputState) -> dict:
    return {"retry_count": state.get("retry_count", 0) + 1, "status": "generating"}


def escalate(state: StructuredOutputState) -> dict:
    return {
        "status": "escalated",
        "final_brief": None,
        "validation_errors": state.get("validation_errors", []) + ["Max retries exceeded"],
    }


def finalize(state: StructuredOutputState) -> dict:
    return {"status": "done"}


def build_structured_output_graph(model: BaseChatModel):
    from langgraph.graph import END, StateGraph

    graph = StateGraph(StructuredOutputState)
    graph.add_node("generate", build_generate_node(model))
    graph.add_node("validate", validate_output)
    graph.add_node("retry", increment_retry)
    graph.add_node("escalate", escalate)
    graph.add_node("finalize", finalize)

    graph.set_entry_point("generate")
    graph.add_edge("generate", "validate")
    graph.add_conditional_edges(
        "validate",
        route_after_validation,
        {"done": "finalize", "retry": "retry", "escalate": "escalate"},
    )
    graph.add_edge("retry", "generate")
    graph.add_edge("escalate", END)
    graph.add_edge("finalize", END)
    return graph.compile()
