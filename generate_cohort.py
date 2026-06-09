#!/usr/bin/env python3
"""One-shot synthetic cohort generator. Run once; commit cohort.json."""

import json
import os
import time
from collections import Counter
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# fmt: off
LONGCOVID_HINTS = (
    "PEM (post-exertional malaise) is central — overexertion triggers multi-day crashes. "
    "Symptoms: brain fog, breathlessness at rest, HR spikes on standing, taste/smell changes, "
    "unrefreshing sleep. Crash-and-rest cycles dominate the timeline."
)
POTS_HINTS = (
    "Orthostatic tachycardia — HR jumps 30+ bpm on standing. Symptoms: dizziness, pre-syncope, "
    "palpitations, fatigue, nausea. Interventions often include salt/fluid loading, compression "
    "garments, beta-blockers, avoiding prolonged standing."
)
MCAS_HINTS = (
    "Mast cell activation — unpredictable allergic-like flares. Symptoms: flushing, hives, "
    "GI cramping, throat tightness, brain fog triggered by foods or scents. Histamine-rich foods "
    "(wine, leftovers, fermented) are common triggers. Antihistamines, low-histamine diet are "
    "typical interventions."
)
SIBO_HINTS = (
    "Gut-centric: bloating (especially after meals), cramping, alternating loose stool/constipation, "
    "gas pain, nausea. Low-FODMAP diet, rifaximin, probiotics, peppermint oil are common "
    "interventions. Food diary entries appear in timeline."
)
HASHIMOTOS_HINTS = (
    "Autoimmune thyroid: fatigue cycles, cold hands/feet even indoors, hair shedding, weight gain "
    "despite restricted eating, brain fog, constipation. Lab events (TSH, free T3) appear in "
    "timeline. Levothyroxine dose adjustments are common interventions."
)
FIBRO_HINTS = (
    "Widespread musculoskeletal pain, tender points, disrupted non-restorative sleep, fatigue "
    "after light activity, weather sensitivity, cognitive fog. Interventions: duloxetine, "
    "low-dose naltrexone, gentle exercise (often worsening at first), sleep hygiene."
)
# fmt: on

BATCHES = [
    ("Long COVID", "longcovid", 7, LONGCOVID_HINTS),
    ("POTS", "pots", 7, POTS_HINTS),
    ("MCAS", "mcas", 7, MCAS_HINTS),
    ("SIBO/IBS", "sibo", 7, SIBO_HINTS),
    ("Hashimoto's", "hashimotos", 7, HASHIMOTOS_HINTS),
    ("Fibromyalgia", "fibro", 7, FIBRO_HINTS),
]

VALID_TYPES = {"symptom", "med", "meal", "wearable", "life"}
VALID_SCORES = {-1, 0, 1, 2}


def build_prompt(condition: str, slug: str, count: int, hints: str) -> str:
    return f"""You are generating SYNTHETIC, clearly fictional patient journey data for a demo app.
Return ONLY a JSON array of {count} journey objects — no markdown, no explanation.

Condition: {condition}
Condition-specific context (use this vocabulary to make symptom text realistic):
{hints}

Required JSON schema — every field is mandatory:
[
  {{
    "id": "{slug}-001",
    "condition": "{condition}",
    "demographics": "F, 34, Seattle",
    "synthetic": true,
    "timeline": [
      {{
        "day": 1,
        "type": "symptom",
        "text": "brain fog · heavy",
        "severity": 4
      }}
    ],
    "interventions": [
      {{
        "name": "low-histamine diet",
        "outcome": "reduced flares after 2 weeks",
        "outcome_score": 1,
        "notes": "hard to stick to; still getting occasional reactions"
      }}
    ]
  }}
]

Hard constraints:
- Timeline: 10–30 events, spanning 10–30 days. Vary length and span across journeys.
- Use all five event types (symptom, med, meal, wearable, life) across the batch.
- Symptom text is colloquial and human. Examples:
    "brain fog · heavy", "bloated again 😩", "crashed after morning walk",
    "PEM hitting — back to bed", "heart racing 120bpm just standing up",
    "finally a 6/10 day", "couldn't get off the couch", "GI flare, skipped dinner",
    "hives on arms · mild", "froze through three layers", "hair in the drain again"
- severity is an integer 1–5 ONLY on type=symptom; all other types MUST have severity=null.
- Interventions: 1–3 per journey. MUST include mixed outcomes across the {count} journeys —
  at least 2 interventions total must have outcome_score of -1 or 0. Do not make everything succeed.
- outcome_score values: -1 (worse), 0 (no effect), 1 (mild relief), 2 (strong relief).
- synthetic must be boolean true, NOT the string "true".
- IDs must be unique within the array. Use pattern "{slug}-001", "{slug}-002", etc.
- demographics: vary gender, age 20–65, US cities.
- Return ONLY the raw JSON array. No ```json fences. No prose before or after."""


