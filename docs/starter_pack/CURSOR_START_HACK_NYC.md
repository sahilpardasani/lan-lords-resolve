# CURSOR START — LAN LORDS / Resolve — LIVE BUILD MODE

The hackathon is live. Use Cursor for bounded implementation during the build window only.

At 18:00, stop coding and stop prompting Cursor.

## Read before edits

Read:
- `00_START_HERE_NOW.md`
- `HACK_NYC_MASTER_PLAN.md`
- `01_KICKOFF/ORGANIZER_RULES_CONFIRMED_2026-08-22.md`
- `01_KICKOFF/GITHUB_BOOTSTRAP.md`
- `07_TEAM/TEAM_SPLIT.md`
- `02_BUILD_SPECS/ARCHITECTURE.md`
- `02_BUILD_SPECS/MONGODB_P0.md`
- `03_QA/PHASE_GATES.md`
- `03_QA/P0_TEST_PLAN.md`
- `05_CASE_REFERENCE_PACKS/PRIMARY_CASE_LOCK_PAYMENT.md`

## Absolute architecture

One local Qwen endpoint.

Five logical roles:
`main, scout, investigator, planner, challenger`.

No LLM Judge.

Deterministic `contract.py` owns permission.

MongoDB is required for audit/replay but cannot decide permission.

P0 sponsor component = OpenShell.

## Branch ownership

Cursor must not let parallel agents edit outside their ownership.

### Agent / Coder 1 — `packet/runtime`
Allowed:
- runtime/model scripts
- OpenShell config
- Mongo startup/config
- evidence/model_acceptance
- evidence/openshell
- evidence/mongodb
- runtime manifests

Forbidden:
- `resolve/case.py`
- `resolve/contract.py`
- `resolve/approval.py`
- `resolve/journal.py`
- primary case facts
- UI behavior

### Agent / Coder 2 — `packet/core`
Single writer:
- `resolve/case.py`
- `resolve/contract.py`
- `resolve/approval.py`
- `resolve/journal.py`
- `tests/test_contract.py`
- `tests/test_approval.py`
- `tests/test_journal.py`
- `tests/test_objective.py`

Forbidden:
- MongoDB calls/imports in `contract.py`
- model/provider hacks
- UI

### Agent / Coder 3 — `packet/integration`
Allowed:
- `resolve/runtime.py`
- `resolve/context.py`
- `resolve/tools.py`
- `resolve/mongo_store.py`
- `simulator/`
- FastAPI
- `static/`
- `tests/test_end_to_end.py`
- demo/replay scripts

Do not rewrite primary business facts.

### Business-owned files

Treat as read-only to engineering unless Business 1 explicitly requests a change:
- `cases/primary/case.yaml`
- `cases/primary/evidence/**`
- `cases/primary/EXPECTED.md`

## Immediate parallel tasks

### Runtime
Make:
1. NVFP4 endpoint green or switch to FP8 quickly.
2. OpenShell external BLOCK / local PASS.
3. local MongoDB green.
4. runtime receipt.

### Core
Write tests first for:
- PASS/FAIL/UNKNOWN;
- four dispositions;
- eight gates;
- fingerprint stability;
- approval expiry/one-use;
- US->GLOBAL mutation invalidation;
- journal tamper detection;
- loss-leader objective cases.

Then minimum implementation.

### Integration
Start against mocks now:
- payment simulator;
- simple FastAPI;
- minimum static UI;
- role-output interface;
- MongoStore interface;
- replay endpoint/view.

Replace mocks only after interfaces are green.

## Mongo implementation constraints

`resolve/mongo_store.py` should be tiny.

Required methods:
`connect, health, ensure_indexes, insert_case_snapshot, append_journal_event, insert_candidate, insert_approval, insert_verification, list_journal, export_run`.

Do not create a generic ORM/repository layer.

Use unique indexes for:
- `event_id`
- `(run_id, sequence)`

## Primary demo state machine

```text
79% incident
-> GLOBAL 100% candidate
-> constraint FAIL
-> BLOCKED
-> targeted evidence
-> US 40% candidate
-> rehearsal PASS
-> WAITING_HUMAN
-> exact approval
-> mutate US->GLOBAL
-> approval INVALID
-> restore signed candidate
-> COMMIT
-> actual simulator read
-> VERIFIED
-> MongoDB replay
```

## Development rules

- tests before critical guards;
- no duplicate permission/state representations;
- no fake tool calls;
- no model-authored final permission;
- missing evidence cannot increase autonomy;
- no blind retry after unknown side effect;
- UI projects canonical journal;
- Mongo persists canonical records;
- cap non-progress loops;
- prefer one working role path over parallel-agent theater.

## Merge discipline

Before merge:
```bash
pytest -q
git status --short
```

Critical files have one writer.

Do not auto-resolve semantic conflicts in core or case facts.

## Gate E

As soon as one E2E run passes:
- save journal;
- export Mongo run;
- save replay;
- screen-record;
- record SHA/tag;
- create/verify Git bundle;
- copy evidence/video to WD.

Then optional work begins.

## Optional order after Gate E

1. approval mutation demo beat
2. counterfactual/calibration
3. telemetry
4. OpenClaw/NemoClaw only if low-risk
5. tiny CLI second case

## Hard clock

16:15 feature freeze.  
17:30 no product changes.  
18:00 stop coding and stop prompting Cursor.

## First Cursor action

Inspect the current repo and respond with:

```text
BRANCH:
SHA:
OWNERSHIP AREA:
CURRENT GATE:
TESTS:
BLOCKER:
FILES I WILL TOUCH NEXT:
FILES I WILL NOT TOUCH:
```

Then implement only the current owner's smallest gate-closing change.
