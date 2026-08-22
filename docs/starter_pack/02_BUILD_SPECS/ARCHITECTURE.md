# Resolve — Frozen P0 Architecture Specification

## Product boundary

Resolve is a **local AI troubleshooting + permission loop**:

`CASE + LOCAL EVIDENCE -> LOCAL REASONING -> CANDIDATE -> CHALLENGE -> DETERMINISTIC CONTRACT -> HUMAN AUTHORITY IF REQUIRED -> BOUNDED LOCAL ACTION -> VERIFY -> MONGODB AUDIT/REPLAY`

## Five logical roles / one model

- `main`: orchestration and bounded loop control.
- `scout`: evidence retrieval/citation.
- `investigator`: competing hypotheses and discriminating evidence/tests.
- `planner`: bounded candidate actions.
- `challenger`: adversarial falsification.

No LLM may authorize itself.

## Deterministic permission core

Day-of core owns:
- case validation/normalization/hash;
- evidence-ID validation;
- eight-gate Resolve Contract;
- disposition calculation;
- exact candidate fingerprints;
- exact approval fingerprint/expiry/one-use;
- material-mutation invalidation;
- deterministic business math;
- bounded local action admission;
- independent verification semantics;
- journal integrity/hash logic.

`contract.py` and approval rules never depend on MongoDB.

## MongoDB — required audit substrate

MongoDB is required by the organizer.

Use:
- `resolve/journal.py` for pure journal/event integrity;
- `resolve/mongo_store.py` for persistence.

MongoDB stores:
- case snapshots;
- evidence references;
- journal events;
- candidate snapshots;
- approvals;
- verification events;
- optional runtime receipts.

Invariant:

`same DecisionInput -> same contract verdict`

even if MongoDB is offline.

MongoDB records decisions. **It does not decide them.**

See `02_BUILD_SPECS/MONGODB_P0.md`.

## Sponsor component

Organizer requires at least **1 of 3**:
- NemoClaw
- OpenClaw
- OpenShell

P0 uses **OpenShell first** because it directly proves the local/controlled-runtime thesis:

`external HTTP -> BLOCKED`
`local Qwen -> PASS`
`local Resolve tool -> PASS`

OpenClaw/NemoClaw are optional after the first working demo unless an organizer gives a stricter instruction.

## Model abstraction

All model calls go through:

`LOCAL_OPENAI_COMPATIBLE_ENDPOINT`

Frozen ladder:
1. NVFP4 + vLLM
2. FP8 + separately validated vLLM profile
3. GGUF + llama.cpp disaster backup

Product logic must not care which serving path is active.

## Shared state

Agents communicate through structured findings, not an open group chat.

Correlate:
`run_id, case_id, step_id, role, evidence_ids, candidate_id, approval_id, tool_call_id, event_seq`.

MongoDB persists the canonical records; the UI is a projection.

## One generic skill

P0 uses one generic `SKILL.md`. Domain variation belongs in `case.yaml` + evidence.

Do not build domain skill trees.

## Architecture claim

Say:

> **deterministic permission around nondeterministic cognition**

Never claim identical LLM output or a completely deterministic system.

## Minimal implementation bias

Prefer:
- Python
- Pydantic/dataclasses
- FastAPI
- local MongoDB
- static HTML/JS
- SSE only if it helps the demo
- tiny deterministic simulator

Avoid:
- Redis
- Postgres
- Celery
- Kubernetes
- vector DB unless absolutely required
- distributed orchestration
- cloud model/API calls
