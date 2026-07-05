#!/usr/bin/env python3
"""Run the Module 05 testing and debugging demo."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_patterns.llm import get_chat_model
from agent_patterns.patterns.p05_testing_debugging.graph import (
    BUGGY_PROMPT,
    FIXED_PROMPT,
    build_debug_graph,
)
from agent_patterns.tracing import configure_tracing, tracing_status_message

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Module 05: testing and debugging")
    parser.add_argument("--question", default="Explain why agent tests should mock the LLM.")
    parser.add_argument("--buggy", action="store_true", help="Use the intentionally weak prompt")
    args = parser.parse_args()

    configure_tracing()
    graph = build_debug_graph(get_chat_model(), buggy=args.buggy)
    result = graph.invoke({"question": args.question, "answer": "", "mode": "", "latency_ms": 0.0})

    prompt = BUGGY_PROMPT if args.buggy else FIXED_PROMPT
    print("\n--- Debug run ---")
    print(f"Prompt: {prompt}")
    print(f"Mode: {result['mode']}")
    print(f"Latency: {result['latency_ms']:.1f} ms")
    print(f"Answer: {result['answer']}")
    print(f"\n{tracing_status_message()}")


if __name__ == "__main__":
    main()
