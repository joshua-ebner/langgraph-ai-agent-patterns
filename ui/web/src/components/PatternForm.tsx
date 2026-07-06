import { useEffect, useMemo, useState } from "react";
import type { PatternInfo } from "../types";

interface PatternFormProps {
  pattern: PatternInfo;
  loading: boolean;
  onSubmit: (inputs: Record<string, unknown>) => void;
}

function initialValues(pattern: PatternInfo): Record<string, unknown> {
  const values: Record<string, unknown> = {};
  for (const field of pattern.fields) {
    values[field.name] = field.default ?? (field.field_type === "boolean" ? false : "");
  }
  return values;
}

export default function PatternForm({ pattern, loading, onSubmit }: PatternFormProps) {
  const defaults = useMemo(() => initialValues(pattern), [pattern]);
  const [values, setValues] = useState<Record<string, unknown>>(defaults);

  useEffect(() => {
    setValues(defaults);
  }, [pattern.id, defaults]);

  function handleChange(name: string, raw: string | boolean) {
    setValues((current) => ({ ...current, [name]: raw }));
  }

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const parsed: Record<string, unknown> = {};
    for (const field of pattern.fields) {
      const raw = values[field.name];
      if (field.field_type === "number") {
        parsed[field.name] = Number(raw);
      } else if (field.field_type === "boolean") {
        parsed[field.name] = Boolean(raw);
      } else {
        parsed[field.name] = String(raw ?? "");
      }
    }
    onSubmit(parsed);
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      {pattern.fields.map((field) => (
        <label key={field.name} className="field">
          <span>{field.label}</span>
          {field.field_type === "boolean" ? (
            <input
              type="checkbox"
              checked={Boolean(values[field.name])}
              onChange={(event) => handleChange(field.name, event.target.checked)}
            />
          ) : (
            <input
              type={field.field_type === "number" ? "number" : "text"}
              value={String(values[field.name] ?? "")}
              onChange={(event) => handleChange(field.name, event.target.value)}
              required={field.required !== false}
            />
          )}
        </label>
      ))}
      <button type="submit" disabled={loading}>
        {loading ? "Running..." : "Run pattern"}
      </button>
    </form>
  );
}
