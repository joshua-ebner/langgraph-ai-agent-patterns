"""LangSmith tracing helpers."""

from __future__ import annotations

import os
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from agent_patterns.config import get_langsmith_project

F = TypeVar("F", bound=Callable[..., Any])


def configure_tracing(*, project: str | None = None, enable: bool = True) -> dict[str, str]:
    """Set LangSmith env vars when tracing is enabled and a key is present."""
    settings: dict[str, str] = {}
    api_key = os.getenv("LANGSMITH_API_KEY")
    if not enable or not api_key:
        settings["LANGSMITH_TRACING"] = "false"
        return settings

    settings["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING", "true")
    settings["LANGSMITH_PROJECT"] = project or get_langsmith_project()
    settings["LANGSMITH_API_KEY"] = api_key
    os.environ.update(settings)
    return settings


def traceable(name: str | None = None) -> Callable[[F], F]:
    """Lightweight decorator that enables tracing when LangSmith is configured."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            configure_tracing()
            return func(*args, **kwargs)

        wrapper.__name__ = name or func.__name__
        return wrapper  # type: ignore[return-value]

    return decorator


def tracing_status_message() -> str:
    """Human-readable tracing hint for CLI scripts."""
    if os.getenv("LANGSMITH_TRACING", "").lower() == "true" and os.getenv("LANGSMITH_API_KEY"):
        project = os.getenv("LANGSMITH_PROJECT", get_langsmith_project())
        return f"LangSmith tracing enabled (project: {project}). Inspect runs at https://smith.langchain.com/"
    return "LangSmith tracing disabled. Set LANGSMITH_API_KEY to capture traces."
