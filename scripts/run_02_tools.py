#!/usr/bin/env python3
"""Run the Module 02 tool-use demo."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from langchain_core.messages import HumanMessage

from agent_patterns.llm import get_chat_model
from agent_patterns.patterns.p02_tool_use.graph import build_tool_agent_graph
from agent_patterns.tracing import configure_tracing, tracing_status_message

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Module 02: tool use")
    parser.add_argument("--question", default="Look up a fact about pytest and summarize it.")
    args = parser.parse_args()

    configure_tracing()
    graph = build_tool_agent_graph(get_chat_model())
    result = graph.invoke(
        {
            "messages": [HumanMessage(content=args.question)],
            "validation_status": "pending",
            "validation_errors": [],
            "tool_call_count": 0,
        }
    )

    print("\n--- Agent response ---")
    print(result["messages"][-1].content)
    print(f"\nTool calls made: {result['tool_call_count']}")
    print(tracing_status_message())


if __name__ == "__main__":
    main()
