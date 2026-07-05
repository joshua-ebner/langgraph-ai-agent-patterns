"""Regression and meta tests for Module 05."""

from agent_patterns.patterns.p01_state_control_flow.graph import PLANNER_SYSTEM_PROMPT
from agent_patterns.patterns.p05_testing_debugging.graph import BUGGY_PROMPT, FIXED_PROMPT
from agent_patterns.testing.mock_llm import ScriptedChatModel


def test_planner_prompt_regression_snapshot():
    assert "JSON array" in PLANNER_SYSTEM_PROMPT
    assert "2-4" in PLANNER_SYSTEM_PROMPT


def test_debug_prompts_differ():
    assert BUGGY_PROMPT != FIXED_PROMPT
    assert "not sure" in FIXED_PROMPT.lower()


def test_scripted_chat_model_returns_sequence():
    model = ScriptedChatModel(responses=["first", "second"])
    assert model.invoke("hi").content == "first"
    assert model.invoke("hi").content == "second"
