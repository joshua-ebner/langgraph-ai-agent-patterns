"""Meta-module demonstrating testing and debugging patterns."""

from __future__ import annotations

import logging
import time
from typing import TypedDict

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

logger = logging.getLogger(__name__)

BUGGY_PROMPT = "Answer in one sentence."
FIXED_PROMPT = "Answer in one sentence. If unsure, say 'I am not sure' instead of guessing."


class DebugState(TypedDict):
    question: str
    answer: str
    mode: str
    latency_ms: float


def build_answer_node(model: BaseChatModel, *, buggy: bool = False):
    prompt = BUGGY_PROMPT if buggy else FIXED_PROMPT

    def answer_node(state: DebugState) -> dict:
        started = time.perf_counter()
        response = model.invoke(
            [
                SystemMessage(content=prompt),
                HumanMessage(content=state["question"]),
            ]
        )
        elapsed = (time.perf_counter() - started) * 1000
        logger.info("Answer node latency: %.1f ms (buggy=%s)", elapsed, buggy)
        return {
            "answer": str(response.content),
            "latency_ms": elapsed,
            "mode": "buggy" if buggy else "fixed",
        }

    return answer_node


def build_debug_graph(model: BaseChatModel, *, buggy: bool = False):
    graph = StateGraph(DebugState)
    graph.add_node("answer", build_answer_node(model, buggy=buggy))
    graph.set_entry_point("answer")
    graph.add_edge("answer", END)
    return graph.compile()
