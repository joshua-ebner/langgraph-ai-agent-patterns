# Module 04 — Human-in-the-Loop

Teaches approval checkpoints, review states, manual correction, and low-confidence escalation with checkpointing.

## Graph

```mermaid
flowchart LR
  validate[validate] --> checkConfidence[check_confidence]
  checkConfidence -->|low confidence| escalateReview[escalate_review]
  checkConfidence --> humanReview[human_review]
  escalateReview --> humanReview
  humanReview -->|approved/edited| finalize[finalize]
  humanReview -->|rejected| retry[retry]
```

The graph interrupts **before** `human_review`. Resume with a review decision via CLI.

## Run

```bash
python scripts/run_04_hitl.py --thread-id demo-1 --topic "LangGraph HITL patterns"
```

When interrupted, choose approve (`a`), reject (`r`), or edit (`e`).

## Test

```bash
pytest tests/unit/test_04_human_in_the_loop.py -v
```
