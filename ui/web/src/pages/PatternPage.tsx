import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchPattern, runPattern } from "../api/client";
import HitlReview from "../components/HitlReview";
import PatternForm from "../components/PatternForm";
import ResultView from "../components/ResultView";
import type { PatternInfo, RunResponse } from "../types";
import { patternDisplayLabel } from "../utils/patternLabel";

export default function PatternPage() {
  const { patternId = "" } = useParams();
  const [pattern, setPattern] = useState<PatternInfo | null>(null);
  const [result, setResult] = useState<RunResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setResult(null);
    setError(null);
    fetchPattern(patternId)
      .then(setPattern)
      .catch((err: Error) => setError(err.message));
  }, [patternId]);

  async function handleRun(inputs: Record<string, unknown>) {
    setLoading(true);
    setError(null);
    try {
      const response = await runPattern(patternId, inputs);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Run failed");
    } finally {
      setLoading(false);
    }
  }

  if (error && !pattern) {
    return <p className="error">{error}</p>;
  }

  if (!pattern) {
    return <p>Loading pattern...</p>;
  }

  return (
    <section>
      <Link to="/" className="back-link">
        Back to patterns
      </Link>
      <h1>
        {patternDisplayLabel(pattern.id)} — {pattern.name}
      </h1>
      <p className="subtitle">{pattern.description}</p>

      <PatternForm pattern={pattern} loading={loading} onSubmit={handleRun} />

      {error ? <p className="error">{error}</p> : null}

      {result && !result.interrupted ? (
        <ResultView patternId={pattern.id} state={result.state} />
      ) : null}

      {result?.interrupted && result.thread_id ? (
        <HitlReview
          threadId={result.thread_id}
          state={result.state}
          onComplete={setResult}
          onError={setError}
        />
      ) : null}
    </section>
  );
}
