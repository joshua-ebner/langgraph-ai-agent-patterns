"""Mock tools for the tool-use pattern."""

from __future__ import annotations

import ast
import operator
from typing import Any

from langchain_core.tools import tool
from pydantic import BaseModel, Field

FACT_DB: dict[str, str] = {
    "langgraph": "LangGraph is a library for building stateful agent workflows as graphs.",
    "python": "Python is a general-purpose programming language.",
    "pytest": "pytest is a testing framework for Python.",
}


class SearchResult(BaseModel):
    title: str
    snippet: str
    score: float = Field(ge=0.0, le=1.0)


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]


@tool
def lookup_fact(query: str) -> str:
    """Look up a short fact from a local knowledge base by keyword."""
    key = query.strip().lower()
    if key not in FACT_DB:
        return f"No fact found for '{query}'."
    return FACT_DB[key]


@tool
def calculate(expression: str) -> float:
    """Evaluate a basic arithmetic expression with +, -, *, / and parentheses."""
    allowed_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.USub: operator.neg,
    }

    def _eval(node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.UnaryOp) and type(node.op) in allowed_ops:
            return allowed_ops[type(node.op)](_eval(node.operand))
        if isinstance(node, ast.BinOp) and type(node.op) in allowed_ops:
            return allowed_ops[type(node.op)](_eval(node.left), _eval(node.right))
        raise ValueError(f"Unsupported expression: {expression}")

    tree = ast.parse(expression, mode="eval")
    return _eval(tree.body)


@tool
def search(query: str) -> dict[str, Any]:
    """Search a mock index and return structured results."""
    normalized = query.strip().lower()
    results = [
        SearchResult(title=key, snippet=value[:80], score=0.9 - idx * 0.1)
        for idx, (key, value) in enumerate(FACT_DB.items())
        if normalized in key or normalized in value.lower()
    ]
    if not results:
        results = [SearchResult(title="none", snippet="No matches", score=0.0)]
    payload = SearchResponse(query=query, results=results[:3])
    return payload.model_dump()


ALL_TOOLS = [lookup_fact, calculate, search]
