# Module 05 — Testing and Debugging

Teaches pytest patterns for agents, LangSmith trace inspection, failure/regression tests, and latency awareness.

## Contents

- `graph.py` — side-by-side buggy vs fixed prompt behavior
- `tests/conftest.py` — shared fixtures and markers
- `tests/integration/` — optional live API smoke tests

## Run

```bash
python scripts/run_05_debug.py --question "What is the capital of France?"
python scripts/run_05_debug.py --buggy --question "What is the capital of France?"
```

## Test

```bash
pytest tests/ -v
pytest tests/ -m integration -v   # requires API keys
```
