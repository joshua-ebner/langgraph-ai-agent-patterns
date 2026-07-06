"""Pattern metadata registry."""

from __future__ import annotations

from ui.api.schemas import PatternField, PatternInfo

PATTERNS: list[PatternInfo] = [
    PatternInfo(
        id="p01",
        name="State and Control Flow",
        description="Multi-step planner with typed state, routing loops, and max-step stopping.",
        fields=[
            PatternField(
                name="goal",
                label="Goal",
                field_type="text",
                default="Prepare a concise project status update",
            ),
            PatternField(
                name="max_steps",
                label="Max steps",
                field_type="number",
                default=10,
            ),
        ],
    ),
    PatternInfo(
        id="p02",
        name="Tool Use",
        description="Agent with mock tools, error handling, and result validation.",
        fields=[
            PatternField(
                name="question",
                label="Question",
                field_type="text",
                default="Look up a fact about LangGraph and summarize it.",
            ),
        ],
    ),
    PatternInfo(
        id="p03",
        name="Structured Outputs",
        description="Pydantic-validated brief with retry and escalation loops.",
        fields=[
            PatternField(
                name="topic",
                label="Topic",
                field_type="text",
                default="Benefits of typed LangGraph state",
            ),
            PatternField(
                name="max_retries",
                label="Max retries",
                field_type="number",
                default=2,
            ),
        ],
    ),
    PatternInfo(
        id="p04",
        name="Human-in-the-Loop",
        description="Checkpointed approval workflow with low-confidence escalation.",
        fields=[
            PatternField(
                name="topic",
                label="Topic",
                field_type="text",
                default="Human approval workflows in LangGraph",
            ),
            PatternField(
                name="thread_id",
                label="Thread ID",
                field_type="text",
                default="demo-1",
            ),
            PatternField(
                name="max_retries",
                label="Max retries",
                field_type="number",
                default=2,
            ),
        ],
    ),
    PatternInfo(
        id="p05",
        name="Testing and Debugging",
        description="Buggy vs fixed prompt comparison with latency logging.",
        fields=[
            PatternField(
                name="question",
                label="Question",
                field_type="text",
                default="Explain why agent tests should mock the LLM.",
            ),
            PatternField(
                name="buggy",
                label="Use buggy prompt",
                field_type="boolean",
                default=False,
                required=False,
            ),
        ],
    ),
]

PATTERN_BY_ID = {pattern.id: pattern for pattern in PATTERNS}


def get_pattern(pattern_id: str) -> PatternInfo:
    pattern = PATTERN_BY_ID.get(pattern_id)
    if pattern is None:
        raise KeyError(f"Unknown pattern: {pattern_id}")
    return pattern
