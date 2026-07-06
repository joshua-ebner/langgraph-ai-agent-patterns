"""Graph invoke/resume helpers and state serialization."""

from __future__ import annotations

import uuid
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel

from agent_patterns.llm import get_chat_model
from agent_patterns.patterns.p01_state_control_flow.graph import build_planner_graph
from agent_patterns.patterns.p02_tool_use.graph import build_tool_agent_graph
from agent_patterns.patterns.p03_structured_outputs.graph import build_structured_output_graph
from agent_patterns.patterns.p03_structured_outputs.models import AgentBrief
from agent_patterns.patterns.p04_human_in_the_loop.graph import build_hitl_graph
from agent_patterns.patterns.p05_testing_debugging.graph import build_debug_graph
from agent_patterns.tracing import configure_tracing
from ui.api.registry import get_pattern
from ui.api.schemas import HitlResumeRequest, RunResponse


def serialize_value(value: Any) -> Any:
    if isinstance(value, BaseMessage):
        return {"type": value.type, "content": value.content}
    if isinstance(value, BaseModel):
        return value.model_dump()
    if isinstance(value, list):
        return [serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: serialize_value(item) for key, item in value.items()}
    return value


def serialize_state(state: dict[str, Any]) -> dict[str, Any]:
    return {key: serialize_value(value) for key, value in state.items()}


class GraphRunner:
    """Runs compiled pattern graphs and serializes results for the API."""

    def __init__(self, model: BaseChatModel | None = None) -> None:
        configure_tracing()
        self._model = model
        self._checkpointer = MemorySaver()
        self._graphs: dict[str, Any] = {}

    @property
    def model(self) -> BaseChatModel:
        if self._model is None:
            self._model = get_chat_model()
        return self._model

    def _get_graph(self, pattern_id: str):
        if pattern_id in self._graphs:
            return self._graphs[pattern_id]

        if pattern_id == "p01":
            graph = build_planner_graph(self.model)
        elif pattern_id == "p02":
            graph = build_tool_agent_graph(self.model)
        elif pattern_id == "p03":
            graph = build_structured_output_graph(self.model)
        elif pattern_id == "p04":
            graph = build_hitl_graph(self.model, checkpointer=self._checkpointer)
        elif pattern_id == "p05":
            graph = build_debug_graph(self.model)
        else:
            raise KeyError(f"Unknown pattern: {pattern_id}")

        self._graphs[pattern_id] = graph
        return graph

    def _build_initial_state(self, pattern_id: str, inputs: dict[str, Any]) -> dict[str, Any]:
        if pattern_id == "p01":
            return {
                "messages": [HumanMessage(content=str(inputs.get("goal", "")))],
                "plan": [],
                "step_count": 0,
                "current_step_index": 0,
                "status": "planning",
                "max_steps": int(inputs.get("max_steps", 10)),
            }
        if pattern_id == "p02":
            return {
                "messages": [HumanMessage(content=str(inputs.get("question", "")))],
                "validation_status": "pending",
                "validation_errors": [],
                "tool_call_count": 0,
            }
        if pattern_id == "p03":
            return {
                "topic": str(inputs.get("topic", "")),
                "scratchpad": "",
                "actions": [],
                "draft_brief": None,
                "final_brief": None,
                "validation_errors": [],
                "retry_count": 0,
                "max_retries": int(inputs.get("max_retries", 2)),
                "status": "generating",
            }
        if pattern_id == "p04":
            thread_id = str(inputs.get("thread_id") or uuid.uuid4().hex[:8])
            inputs["thread_id"] = thread_id
            return {
                "topic": str(inputs.get("topic", "")),
                "scratchpad": "",
                "actions": [],
                "draft_brief": None,
                "final_brief": None,
                "validation_errors": [],
                "retry_count": 0,
                "max_retries": int(inputs.get("max_retries", 2)),
                "status": "generating",
                "review_status": "pending",
                "human_feedback": "",
                "requires_escalation": False,
                "confidence_threshold": 0.7,
            }
        if pattern_id == "p05":
            return {
                "question": str(inputs.get("question", "")),
                "answer": "",
                "mode": "",
                "latency_ms": 0.0,
            }
        raise KeyError(f"Unknown pattern: {pattern_id}")

    def run(self, pattern_id: str, inputs: dict[str, Any]) -> RunResponse:
        get_pattern(pattern_id)
        graph = self._get_graph(pattern_id)
        state = self._build_initial_state(pattern_id, inputs)

        if pattern_id == "p04":
            thread_id = str(inputs["thread_id"])
            config = {"configurable": {"thread_id": thread_id}}
            graph.invoke(state, config=config)
            return self._hitl_response(thread_id, graph, config)

        if pattern_id == "p05":
            graph = build_debug_graph(self.model, buggy=bool(inputs.get("buggy", False)))
            self._graphs[pattern_id] = graph
            result = graph.invoke(state)
            return RunResponse(pattern_id=pattern_id, state=serialize_state(result))

        result = graph.invoke(state)
        return RunResponse(pattern_id=pattern_id, state=serialize_state(result))

    def _hitl_response(self, thread_id: str, graph, config: dict[str, Any]) -> RunResponse:
        snapshot = graph.get_state(config)
        interrupted = bool(snapshot.next)
        return RunResponse(
            pattern_id="p04",
            interrupted=interrupted,
            thread_id=thread_id,
            state=serialize_state(snapshot.values),
        )

    def get_hitl_state(self, thread_id: str) -> RunResponse:
        graph = self._get_graph("p04")
        config = {"configurable": {"thread_id": thread_id}}
        snapshot = graph.get_state(config)
        if not snapshot.values:
            raise KeyError(f"No checkpoint found for thread_id={thread_id}")
        return self._hitl_response(thread_id, graph, config)

    def resume_hitl(self, request: HitlResumeRequest) -> RunResponse:
        graph = self._get_graph("p04")
        config = {"configurable": {"thread_id": request.thread_id}}
        update: dict[str, Any] = {"review_status": request.review_status}
        if request.human_feedback:
            update["human_feedback"] = request.human_feedback
        if request.brief is not None:
            update["final_brief"] = AgentBrief.model_validate(request.brief.model_dump())
        graph.update_state(config, update)
        graph.invoke(None, config=config)
        return self._hitl_response(request.thread_id, graph, config)
