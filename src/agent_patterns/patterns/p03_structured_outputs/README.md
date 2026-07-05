# Module 03 — Structured Outputs

Teaches Pydantic validation at workflow boundaries, retry loops, and separating scratchpad/actions/final output.

## Graph

```mermaid
flowchart LR
  generate[generate] --> validate[validate]
  validate -->|valid| finalize[finalize]
  validate -->|invalid| retry[retry]
  retry --> generate
  validate -->|max retries| escalate[escalate]
```

## Run

```bash
python scripts/run_03_structured.py --topic "LangGraph checkpointing"
```

## Test

```bash
pytest tests/unit/test_03_structured_outputs.py -v
```
