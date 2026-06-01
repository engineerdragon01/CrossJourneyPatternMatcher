import type { Event, InsightResponse, MatchResponse } from "./types";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function fetchMatches(timeline: Event[]): Promise<MatchResponse> {
  const res = await fetch(`${API_BASE}/match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ timeline }),
  });
  if (!res.ok) throw new Error(`/match failed: ${res.status}`);
  return res.json();
}

export async function fetchInsight(timeline: Event[]): Promise<InsightResponse> {
  const res = await fetch(`${API_BASE}/insight`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ timeline }),
  });
  if (!res.ok) throw new Error(`/insight failed: ${res.status}`);
  return res.json();
}
