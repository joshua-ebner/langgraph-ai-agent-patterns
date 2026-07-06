export type FieldType = "text" | "number" | "boolean";

export interface PatternField {
  name: string;
  label: string;
  field_type: FieldType;
  default?: string | number | boolean | null;
  required?: boolean;
}

export interface PatternInfo {
  id: string;
  name: string;
  description: string;
  fields: PatternField[];
}

export interface RunResponse {
  pattern_id: string;
  interrupted: boolean;
  thread_id: string | null;
  state: Record<string, unknown>;
}

export interface AgentBriefPayload {
  summary: string;
  key_points: string[];
  confidence: number;
  sources: string[];
}

export interface HitlResumeRequest {
  thread_id: string;
  review_status: "approved" | "rejected" | "edited";
  human_feedback?: string;
  brief?: AgentBriefPayload;
}
