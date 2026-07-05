# Phase 3 — Optional Web UI (Deferred)

This document describes a future UI layer. **No UI code ships in the initial pattern library.**

## Goal

Wrap existing LangGraph workflows (especially Module 04 human-in-the-loop) with a thin web interface suitable for portfolio demos — without changing graph logic.

## Proposed layout

```
ui/
├── api/
│   └── main.py       # FastAPI: POST /run, POST /resume
└── web/
    └── ...           # Minimal frontend (Vite/React or HTMX)
```

## API sketch

| Endpoint | Purpose |
|----------|---------|
| `POST /run` | Start a graph with `{ pattern, thread_id, input }` |
| `POST /resume` | Resume after interrupt with `{ thread_id, review_status, edits? }` |
| `GET /state/{thread_id}` | Fetch checkpoint state for review UI |

## Implementation notes

- Import compiled graphs from `agent_patterns.patterns.p04_human_in_the_loop.graph`.
- Reuse `MemorySaver` or `SqliteSaver` with stable `thread_id` values.
- Keep business logic in `src/`; UI only orchestrates invoke/resume and renders `final_brief`.
- Module 04 CLI (`scripts/run_04_hitl.py`) is the reference interaction model.

## When to build

After Module 04 CLI works end-to-end and unit tests pass. The HITL module benefits most from approve/reject/edit buttons in a browser.
