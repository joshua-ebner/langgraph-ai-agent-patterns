import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchPatterns } from "../api/client";
import type { PatternInfo } from "../types";
import { patternDisplayLabel } from "../utils/patternLabel";

export default function Home() {
  const [patterns, setPatterns] = useState<PatternInfo[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPatterns()
      .then(setPatterns)
      .catch((err: Error) => setError(err.message));
  }, []);

  if (error) {
    return <p className="error">Failed to load patterns: {error}</p>;
  }

  return (
    <section>
      <h1>Choose an AI Agent Pattern</h1>
      <p className="subtitle">
        Run LangGraph workflow demos from the browser. Each card is a self-contained
        agent engineering pattern you can execute and inspect.
      </p>
      <div className="grid">
        {patterns.map((pattern) => (
          <Link key={pattern.id} to={`/patterns/${pattern.id}`} className="card">
            <span className="card-badge">{patternDisplayLabel(pattern.id)}</span>
            <h2>{pattern.name}</h2>
            <p>{pattern.description}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
