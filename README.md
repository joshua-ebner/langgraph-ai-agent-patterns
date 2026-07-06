# LangGraph AI Agent Patterns

A pattern library for production-oriented LangGraph agents — typed state, reliable tool pipelines, validated structured outputs, human approval gates, and pytest-first testing. Each module is a minimal but realistic workflow you can run and inspect in LangSmith.

## Focus areas

- State and control flow
- Tool use
- Structured outputs
- Human-in-the-loop workflows
- Testing and debugging

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Add OPENAI_API_KEY or ANTHROPIC_API_KEY (and optional LANGSMITH_API_KEY)
```

Optional env vars:

| Variable | Default | Purpose |
|----------|---------|---------|
| `MODEL_PROVIDER` | `openai` | `openai` or `anthropic` |
| `MODEL_NAME` | provider default | Override model id |
| `LANGSMITH_TRACING` | `true` | Enable traces when key is set |
| `LANGSMITH_PROJECT` | `langgraph-ai-agent-patterns` | LangSmith project name |

## Learning path

| Module | Concepts | Run | Test |
|--------|----------|-----|------|
| p01_state_control_flow | Typed state, routing, loops, stopping | `python scripts/run_01_state.py` | `pytest tests/unit/test_01_state_control_flow.py -v` |
| p02_tool_use | Tool schemas, failures, validation | `python scripts/run_02_tools.py` | `pytest tests/unit/test_02_tool_use.py -v` |
| p03_structured_outputs | Pydantic boundaries, retry loops | `python scripts/run_03_structured.py` | `pytest tests/unit/test_03_structured_outputs.py -v` |
| p04_human_in_the_loop | Checkpoints, interrupts, review | `python scripts/run_04_hitl.py --thread-id demo-1` | `pytest tests/unit/test_04_human_in_the_loop.py -v` |
| p05_testing_debugging | pytest, regression, LangSmith | `python scripts/run_05_debug.py` | `pytest tests/ -v` |

Run all unit tests:

```bash
pytest tests/ -v
```

Live API smoke tests (requires keys):

```bash
pytest tests/ -m integration -v
```

## Web UI

Run all five patterns from a React pattern picker backed by FastAPI.

```bash
# Terminal 1 — API
source .venv/bin/activate
pip install -e ".[ui,dev]"
./scripts/run_api.sh

# Terminal 2 — React dev server
cd ui/web
npm install
npm run dev
# open http://localhost:5173
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`. Requires the same `.env` API keys as the CLI scripts.

On macOS, editable installs may not add `src/` to `sys.path` (hidden `.pth` files). `run_api.sh` sets `PYTHONPATH=src:.` automatically.

For a static build served by FastAPI:

```bash
cd ui/web && npm run build
PYTHONPATH=src:. python -m uvicorn ui.api.main:app --port 8000
# open http://localhost:8000
```

See [docs/phase3-ui.md](docs/phase3-ui.md) for architecture notes.

## LangSmith

When `LANGSMITH_API_KEY` is set, CLI scripts enable tracing automatically. Inspect runs at [smith.langchain.com](https://smith.langchain.com/) under project `langgraph-ai-agent-patterns`.

## Repository layout

```
src/agent_patterns/          # Shared config, LLM factory, patterns
scripts/                       # Runnable CLI demos
ui/api/                        # FastAPI backend
ui/web/                        # Vite + React frontend
tests/                         # Unit + integration tests
capstone/                      # Future integrated demo (placeholder)
docs/phase3-ui.md              # Web UI architecture notes
```

Pattern modules live under `src/agent_patterns/patterns/pNN_*` (Python package names use the `pNN_` prefix because module names cannot start with a digit).

## Capstone

Not started. See [capstone/README.md](capstone/README.md) for how future work will compose these patterns.

## Optional web UI

Implemented. See the **Web UI** section above and [docs/phase3-ui.md](docs/phase3-ui.md).
