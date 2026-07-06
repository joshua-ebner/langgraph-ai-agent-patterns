interface ResultViewProps {
  patternId: string;
  state: Record<string, unknown>;
}

function renderMessages(messages: unknown) {
  if (!Array.isArray(messages)) return null;
  return (
    <ul>
      {messages.map((message, index) => (
        <li key={index}>
          {typeof message === "string"
            ? message
            : typeof message === "object" && message && "content" in message
              ? String((message as { content: unknown }).content)
              : JSON.stringify(message)}
        </li>
      ))}
    </ul>
  );
}

export default function ResultView({ patternId, state }: ResultViewProps) {
  return (
    <section className="results">
      <h2>Result</h2>

      {patternId === "p01" ? (
        <>
          <p>
            <strong>Status:</strong> {String(state.status)}
          </p>
          <p>
            <strong>Step count:</strong> {String(state.step_count)}
          </p>
          <h3>Plan</h3>
          <pre>{JSON.stringify(state.plan, null, 2)}</pre>
          <h3>Messages</h3>
          {renderMessages(state.messages)}
        </>
      ) : null}

      {patternId === "p02" ? (
        <>
          <p>
            <strong>Tool calls:</strong> {String(state.tool_call_count)}
          </p>
          <h3>Messages</h3>
          {renderMessages(state.messages)}
        </>
      ) : null}

      {patternId === "p03" || patternId === "p04" ? (
        <>
          <p>
            <strong>Status:</strong> {String(state.status)}
          </p>
          {state.scratchpad ? (
            <>
              <h3>Scratchpad</h3>
              <pre>{String(state.scratchpad)}</pre>
            </>
          ) : null}
          <h3>Final brief</h3>
          <pre>{JSON.stringify(state.final_brief, null, 2)}</pre>
          {state.validation_errors ? (
            <>
              <h3>Validation errors</h3>
              <pre>{JSON.stringify(state.validation_errors, null, 2)}</pre>
            </>
          ) : null}
        </>
      ) : null}

      {patternId === "p05" ? (
        <>
          <p>
            <strong>Mode:</strong> {String(state.mode)}
          </p>
          <p>
            <strong>Latency:</strong> {String(state.latency_ms)} ms
          </p>
          <h3>Answer</h3>
          <pre>{String(state.answer)}</pre>
        </>
      ) : null}

      <details>
        <summary>Raw state JSON</summary>
        <pre>{JSON.stringify(state, null, 2)}</pre>
      </details>
    </section>
  );
}
