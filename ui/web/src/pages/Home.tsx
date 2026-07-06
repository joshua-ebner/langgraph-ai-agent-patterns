import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchPatterns } from "../api/client";
import type { PatternInfo } from "../types";

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
      <h1>Choose a pattern</h1>
      <p className="subtitle">
        Run LangGraph workflow demos from the browser. Each pattern maps to a module in{" "}
        <code>src/agent_patterns/patterns/</code>.
      </p>
      <div className="grid">
        {patterns.map((pattern) => (
          <Link key={pattern.id} to={`/patterns/${pattern.id}`} className="card">
            <span className="card-id">{pattern.id}</span>
            <h2>{pattern.name}</h2>
            <p>{pattern.description}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
