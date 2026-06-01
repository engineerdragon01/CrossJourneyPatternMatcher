# CLAUDE.md — Cohort

Project context for Claude Code. Read this before planning or writing code.

## What this is

**Cohort** is a small prototype of a cross-journey pattern matcher for chronic illness.
Given one user's recent symptom timeline, it finds the most similar synthetic patient
journeys, then surfaces what those people tried and how it went ("people with similar
patterns explored X; N reported relief").

It's a demo built for an interview with Atlas (theatlasnetwork.ai), a startup building a
personal health agent that aggregates self-reported symptom data to surface cross-patient
patterns. This prototype deliberately targets their *aggregation / decentralized-study*
thesis — NOT a symptom-checker chatbot.

## Non-negotiables (read these first)

- **All data is synthetic.** No real patient data, ever. Every generated journey is tagged
  as synthetic.
- **This is hypothesis generation, NOT diagnosis or medical advice.** The product never
  tells a user what they "have." It surfaces patterns from similar journeys and always
  recommends discussing with a clinician.
- **Persistent UI disclaimer** must be visible: "Synthetic data. Not medical advice.
  Prototype."
- Scope is an afternoon build. Prefer the lean path over production infra everywhere.
  When tempted to add a database, vector store, auth, or a queue — don't. Note it as a
  "for production" comment instead.

## Architecture

```
React (Vite, TS)  ──>  FastAPI (Python)
                         ├─ POST /match    { timeline } -> top-K journey ids + scores
                         ├─ POST /insight  { timeline } -> retrieve + Claude -> insight JSON
                         └─ startup: load cohort.json, embed signatures, hold matrix in RAM
```

- **No database.** Cohort lives in `cohort.json`. Embedding matrix is a module-level numpy
  array built once at startup.
- **No vector DB.** Cosine similarity in-memory with numpy. (For production: pgvector.)
- **No auth, no persistence** of user input.

## Data model

```python
EventType = Literal["symptom", "med", "meal", "wearable", "life"]

Event:        { day: int, type: EventType, text: str, severity: int | None }  # severity 1-5 for symptoms
Intervention: { name: str, outcome: str, outcome_score: int, notes: str }     # score: -1 worse, 0 none, 1 mild, 2 strong
Journey:      { id: str, condition: str, demographics: str,
                timeline: list[Event], interventions: list[Intervention], synthetic: true }
```

Event vocabulary mirrors Atlas's site (symptom / med / meal / wearable / life). Symptom text
is colloquial ("brain fog · heavy", "bloated again 😩").

## Matching approach

1. For each journey, build a natural-language **signature** from its *symptoms only*
   (exclude interventions — match on symptom similarity, then reveal what those people tried).
2. Embed all signatures once at startup; cache as a numpy matrix.
3. At query time, embed the user's timeline signature, cosine-sim against the matrix, take top-K (K=5).
4. Pass top-K journeys (with their interventions/outcomes) to Claude to synthesize the insight.

Embedding model: voyage-3 (or OpenAI text-embedding-3-small) — keep it swappable behind one function.

## Agent / insight layer

One Claude call turns top-K matches into the insight. Output strict JSON:
`{ summary, patterns[], interventions_to_explore[{name, cohort_evidence, outcome_summary}], confidence }`.

Prompt rules: hypothesis-only framing; cite the cohort ("N of K tried Y"); flag weak matches /
small cohort; end by recommending a clinician. Never state a diagnosis.

## Tech / conventions

- Backend: Python 3.11+, FastAPI, uvicorn, numpy, anthropic SDK, an embeddings client.
  Secrets via env vars (`ANTHROPIC_API_KEY`, embedding key). Never commit keys.
- Frontend: React + Vite + TypeScript. Three views: pick/enter timeline → matched journeys
  with scores → insight card. Seed 2–3 preset timelines so the demo is one click.
- Deploy: FastAPI to Railway/Render, static React build to Vercel/Netlify.

## Definition of done

Deployed link works end-to-end from a preset timeline; insight card renders with cohort
evidence; disclaimer visible on every view; README explains *why* the matching layer (not a
chatbot) and lists the production trade-offs. Shippable beats ambitious.
