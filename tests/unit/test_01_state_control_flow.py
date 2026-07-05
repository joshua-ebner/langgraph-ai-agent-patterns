"""Unit tests for Module 01 routing and parsing."""

from agent_patterns.patterns.p01_state_control_flow.graph import parse_plan, route_after_execute


def test_parse_plan_json_array():
    assert parse_plan('["a", "b"]') == ["a", "b"]


def test_parse_plan_strips_markdown_fence():
    raw = '```json\n["step one", "step two"]\n```'
    assert parse_plan(raw) == ["step one", "step two"]


def test_route_continue():
    state = {
        "step_count": 1,
        "current_step_index": 1,
        "plan": ["a", "b", "c"],
        "max_steps": 10,
    }
    assert route_after_execute(state) == "continue"


def test_route_finish():
    state = {
        "step_count": 3,
        "current_step_index": 3,
        "plan": ["a", "b", "c"],
        "max_steps": 10,
    }
    assert route_after_execute(state) == "finish"


def test_route_stop_at_max_steps():
    state = {
        "step_count": 2,
        "current_step_index": 1,
        "plan": ["a", "b", "c"],
        "max_steps": 2,
    }
    assert route_after_execute(state) == "stop"
