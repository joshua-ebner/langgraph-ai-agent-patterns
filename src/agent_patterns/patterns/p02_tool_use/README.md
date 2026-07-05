# Module 02 — Tool Use

Teaches clear tool definitions, schemas, failure handling, result validation, and tool-vs-respond routing.

## Graph

```mermaid
flowchart LR
  agent[agent] -->|tool_calls| tools[tools]
  agent -->|no tools| respond[respond]
  tools --> validate[validate_tool_results]
  validate --> agent
  respond --> endNode[END]
```

## Run

```bash
python scripts/run_02_tools.py --question "What is LangGraph?"
python scripts/run_02_tools.py --question "Calculate (12 + 8) / 4"
```

## Test

```bash
pytest tests/unit/test_02_tool_use.py -v
```
