#!/usr/bin/env python3
"""Run the Module 01 planner control-flow demo."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from langchain_core.messages import HumanMessage

from agent_patterns.llm import get_chat_model
from agent_patterns.patterns.p01_state_control_flow.graph import build_planner_graph
from agent_patterns.tracing import configure_tracing, tracing_status_message

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Module 01: state and control flow")
    parser.add_argument("--goal", default="Prepare a concise project status update")
    parser.add_argument("--max-steps", type=int, default=10)
    args = parser.parse_args()

    configure_tracing()
    model = get_chat_model()
    graph = build_planner_graph(model)

    initial_state = {
        "messages": [HumanMessage(content=args.goal)],
        "plan": [],
        "step_count": 0,
        "current_step_index": 0,
        "status": "planning",
        "max_steps": args.max_steps,
    }

    result = graph.invoke(initial_state)
    print("\n--- Final state ---")
    print(json.dumps(
        {
            "status": result["status"],
            "plan": result["plan"],
            "step_count": result["step_count"],
            "messages": [m.content for m in result["messages"]],
        },
        indent=2,
    ))
    print(f"\n{tracing_status_message()}")


if __name__ == "__main__":
    main()
