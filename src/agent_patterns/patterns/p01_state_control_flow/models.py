"""State models for the planner control-flow pattern."""

from __future__ import annotations

from typing import Annotated, Literal

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

PlannerStatus = Literal["planning", "executing", "done", "max_steps_reached"]


class PlannerState(TypedDict):
    """Graph state for the multi-step planner demo."""

    messages: Annotated[list, add_messages]
    plan: list[str]
    step_count: int
    current_step_index: int
    status: PlannerStatus
    max_steps: int