def validate_journey(j: dict) -> None:
    """Raises ValueError if the journey violates the schema."""
    for key in ("id", "condition", "demographics", "synthetic", "timeline", "interventions"):
        if key not in j:
            raise ValueError(f"Missing key: {key}")
    if j["synthetic"] is not True:
        raise ValueError(f"synthetic must be boolean true, got {j['synthetic']!r}")
    if not isinstance(j["timeline"], list) or len(j["timeline"]) < 5:
        raise ValueError(f"timeline too short ({len(j.get('timeline', []))} events) or not a list")
    for i, e in enumerate(j["timeline"]):
        if e.get("type") not in VALID_TYPES:
            raise ValueError(f"Event {i}: invalid type {e.get('type')!r}")
        if e["type"] == "symptom" and not isinstance(e.get("severity"), int):
            raise ValueError(f"Event {i}: symptom missing integer severity")
        if e["type"] != "symptom" and e.get("severity") is not None:
            raise ValueError(f"Event {i}: non-symptom event has severity={e.get('severity')!r}")
    if not isinstance(j["interventions"], list) or len(j["interventions"]) == 0:
        raise ValueError("interventions must be a non-empty list")
    for iv in j["interventions"]:
        if iv.get("outcome_score") not in VALID_SCORES:
            raise ValueError(f"Invalid outcome_score: {iv.get('outcome_score')!r}")
        for key in ("name", "outcome", "notes"):
            if not isinstance(iv.get(key), str):
                raise ValueError(f"Intervention missing string field: {key}")


def generate_batch(
    client: anthropic.Anthropic,
    condition: str,
    slug: str,
    count: int,
    hints: str,
    max_retries: int = 3,
) -> list[dict]:
    prompt = build_prompt(condition, slug, count, hints)
    last_error = None
    for attempt in range(1, max_retries + 1):
        print(f"  Attempt {attempt}/{max_retries}...")
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8192,
            temperature=1.0,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()
        # Strip accidental ```json fences if Claude adds them despite the instruction
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        try:
            journeys = json.loads(raw)
            if not isinstance(journeys, list):
                raise ValueError("Response is not a JSON array")
            for j in journeys:
                validate_journey(j)
            return journeys
        except (json.JSONDecodeError, ValueError, KeyError) as exc:
            last_error = exc
            print(f"  Validation failed: {exc}. Retrying...")
            time.sleep(2)
    raise RuntimeError(
        f"Failed to generate valid batch for {condition} after {max_retries} attempts. "
        f"Last error: {last_error}"
    )


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ANTHROPIC_API_KEY not set")

    client = anthropic.Anthropic(api_key=api_key)
    all_journeys: list[dict] = []

    for condition, slug, count, hints in BATCHES:
        print(f"\nGenerating {count} journeys for {condition}...")
        batch = generate_batch(client, condition, slug, count, hints)
        print(f"  ✓ {len(batch)} journeys validated")
        all_journeys.extend(batch)

    out_path = os.path.join(os.path.dirname(__file__), "cohort.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_journeys, f, indent=2, ensure_ascii=False)

    print(f"\nWrote {len(all_journeys)} journeys to cohort.json")
    print("Sanity check:")
    scores = [
        iv["outcome_score"]
        for j in all_journeys
        for iv in j["interventions"]
    ]
    print(f"  outcome_score distribution: {dict(Counter(scores))}")
    print(f"  conditions: {sorted(set(j['condition'] for j in all_journeys))}")


if __name__ == "__main__":
    main()
