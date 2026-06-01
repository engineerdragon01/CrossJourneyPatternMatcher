"""FastAPI backend for CrossJourneyPatternMatcher.

Startup: loads cohort.json, builds symptom-only signatures, embeds them into a numpy
matrix held in RAM. No database, no persistence.
"""
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Literal, Optional, Tuple

import anthropic
import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from embeddings import embed

load_dotenv(Path(__file__).parent.parent / ".env")

# ---------------------------------------------------------------------------
# Module-level state (populated once at startup, read-only afterward)
# ---------------------------------------------------------------------------

journeys: list[dict] = []
sig_matrix: Optional[np.ndarray] = None  # shape (N, embedding_dim)

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

EventType = Literal["symptom", "med", "meal", "wearable", "life"]


class Event(BaseModel):
    day: int
    type: EventType
    text: str
    severity: Optional[int] = None


class TimelineRequest(BaseModel):
    timeline: list[Event]


class JourneyMatch(BaseModel):
    journey_id: str
    condition: str
    score: float


class MatchResponse(BaseModel):
    matches: list[JourneyMatch]


class InterventionInsight(BaseModel):
    name: str
    cohort_evidence: str
    outcome_summary: str


class InsightResponse(BaseModel):
    summary: str
    patterns: list[str]
    interventions_to_explore: list[InterventionInsight]
    confidence: str
    match_count: int


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

INSIGHT_SYSTEM_PROMPT = """You are a pattern-analysis assistant for a chronic illness research demo.
Your role is to identify patterns across similar patient journeys and surface what interventions
those patients tried and how they went.

Rules — follow these exactly:
- Frame ALL findings as hypotheses. Use "some patients reported", "a subset tried", "patterns
  suggest" — never diagnosis language or "this means you have X".
- Cite cohort counts explicitly: "N of K matched patients tried X".
- If the highest match score is below 0.75, flag this as a weak match and lower confidence.
- Never state or imply a diagnosis. Never recommend a specific treatment as definitive.
- Return ONLY valid JSON — no markdown fences, no prose before or after — matching this schema:

{
  "summary": "2–3 sentences summarizing patterns observed; end with a recommendation to discuss findings with a qualified clinician before acting on them",
  "patterns": ["pattern string", ...],
  "interventions_to_explore": [
    {
      "name": "intervention name",
      "cohort_evidence": "N of K matched patients tried this",
      "outcome_summary": "brief description of outcomes across those patients"
    }
  ],
  "confidence": "high|moderate|low — one word then a brief reason including match quality and that the cohort is synthetic"
}"""


def build_signature(journey: dict) -> str:
    symptoms = [e["text"] for e in journey["timeline"] if e["type"] == "symptom"]
    body = ", ".join(symptoms) if symptoms else "no recorded symptoms"
    return f"{journey['condition']} patient: {body}"


def cosine_top_k(query_vec: np.ndarray, k: int = 5) -> List[Tuple[int, float]]:
    q = query_vec / np.linalg.norm(query_vec)
    norms = np.linalg.norm(sig_matrix, axis=1)
    scores = (sig_matrix / norms[:, None]) @ q
    top_idx = np.argsort(scores)[::-1][:k]
    return [(int(i), float(scores[i])) for i in top_idx]


def timeline_signature(timeline: List[Event]) -> str:
    symptoms = [e.text for e in timeline if e.type == "symptom"]
    body = ", ".join(symptoms) if symptoms else "no recorded symptoms"
    return f"Patient symptoms: {body}"


def parse_insight_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```", 2)
        inner = parts[1]
        if inner.startswith("json\n"):
            inner = inner[5:]
        text = inner.rsplit("```", 1)[0].strip()
    data = json.loads(text)
    for key in ("summary", "patterns", "interventions_to_explore", "confidence"):
        if key not in data:
            raise ValueError(f"Missing key in insight response: {key}")
    return data


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    global journeys, sig_matrix
    cohort_path = Path(os.environ.get("COHORT_PATH", Path(__file__).parent.parent / "cohort.json"))
    journeys = json.loads(cohort_path.read_text(encoding="utf-8"))
    signatures = [build_signature(j) for j in journeys]
    sig_matrix = embed(signatures)
    print(f"Loaded {len(journeys)} journeys; embedding matrix shape: {sig_matrix.shape}")
    yield


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="CrossJourneyPatternMatcher", lifespan=lifespan)

_raw_origins = os.environ.get("ALLOWED_ORIGINS", "*")
_origins = [o.strip() for o in _raw_origins.split(",")] if _raw_origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok", "cohort_size": len(journeys)}


@app.post("/match", response_model=MatchResponse)
def match(req: TimelineRequest):
    if sig_matrix is None:
        raise HTTPException(status_code=503, detail="Cohort not loaded")
    query_sig = timeline_signature(req.timeline)
    query_vec = embed([query_sig])[0]
    top = cosine_top_k(query_vec, k=5)
    matches = [
        JourneyMatch(
            journey_id=journeys[idx]["id"],
            condition=journeys[idx]["condition"],
            score=round(score, 4),
        )
        for idx, score in top
    ]
    return MatchResponse(matches=matches)


@app.post("/insight", response_model=InsightResponse)
def insight(req: TimelineRequest):
    if sig_matrix is None:
        raise HTTPException(status_code=503, detail="Cohort not loaded")

    # Retrieve top-K
    query_sig = timeline_signature(req.timeline)
    query_vec = embed([query_sig])[0]
    top = cosine_top_k(query_vec, k=5)
    top_score = top[0][1] if top else 0.0
    matched = [journeys[idx] for idx, _ in top]

    # Build user message for Claude
    journeys_text = json.dumps(
        [
            {
                "id": j["id"],
                "condition": j["condition"],
                "interventions": j["interventions"],
            }
            for j in matched
        ],
        indent=2,
    )
    user_message = (
        f"The user's symptom timeline: {query_sig}\n\n"
        f"Top match score: {top_score:.2f} (threshold for high confidence: 0.75)\n"
        f"Number of matched journeys: {len(matched)}\n\n"
        f"Matched journeys (interventions only — symptoms were used only for matching):\n"
        f"{journeys_text}\n\n"
        "Synthesize the patterns and interventions into the required JSON."
    )

    # Call Claude
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=INSIGHT_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    # Parse defensively
    try:
        data = parse_insight_json(msg.content[0].text)
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail={"error": "insight generation failed", "detail": str(exc)},
        )

    return InsightResponse(
        summary=data["summary"],
        patterns=data["patterns"],
        interventions_to_explore=[
            InterventionInsight(**iv) for iv in data["interventions_to_explore"]
        ],
        confidence=data["confidence"],
        match_count=len(matched),
    )
