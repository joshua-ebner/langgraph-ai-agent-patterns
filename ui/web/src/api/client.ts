import type { HitlResumeRequest, PatternInfo, RunResponse } from "../types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function fetchPatterns(): Promise<PatternInfo[]> {
  return request<PatternInfo[]>("/api/patterns");
}

export function fetchPattern(patternId: string): Promise<PatternInfo> {
  return request<PatternInfo>(`/api/patterns/${patternId}`);
}

export function runPattern(
  patternId: string,
  inputs: Record<string, unknown>,
): Promise<RunResponse> {
  return request<RunResponse>(`/api/patterns/${patternId}/run`, {
    method: "POST",
    body: JSON.stringify({ inputs }),
  });
}

export function getHitlState(threadId: string): Promise<RunResponse> {
  return request<RunResponse>(`/api/patterns/p04/state/${threadId}`);
}

export function resumeHitl(payload: HitlResumeRequest): Promise<RunResponse> {
  return request<RunResponse>("/api/patterns/p04/resume", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
