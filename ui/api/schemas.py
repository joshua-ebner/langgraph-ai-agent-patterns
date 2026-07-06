"""API request and response models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

FieldType = Literal["text", "number", "boolean"]


class PatternField(BaseModel):
    name: str
    label: str
    field_type: FieldType = "text"
    default: str | int | float | bool | None = None
    required: bool = True


class PatternInfo(BaseModel):
    id: str
    name: str
    description: str
    fields: list[PatternField]


class RunRequest(BaseModel):
    inputs: dict[str, Any] = Field(default_factory=dict)


class AgentBriefPayload(BaseModel):
    summary: str
    key_points: list[str]
    confidence: float = Field(ge=0.0, le=1.0)
    sources: list[str] = Field(default_factory=list)


class HitlResumeRequest(BaseModel):
    thread_id: str
    review_status: Literal["approved", "rejected", "edited"]
    human_feedback: str = ""
    brief: AgentBriefPayload | None = None


class RunResponse(BaseModel):
    pattern_id: str
    interrupted: bool = False
    thread_id: str | None = None
    state: dict[str, Any]
