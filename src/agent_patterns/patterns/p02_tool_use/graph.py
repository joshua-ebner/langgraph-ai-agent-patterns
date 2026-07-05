"""Tool-using agent with error handling and result validation."""

from __future__ import annotations

import json
import logging

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langgraph.graph import END, StateGraph

from agent_patterns.patterns.p02_tool_use.models import ToolAgentState
from agent_patterns.patterns.p02_tool_use.tools import ALL_TOOLS, SearchResponse

logger = logging.getLogger(__name__)

AGENT_SYSTEM_PROMPT = """You are a helpful assistant with access to tools.
Use tools when you need facts, calculations, or structured search results.
When you have enough information, respond directly without calling tools."""


def build_agent_node(model: BaseChatModel):
    bound = model.bind_tools(ALL_TOOLS)

    def agent(state: ToolAgentState) -> dict:
        messages = [SystemMessage(content=AGENT_SYSTEM_PROMPT), *state["messages"]]
        response = bound.invoke(messages)
        tool_call_count = state.get("tool_call_count", 0)
        if isinstance(response, AIMessage) and response.tool_calls:
            tool_call_count += len(response.tool_calls)
        return {
            "messages": [response],
            "tool_call_count": tool_call_count,
            "validation_status": "pending",
            "validation_errors": [],
        }

    return agent


def run_tools(state: ToolAgentState) -> dict:
    """Execute tools and capture failures as tool messages."""
    last = state["messages"][-1]
    if not isinstance(last, AIMessage) or not last.tool_calls:
        return {}

    outputs: list[ToolMessage] = []
    tools_by_name = {t.name: t for t in ALL_TOOLS}
    for call in last.tool_calls:
        name = call["name"]
        tool = tools_by_name.get(name)
        if tool is None:
            outputs.append(
                ToolMessage(
                    content=f"Unknown tool: {name}",
                    tool_call_id=call["id"],
                    status="error",
                )
            )
            continue
        try:
            result = tool.invoke(call["args"])
            content = result if isinstance(result, str) else json.dumps(result)
            outputs.append(ToolMessage(content=content, tool_call_id=call["id"]))
        except Exception as exc:
            logger.warning("Tool %s failed: %s", name, exc)
            outputs.append(
                ToolMessage(
                    content=f"Tool error ({name}): {exc}",
                    tool_call_id=call["id"],
                    status="error",
                )
            )
    return {"messages": outputs}


def validate_tool_results(state: ToolAgentState) -> dict:
    """Validate structured tool outputs before returning control to the agent."""
    errors: list[str] = []
    for message in reversed(state["messages"]):
        if not isinstance(message, ToolMessage):
            break
        if message.status == "error":
            errors.append(message.content)
            continue
        try:
            payload = json.loads(message.content)
        except json.JSONDecodeError:
            continue
        if "results" in payload:
            SearchResponse.model_validate(payload)

    if errors:
        return {"validation_status": "invalid", "validation_errors": errors}
    return {"validation_status": "valid", "validation_errors": []}


def route_after_agent(state: ToolAgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return "respond"



def respond(state: ToolAgentState) -> dict:
    last = state["messages"][-1]
    if isinstance(last, AIMessage):
        return {"messages": [last]}
    return {}


def build_tool_agent_graph(model: BaseChatModel):
    graph = StateGraph(ToolAgentState)
    graph.add_node("agent", build_agent_node(model))
    graph.add_node("tools", run_tools)
    graph.add_node("validate", validate_tool_results)
    graph.add_node("respond", respond)

    graph.set_entry_point("agent")
    graph.add_conditional_edges(
        "agent",
        route_after_agent,
        {"tools": "tools", "respond": "respond"},
    )
    graph.add_edge("tools", "validate")
    graph.add_edge("validate", "agent")
    graph.add_edge("respond", END)
    return graph.compile()
