# TODO — Cohort

Ordered for an afternoon build. Rough budget in brackets. Ship the lean path; a deployed
narrow version beats an ambitious half-built one.

## 0. Setup [~15 min]
- [ ] Init repo; add `CLAUDE.md`, `PLAN_PROMPTS.md`, this file.
- [ ] Backend: Python venv, install `fastapi uvicorn numpy anthropic` + embeddings client.
- [ ] Frontend: scaffold Vite React + TS.
- [ ] `.env` with `ANTHROPIC_API_KEY` + embedding key; add `.env` to `.gitignore`. Never commit keys.

## 1. Synthetic cohort [~30 min]
- [ ] Write the generation script (Prompt 1).
- [ ] Generate ~40 journeys across the 6 conditions; mixed intervention outcomes.
- [ ] Validate every record against the schema; `synthetic: true` on each.
- [ ] Eyeball cohort.json for realism + variety; commit it.

## 2. Backend [~45 min]
- [ ] Startup: load cohort, build symptom-only signatures, embed, cache numpy matrix.
- [ ] Embedding call behind one swappable function.
- [ ] `POST /match` — cosine-sim top-K with scores.
- [ ] `POST /insight` — retrieve + Claude, strict insight JSON, defensive parse.
- [ ] Insight prompt: hypothesis-only, cohort counts, weak-match flag, clinician rec, no diagnosis.
- [ ] CORS for local dev; test both endpoints with a preset timeline.

## 3. Frontend [~60 min]
- [ ] API client.
- [ ] View 1: timeline picker with 2–3 presets (one-click demo).
- [ ] View 2: matched journeys + similarity scores.
- [ ] View 3: insight card (summary, patterns, interventions w/ cohort evidence, confidence).
- [ ] Persistent disclaimer banner on every view.
- [ ] Full click-through works against the live backend.

## 4. Deploy + README [~30 min]
- [ ] Backend to Railway/Render with env vars.
- [ ] Frontend to Vercel/Netlify pointed at the deployed API.
- [ ] Smoke-test the public link end-to-end from a preset.
- [ ] README: *why matching layer not chatbot*; production trade-offs skipped; disclaimer.

## 5. Pre-call polish [~15 min]
- [ ] Re-read: does a stranger get from preset → insight in one click?
- [ ] Disclaimer visible everywhere; no diagnosis language anywhere in outputs.
- [ ] Draft the one-liner for Khaylah + decide whether to send the link before or after the call.

## Guardrails — do NOT do
- [ ] No database, vector store, auth, or queue. Note as "for production" instead.
- [ ] No real patient data. No diagnosis framing. No claims of clinical validity.
