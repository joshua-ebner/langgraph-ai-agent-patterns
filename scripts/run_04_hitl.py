#!/usr/bin/env python3
"""Run the Module 04 human-in-the-loop demo."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_patterns.llm import get_chat_model
from agent_patterns.patterns.p03_structured_outputs.models import AgentBrief
from agent_patterns.patterns.p04_human_in_the_loop.graph import build_hitl_graph
from agent_patterns.tracing import configure_tracing, tracing_status_message

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def _print_brief(state: dict) -> None:
    brief = state.get("final_brief")
    if brief is None:
        print("No brief yet.")
        return
    if isinstance(brief, AgentBrief):
        payload = brief.model_dump()
    else:
        payload = brief
    print(json.dumps(payload, indent=2))


def _prompt_review() -> tuple[str, AgentBrief | None]:
    choice = input("Review [a]pprove / [r]eject / [e]dit summary: ").strip().lower()
    if choice.startswith("a"):
        return "approved", None
    if choice.startswith("r"):
        feedback = input("Rejection reason: ").strip()
        print(f"Recorded feedback: {feedback}")
        return "rejected", None
    if choice.startswith("e"):
        summary = input("New summary: ").strip()
        raw_points = input("Key points (comma-separated): ")
        key_points = [p.strip() for p in raw_points.split(",") if p.strip()]
        confidence = float(input("Confidence (0-1): ").strip() or "0.85")
        sources = [s.strip() for s in input("Sources (comma-separated): ").split(",") if s.strip()]
        brief = AgentBrief(
            summary=summary,
            key_points=key_points or ["edited"],
            confidence=confidence,
            sources=sources,
        )
        return "edited", brief
    print("Unknown choice; defaulting to approve.")
    return "approved", None


def main() -> None:
    parser = argparse.ArgumentParser(description="Module 04: human in the loop")
    parser.add_argument("--thread-id", default="demo-1")
    parser.add_argument("--topic", default="Human approval workflows in LangGraph")
    parser.add_argument("--max-retries", type=int, default=2)
    args = parser.parse_args()

    configure_tracing()
    graph = build_hitl_graph(get_chat_model())
    config = {"configurable": {"thread_id": args.thread_id}}

    initial_state = {
        "topic": args.topic,
        "scratchpad": "",
        "actions": [],
        "draft_brief": None,
        "final_brief": None,
        "validation_errors": [],
        "retry_count": 0,
        "max_retries": args.max_retries,
        "status": "generating",
        "review_status": "pending",
        "human_feedback": "",
        "requires_escalation": False,
        "confidence_threshold": 0.7,
    }

    result = graph.invoke(initial_state, config=config)

    while graph.get_state(config).next:
        snapshot = graph.get_state(config)
        print("\n--- Awaiting human review ---")
        if snapshot.values.get("human_feedback"):
            print(snapshot.values["human_feedback"])
        _print_brief(snapshot.values)

        review_status, edited_brief = _prompt_review()
        update = {"review_status": review_status}
        if edited_brief is not None:
            update["final_brief"] = edited_brief
        graph.update_state(config, update)
        result = graph.invoke(None, config=config)

    print("\n--- Final result ---")
    print(json.dumps(
        {
            "status": result.get("status"),
            "review_status": result.get("review_status"),
            "final_brief": (
                result["final_brief"].model_dump() if result.get("final_brief") else None
            ),
        },
        indent=2,
    ))
    print(f"\n{tracing_status_message()}")


if __name__ == "__main__":
    main()
