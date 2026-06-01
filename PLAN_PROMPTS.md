# Plan-mode prompts — Cohort

Paste these into Claude Code's plan mode. Run them in order; each assumes the previous
step's output exists. Read `CLAUDE.md` first — it has the data model, architecture, and
non-negotiables these prompts rely on.

---

## Prompt 1 — Synthetic cohort generation

> Read CLAUDE.md. I want to generate the synthetic cohort as a one-time script that writes
> `cohort.json`, then commit the JSON so the app never regenerates at runtime.
>
> Plan a Python script that uses the Anthropic SDK to generate ~40 synthetic patient
> journeys across these conditions: Long COVID, POTS, MCAS, SIBO/IBS, Hashimoto's,
> fibromyalgia. Requirements:
> - Conform exactly to the Journey / Event / Intervention data model in CLAUDE.md.
> - Realistic but clearly fake; every record tagged `synthetic: true`.
> - Vary timeline length (10–30 days) and symptom severity. Colloquial symptom text like
>   the Atlas site ("brain fog · heavy", "bloated again 😩").
> - Each journey has 1–3 interventions with mixed outcomes (some fail — outcome_score 0 or
>   -1, some work — 1 or 2). Don't make everything a success.
> - Generate in small batches, validate each journey against the schema, retry on bad JSON,
>   write the combined result to cohort.json.
>
> Show me the plan and the prompt you'll send to Claude to generate each batch before writing code.

---

## Prompt 2 — FastAPI backend

> Read CLAUDE.md and assume cohort.json exists. Plan the FastAPI backend.
>
> - On startup: load cohort.json, build a symptom-only natural-language signature per
>   journey, embed all signatures, hold the matrix as a module-level numpy array. Keep the
>   embedding call behind a single swappable function.
> - `POST /match { timeline }`: embed the incoming timeline's signature, cosine-sim against
>   the matrix with numpy, return top-K (K=5) journey ids + similarity scores.
> - `POST /insight { timeline }`: reuse /match retrieval, pass the top-K journeys (with
>   interventions/outcomes) to Claude, return the strict insight JSON from CLAUDE.md.
> - Strict hypothesis-only system prompt; cite cohort counts; flag weak matches; recommend
>   a clinician; never state a diagnosis. Validate/parse Claude's JSON defensively.
> - Env vars for keys, CORS for the local React dev server, no DB, no persistence.
>
> Give me the file layout and endpoint contracts before coding.

---

## Prompt 3 — React frontend

> Read CLAUDE.md and assume the FastAPI endpoints work. Plan a React + Vite + TypeScript
> frontend with three views:
> 1. Timeline picker — 2–3 preset timelines (one-click demo) plus an optional simple editor.
> 2. Matches — the top-K journeys with similarity scores and condition labels.
> 3. Insight — render the insight JSON: summary, patterns, interventions-to-explore with
>    cohort evidence, confidence badge.
>
> Persistent banner on every view: "Synthetic data. Not medical advice. Prototype."
> Keep styling clean and minimal — this is judged on clarity, not polish. Plan component
> structure and the API client before coding.

---

## Prompt 4 — Deploy + README

> Read CLAUDE.md. Plan: (1) deploying the FastAPI backend to Railway or Render and the
> static React build to Vercel or Netlify, with the env vars each needs; (2) a README that
> explains *why* I built the cross-journey matching layer instead of a chatbot — that I read
> Atlas's thesis as the aggregation / decentralized-study insight — and lists the production
> trade-offs I deliberately skipped (pgvector for embeddings, real journey ingestion,
> clinician-facing outputs, auth). Include the synthetic-data / not-medical-advice
> disclaimer prominently.
