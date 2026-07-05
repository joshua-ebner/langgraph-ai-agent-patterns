# Capstone (Future)

This directory is reserved for a future integrated demo that composes patterns from `src/agent_patterns/patterns/` into one cohesive workflow.

## Planned composition

| Pattern module | Capstone role |
|----------------|---------------|
| p01_state_control_flow | Multi-step orchestration backbone |
| p02_tool_use | External lookups and calculations |
| p03_structured_outputs | Validated final deliverable |
| p04_human_in_the_loop | Approval gate before publish |

## Status

**Not started.** Pick a domain (research ops, support triage, code review, etc.) when you are ready and wire existing graphs together rather than rewriting them.

## Suggested next step

1. Choose a user-facing scenario with a clear input/output artifact.
2. Import compiled graphs or shared nodes from pattern modules.
3. Add a thin CLI or web UI entry point in `capstone/` or `ui/`.
