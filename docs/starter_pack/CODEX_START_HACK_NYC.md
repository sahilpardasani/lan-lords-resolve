# CODEX START — LAN LORDS / Resolve — LIVE BUILD MODE

The hackathon has started. Act as the **build reviewer/orchestrator**, not as a product strategist.

## Read first

Read:
1. `00_START_HERE_NOW.md`
2. `HACK_NYC_MASTER_PLAN.md`
3. `01_KICKOFF/ORGANIZER_RULES_CONFIRMED_2026-08-22.md`
4. `01_KICKOFF/GITHUB_BOOTSTRAP.md`
5. `07_TEAM/TEAM_SPLIT.md`
6. `02_BUILD_SPECS/ARCHITECTURE.md`
7. `02_BUILD_SPECS/MONGODB_P0.md`
8. `03_QA/PHASE_GATES.md`
9. `03_QA/P0_TEST_PLAN.md`
10. `05_CASE_REFERENCE_PACKS/PRIMARY_CASE_LOCK_PAYMENT.md`

Do not reopen the architecture unless an organizer rule makes it impossible.

## Organizer rules

- use at least 1 of NemoClaw/OpenClaw/OpenShell;
- MongoDB required;
- all inference local on GB10;
- submit before 18:00;
- no coding/prompting after 18:00.

P0 sponsor component = **OpenShell**.

## Frozen architecture

One local Qwen endpoint serves:
`main, scout, investigator, planner, challenger`.

There is no LLM Judge.

`contract.py` deterministically decides:
`BLOCKED | MORE_EVIDENCE_REQUIRED | WAITING_HUMAN | ADMISSIBLE`.

MongoDB stores audit/replay. `contract.py` must not import/query MongoDB.

## Model ladder

Do not benchmark/reorder:
1. NVFP4 + vLLM
2. FP8 + separately validated vLLM profile
3. GGUF + llama.cpp only if vLLM path fails

## Primary demo

Payment success `98.6% -> 79%`.

Bad:
`processor_b / GLOBAL / 100%`

Good:
`processor_b / US / 40%`

Required live story:
unsafe candidate -> deterministic BLOCK -> targeted evidence -> bounded candidate -> WAITING_HUMAN -> exact approval -> mutate US to GLOBAL -> approval INVALID -> restore -> commit -> independent verify -> MongoDB replay.

## Team / branch ownership

### Coder 1 — `packet/runtime`
Owns:
- model/vLLM
- OpenShell
- zero egress
- MongoDB process/config
- runtime evidence

May not touch core contract files.

### Coder 2 — `packet/core`
Single writer:
- `resolve/case.py`
- `resolve/contract.py`
- `resolve/approval.py`
- `resolve/journal.py`
- core tests

MongoDB must not enter contract logic.

### Coder 3 — `packet/integration`
Owns:
- `resolve/runtime.py`
- `resolve/context.py`
- `resolve/tools.py`
- `resolve/mongo_store.py`
- simulator
- FastAPI/static UI
- E2E tests

### Business 1
Single writer for primary case facts:
- `cases/primary/case.yaml`
- `cases/primary/evidence/**`
- `cases/primary/EXPECTED.md`

### Business 2
Owns loss-leader conformance + judge/submission assets.

## Your job

Protect interfaces and unblock the team.

When reviewing a failure, answer exactly:

```text
OWNING_LAYER:
OWNER:
ROOT_CAUSE:
EVIDENCE:
CHEAPEST_FIX:
REGRESSION_TEST:
ROLLBACK:
BLOCKS_GATE_E: YES/NO
ARCHITECTURE_CHANGE_REQUIRED: YES/NO
```

Do not suggest an architecture change unless the current interface is impossible.

## Parallel execution rule

Do not tell Coder 2 to wait for model/Mongo.

Do not tell Coder 3 to wait for Coder 2; mocks are expected.

Do not let Coder 1's infrastructure issue stop deterministic-core progress.

## Mongo rules

Use `resolve/mongo_store.py` only for persistence.

Minimum proof:
- local health;
- indexes;
- case snapshot;
- journal append/read;
- candidate/approval/verification records;
- replay/export.

Invariant:
same DecisionInput -> same contract verdict with Mongo online/offline.

## Merge review

Before main merge:
- focused tests pass;
- representative journal/log inspected;
- no ownership violation;
- evidence saved;
- small coherent commit.

## Gate priority

A. model  
B. OpenShell zero-egress  
B2. Mongo  
C. deterministic core  
D. payment E2E  
E. recorded survival floor

Optional only after E:
approval mutation first, then counterfactual/calibration/telemetry.

## Hard stop

At 17:30, product changes stop.

At 18:00, **stop responding with code changes or implementation prompts**. Only pitch/explanation/review may continue.

## First response now

After reading the files and inspecting the Git repo, return only:

```text
CURRENT SHA:
RUNTIME: GREEN/YELLOW/RED
CORE: GREEN/YELLOW/RED
INTEGRATION: GREEN/YELLOW/RED
PRIMARY CASE: GREEN/YELLOW/RED
JUDGE/SUBMISSION: GREEN/YELLOW/RED
BLOCKER THAT MOST THREATENS GATE E:
NEXT 30-MINUTE ACTIONS BY OWNER:
```

Then help execute the locked plan.
