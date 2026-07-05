"""Models for structured agent outputs."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field
from typing_extensions import TypedDict

ReviewStatus = Literal["pending", "approved", "rejected", "edited"]
WorkflowStatus = Literal["generating", "valid", "invalid", "escalated", "done"]


class ToolAction(BaseModel):
    name: str
    detail: str


class AgentBrief(BaseModel):
    summary: str = Field(min_length=10)
    key_points: list[str] = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    sources: list[str] = Field(default_factory=list)


class StructuredOutputState(TypedDict):
    topic: str
    scratchpad: str
    actions: list[ToolAction]
    draft_brief: dict | None
    final_brief: AgentBrief | None
    validation_errors: list[str]
    retry_count: int
    max_retries: int
    status: WorkflowStatus
