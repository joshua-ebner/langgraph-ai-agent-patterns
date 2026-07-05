"""Unit tests for Module 02 tool routing and validation."""

import json

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from agent_patterns.patterns.p02_tool_use.graph import (
    route_after_agent,
    validate_tool_results,
)
from agent_patterns.patterns.p02_tool_use.tools import calculate, lookup_fact


def test_lookup_fact():
    assert "LangGraph" in lookup_fact.invoke({"query": "langgraph"})


def test_calculate():
    assert calculate.invoke({"expression": "(2 + 3) * 4"}) == 20.0


def test_route_after_agent_with_tools():
    state = {
        "messages": [
            HumanMessage(content="hi"),
            AIMessage(content="", tool_calls=[{"name": "lookup_fact", "args": {}, "id": "1"}]),
        ]
    }
    assert route_after_agent(state) == "tools"


def test_route_after_agent_without_tools():
    state = {"messages": [AIMessage(content="done")]}
    assert route_after_agent(state) == "respond"


def test_validate_accepts_search_payload():
    payload = {
        "query": "langgraph",
        "results": [{"title": "langgraph", "snippet": "...", "score": 0.9}],
    }
    state = {
        "messages": [ToolMessage(content=json.dumps(payload), tool_call_id="1")],
    }
    result = validate_tool_results(state)
    assert result["validation_status"] == "valid"


def test_validate_records_tool_errors():
    state = {
        "messages": [
            ToolMessage(content="Tool error (calculate): bad", tool_call_id="1", status="error")
        ],
    }
    result = validate_tool_results(state)
    assert result["validation_status"] == "invalid"
    assert result["validation_errors"]
