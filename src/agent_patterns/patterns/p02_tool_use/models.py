"""State models for the tool-use pattern."""

from __future__ import annotations

from typing import Annotated, Literal

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

ValidationStatus = Literal["pending", "valid", "invalid"]


class ToolAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    validation_status: ValidationStatus
    validation_errors: list[str]
    tool_call_count: int
