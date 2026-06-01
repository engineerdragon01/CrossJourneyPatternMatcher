export type EventType = "symptom" | "med" | "meal" | "wearable" | "life";

export interface Event {
  day: number;
  type: EventType;
  text: string;
  severity: number | null;
}

export interface JourneyMatch {
  journey_id: string;
  condition: string;
  score: number;
}

export interface MatchResponse {
  matches: JourneyMatch[];
}

export interface InterventionInsight {
  name: string;
  cohort_evidence: string;
  outcome_summary: string;
}

export interface InsightResponse {
  summary: string;
  patterns: string[];
  interventions_to_explore: InterventionInsight[];
  confidence: string;
  match_count: number;
}
