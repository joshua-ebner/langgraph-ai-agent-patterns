import { useState } from "react";
import { resumeHitl } from "../api/client";
import type { AgentBriefPayload, RunResponse } from "../types";
import ResultView from "./ResultView";

interface HitlReviewProps {
  threadId: string;
  state: Record<string, unknown>;
  onComplete: (response: RunResponse) => void;
  onError: (message: string) => void;
}

export default function HitlReview({ threadId, state, onComplete, onError }: HitlReviewProps) {
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<"approve" | "reject" | "edit" | null>(null);
  const [feedback, setFeedback] = useState("");
  const [brief, setBrief] = useState<AgentBriefPayload>(() => {
    const existing = state.final_brief as AgentBriefPayload | null | undefined;
    return {
      summary: existing?.summary ?? "",
      key_points: existing?.key_points ?? [""],
      confidence: existing?.confidence ?? 0.85,
      sources: existing?.sources ?? [],
    };
  });

  async function submit(reviewStatus: "approved" | "rejected" | "edited") {
    setLoading(true);
    try {
      const response = await resumeHitl({
        thread_id: threadId,
        review_status: reviewStatus,
        human_feedback: feedback,
        brief: reviewStatus === "edited" ? brief : undefined,
      });
      onComplete(response);
    } catch (err) {
      onError(err instanceof Error ? err.message : "Resume failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="hitl">
      <h2>Human review required</h2>
      {state.human_feedback ? <p className="notice">{String(state.human_feedback)}</p> : null}
      <ResultView patternId="p04" state={state} />

      <div className="hitl-actions">
        <button type="button" disabled={loading} onClick={() => submit("approved")}>
          Approve
        </button>
        <button type="button" disabled={loading} onClick={() => setMode("reject")}>
          Reject
        </button>
        <button type="button" disabled={loading} onClick={() => setMode("edit")}>
          Edit
        </button>
      </div>

      {mode === "reject" ? (
        <div className="hitl-form">
          <label className="field">
            <span>Rejection reason</span>
            <input value={feedback} onChange={(event) => setFeedback(event.target.value)} />
          </label>
          <button type="button" disabled={loading} onClick={() => submit("rejected")}>
            Submit rejection
          </button>
        </div>
      ) : null}

      {mode === "edit" ? (
        <div className="hitl-form">
          <label className="field">
            <span>Summary</span>
            <textarea
              value={brief.summary}
              onChange={(event) => setBrief({ ...brief, summary: event.target.value })}
              rows={4}
            />
          </label>
          <label className="field">
            <span>Key points (comma-separated)</span>
            <input
              value={brief.key_points.join(", ")}
              onChange={(event) =>
                setBrief({
                  ...brief,
                  key_points: event.target.value.split(",").map((part) => part.trim()).filter(Boolean),
                })
              }
            />
          </label>
          <label className="field">
            <span>Confidence (0-1)</span>
            <input
              type="number"
              min={0}
              max={1}
              step={0.01}
              value={brief.confidence}
              onChange={(event) =>
                setBrief({ ...brief, confidence: Number(event.target.value) })
              }
            />
          </label>
          <label className="field">
            <span>Sources (comma-separated)</span>
            <input
              value={brief.sources.join(", ")}
              onChange={(event) =>
                setBrief({
                  ...brief,
                  sources: event.target.value.split(",").map((part) => part.trim()).filter(Boolean),
                })
              }
            />
          </label>
          <button type="button" disabled={loading} onClick={() => submit("edited")}>
            Submit edits
          </button>
        </div>
      ) : null}
    </section>
  );
}
