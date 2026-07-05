"""Multi-step planner graph demonstrating state, routing, and loops."""

from __future__ import annotations

import json
import logging
import re

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from agent_patterns.patterns.p01_state_control_flow.models import PlannerState

logger = logging.getLogger(__name__)

PLANNER_SYSTEM_PROMPT = (
    "You are a planning assistant. Given a user goal, return a JSON array "
    "of 2-4 short actionable steps. Return ONLY valid JSON, "
    'e.g. ["step one", "step two"]. No markdown.'
)


def parse_plan(raw: str) -> list[str]:
    """Parse model output into a list of plan steps."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    data = json.loads(cleaned)
    if not isinstance(data, list) or not data:
        raise ValueError("Plan must be a non-empty JSON array")
    return [str(step) for step in data]


def create_plan_node(model: BaseChatModel):
    def create_plan(state: PlannerState) -> dict:
        user_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
        goal = user_messages[-1].content if user_messages else "No goal provided"
        response = model.invoke(
            [
                SystemMessage(content=PLANNER_SYSTEM_PROMPT),
                HumanMessage(content=f"Goal: {goal}"),
            ]
        )
        plan = parse_plan(str(response.content))
        logger.info("Created plan with %s steps", len(plan))
        return {
            "plan": plan,
            "current_step_index": 0,
            "step_count": 0,
            "status": "executing",
            "messages": [AIMessage(content=f"Plan created: {plan}")],
        }

    return create_plan


def execute_step(state: PlannerState) -> dict:
    """Execute the current plan step and advance the index."""
    index = state["current_step_index"]
    plan = state["plan"]
    if index >= len(plan):
        return {"status": "done"}

    step = plan[index]
    logger.info("Executing step %s: %s", index + 1, step)
    return {
        "current_step_index": index + 1,
        "step_count": state["step_count"] + 1,
        "messages": [AIMessage(content=f"Completed step {index + 1}: {step}")],
    }


def route_after_execute(state: PlannerState) -> str:
    """Pure routing function: loop, finish, or stop at max steps."""
    if state["step_count"] >= state["max_steps"]:
        return "stop"
    if state["current_step_index"] >= len(state["plan"]):
        return "finish"
    return "continue"


def finalize(state: PlannerState) -> dict:
    hit_max = state["step_count"] >= state["max_steps"]
    steps_remain = state["current_step_index"] < len(state["plan"])
    if hit_max and steps_remain:
        status = "max_steps_reached"
        message = AIMessage(
            content=(
                f"Stopped after {state['step_count']} steps "
                f"({len(state['plan']) - state['current_step_index']} remaining)."
            )
        )
    else:
        status = "done"
        message = AIMessage(content="All planned steps completed.")
    return {"status": status, "messages": [message]}


def build_planner_graph(model: BaseChatModel):
    graph = StateGraph(PlannerState)
    graph.add_node("create_plan", create_plan_node(model))
    graph.add_node("execute_step", execute_step)
    graph.add_node("finalize", finalize)

    graph.set_entry_point("create_plan")
    graph.add_edge("create_plan", "execute_step")
    graph.add_conditional_edges(
        "execute_step",
        route_after_execute,
        {
            "continue": "execute_step",
            "finish": "finalize",
            "stop": "finalize",
        },
    )
    graph.add_edge("finalize", END)
    return graph.compile()
