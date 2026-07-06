# Web UI — Pattern Picker

The web UI wraps all five LangGraph pattern modules with a FastAPI backend and Vite/React frontend.

## Layout

```
ui/
├── api/
│   ├── main.py       # FastAPI app, CORS, optional static file serving
│   ├── registry.py   # Pattern metadata for picker + forms
│   ├── runner.py     # Graph invoke/resume + state serialization
│   └── schemas.py    # Pydantic API models
└── web/
    └── src/          # React pattern picker, forms, HITL review panel
```

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/patterns` | List patterns (id, name, description, fields) |
| `GET` | `/api/patterns/{id}` | Pattern metadata |
| `POST` | `/api/patterns/{id}/run` | Run a pattern |
| `GET` | `/api/patterns/p04/state/{thread_id}` | Fetch paused HITL checkpoint |
| `POST` | `/api/patterns/p04/resume` | Resume HITL with approve/reject/edit |

## Design notes

- Graph logic stays in `src/agent_patterns/patterns/` — the API only orchestrates invoke/resume.
- Module 04 uses a shared in-process `MemorySaver` so `thread_id` resume works across HTTP requests.
- CLI scripts in `scripts/` remain the terminal-first entry point.

## Run

See the **Web UI** section in [README.md](../README.md).
