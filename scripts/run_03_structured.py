#!/usr/bin/env python3
"""Run the Module 03 structured output demo."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_patterns.llm import get_chat_model
from agent_patterns.patterns.p03_structured_outputs.graph import build_structured_output_graph
from agent_patterns.tracing import configure_tracing, tracing_status_message

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Module 03: structured outputs")
    parser.add_argument("--topic", default="Benefits of typed LangGraph state")
    parser.add_argument("--max-retries", type=int, default=2)
    args = parser.parse_args()

    configure_tracing()
    graph = build_structured_output_graph(get_chat_model())
    result = graph.invoke(
        {
            "topic": args.topic,
            "scratchpad": "",
            "actions": [],
            "draft_brief": None,
            "final_brief": None,
            "validation_errors": [],
            "retry_count": 0,
            "max_retries": args.max_retries,
            "status": "generating",
        }
    )

    print("\n--- Result ---")
    brief = result.get("final_brief")
    print(json.dumps(
        {
            "status": result["status"],
            "scratchpad": result.get("scratchpad"),
            "actions": [a.model_dump() for a in result.get("actions", [])],
            "final_brief": brief.model_dump() if brief else None,
            "validation_errors": result.get("validation_errors", []),
        },
        indent=2,
    ))
    print(f"\n{tracing_status_message()}")


if __name__ == "__main__":
    main()
