# LAN LORDS / Resolve — STARTER PROMPTS

> **Archive.** Duplicate of the day-of role prompts. Product documentation is [../../README.md](../../README.md). Event file map: [../HACKATHON.md](../HACKATHON.md).

Use this README after cloning the hackathon archive repository.

**Team:** 3 coders + 2 business  
**Product:** Resolve  
**Primary demo:** Payment authorization outage  
**P0 sponsor component:** OpenShell  
**Required database:** MongoDB  
**Inference:** local on Dell GB10  
**Hard stop:** 18:00 local — no more coding or Cursor/Codex prompting

> **The AI recommends. Resolve decides whether that exact recommendation has earned permission.**

---

# 1. BEFORE ANYONE STARTS

After cloning:

```bash
git status
git remote -v
git branch -a
```

Read:

```text
START_HERE.md
HACK_NYC_MASTER_PLAN.md
TEAM_SPLIT.md
ARCHITECTURE.md
MONGODB_P0.md
P0_TEST_PLAN.md
PHASE_GATES.md
RUBRIC_MAP.md
```

Do not redesign the architecture.

Do not:
- use remote LLM inference in the Resolve runtime;
- add an LLM Judge;
- let MongoDB decide permission;
- change another person's owned files;
- commit model weights, secrets, HF caches or recordings;
- silently change business facts to make a test pass.

The build priority is:

```text
A   local model
B   OpenShell proof
B2  MongoDB
C   deterministic core
D   payment E2E
E   survival floor
```

Work in parallel. Do not wait unnecessarily for another owner.

---

# 2. FROZEN ARCHITECTURE IN 30 SECONDS

One local Qwen endpoint serves five logical roles:

```text
main
scout
investigator
planner
challenger
```

The LLM may:
- retrieve evidence;
- generate hypotheses;
- propose actions;
- challenge actions;
- request missing evidence.

The LLM may NOT authorize itself.

Final permission comes from deterministic Python:

```text
INTENT
EVIDENCE
CONSTRAINTS
CONSEQUENCE
REVERSIBILITY
REHEARSAL
AUTHORITY
VERIFICATION
```

Gate values:

```text
PASS
FAIL
UNKNOWN
```

Final dispositions:

```text
BLOCKED
MORE_EVIDENCE_REQUIRED
WAITING_HUMAN
ADMISSIBLE
```

MongoDB is:

> **the audit substrate, not the authority.**

It records:
- case snapshots;
- evidence references;
- journal events;
- candidate snapshots;
- approvals;
- verification;
- replay.

`contract.py` must not depend on MongoDB.

---

# 3. PRIMARY DEMO LOCK

Starting state:

```text
normal payment success: 98.6%
incident payment success: 79%
```

Tempting candidate:

```text
Processor B
region = GLOBAL
traffic_pct = 100
```

Problem:

```text
Processor B is not authorized for unrestricted global traffic.
```

Expected first result:

```text
BLOCKED
```

After targeted evidence:

```text
Processor B
country = US
networks = visa, mastercard
maximum_transaction_value_usd = 5000
traffic_share = 0.174 of total traffic
```

Expected flow:

```text
rehearsal PASS
→ WAITING_HUMAN
→ approve exact action
→ mutate US to GLOBAL
→ old approval INVALID
→ restore signed action
→ COMMIT
→ verifier reads actual simulator state
→ VERIFIED
→ MongoDB replay
```

---

# 4. CODER 1 — RUNTIME / GB10 / INFRA

## Branch

```bash
git switch packet/runtime
git pull --ff-only
```

## Mission

> **Make the machine boring.**

## Own

```text
GB10 bring-up
Qwen3.8 NVFP4
Qwen3.8 FP8 fallback
vLLM
OpenShell
local MongoDB process/config
zero-egress proof
runtime manifests
model acceptance evidence
system diagnostics
```

Do NOT edit:

```text
resolve/case.py
resolve/contract.py
resolve/approval.py
resolve/journal.py
cases/primary/**
static/**
```

## First Cursor prompt

Copy/paste:

```text
You are CODER 1 for LAN LORDS / Resolve.

Mission: MAKE THE MACHINE BORING.

Work only on branch packet/runtime and only in your owned runtime/infra files.

Read first:
START_HERE.md
HACK_NYC_MASTER_PLAN.md
TEAM_SPLIT.md
ARCHITECTURE.md
MONGODB_P0.md
PHASE_GATES.md
P0_TEST_PLAN.md
docs/starter_pack/03_QA/MODEL_ACCEPTANCE_SUITE.md

Do not redesign the architecture.

Frozen model ladder:
1. PRIMARY: Qwen3.8-27B NVFP4 + vLLM
2. FALLBACK 1: Qwen3.8-27B FP8 + separately validated vLLM profile
3. DISASTER BACKUP: verified Qwen3.8 GGUF + llama.cpp only if vLLM itself fails

P0 sponsor component is OpenShell.

Your immediate goals:

1. Inspect the actual GB10 environment and record exact versions.
2. Make the PRIMARY local Qwen endpoint work on the GB10.
3. If NVFP4 cannot become credible within the remaining short model-debug timebox, switch to FP8 without reopening model selection.
4. Make OpenShell prove:
   external/public HTTP -> BLOCKED
   local Qwen -> PASS
   local harmless Resolve tool -> PASS
5. Start MongoDB locally and record exact version/config.
6. Save receipts under:
   evidence/model_acceptance/
   evidence/openshell/
   evidence/mongodb/
   evidence/runtime/

Do not upgrade a working stack.
Do not guess package/container versions.
Do not touch deterministic core files, primary case facts or UI.

Before changing anything, respond only:

BRANCH:
SHA:
GB10/GPU:
NVFP4 STATUS:
FP8 STATUS:
VLLM STATUS:
OPENSHELL STATUS:
MONGODB STATUS:
BIGGEST RUNTIME BLOCKER:
FILES I WILL TOUCH:
FIRST 30-MINUTE PLAN:

Then execute the smallest work that closes Gates A, B and B2.
```

## Success

```text
[ ] local Qwen endpoint works
[ ] GPU path verified
[ ] OpenShell public egress blocked
[ ] local model still works
[ ] local tool still works
[ ] MongoDB running locally
[ ] exact versions recorded
[ ] receipts saved
```

---

# 5. CODER 2 — RESOLVE CORE / CONTRACT / APPROVAL

## Branch

```bash
git switch packet/core
git pull --ff-only
```

## Mission

> **Make permission deterministic.**

## Single-writer files

```text
resolve/case.py
resolve/contract.py
resolve/approval.py
resolve/journal.py
```

Tests:

```text
tests/test_contract.py
tests/test_approval.py
tests/test_journal.py
tests/test_objective.py
cases/conformance/
```

## First Cursor prompt

```text
You are CODER 2 for LAN LORDS / Resolve.

Mission: MAKE PERMISSION DETERMINISTIC.

Work only on branch packet/core.

You are the SINGLE WRITER for:
resolve/case.py
resolve/contract.py
resolve/approval.py
resolve/journal.py

Read first:
START_HERE.md
HACK_NYC_MASTER_PLAN.md
TEAM_SPLIT.md
ARCHITECTURE.md
P0_TEST_PLAN.md
PHASE_GATES.md
docs/starter_pack/02_BUILD_SPECS/RESOLVE_CONTRACT.md
docs/starter_pack/02_BUILD_SPECS/STATE_MACHINE.md
docs/starter_pack/03_QA/BEHAVIOR_CALIBRATION.md

Do not wait for the model, MongoDB, OpenShell or UI.

Hard architecture rules:

- contract.py MUST NOT import/query MongoDB.
- No LLM Judge.
- No model output can directly grant permission.
- Missing material evidence cannot increase autonomy.

Implement tests first for:

1. PASS / FAIL / UNKNOWN.
2. INTENT.
3. EVIDENCE.
4. CONSTRAINTS.
5. CONSEQUENCE.
6. REVERSIBILITY.
7. REHEARSAL.
8. AUTHORITY.
9. VERIFICATION.

Disposition rules:

hard FAIL -> BLOCKED
material UNKNOWN -> MORE_EVIDENCE_REQUIRED
required PASS + human required -> WAITING_HUMAN
required PASS + no human required -> ADMISSIBLE

Also implement/test:

- deterministic normalized case fingerprint;
- deterministic candidate fingerprint;
- approval bound to exact candidate + case + authority;
- expiry;
- one-time use;
- mutation invalidation;
- US -> GLOBAL mutation invalidates old approval;
- expired approval invalid;
- reused approval invalid;
- journal hash/HMAC tamper detection;
- loss-leader INTENT conformance cases.

Keep functions small and deterministic.

Before edits, respond only:

BRANCH:
SHA:
OWNED FILES:
TEST FILES I WILL CREATE:
INTERFACES I NEED FROM INTEGRATION:
BIGGEST CORE RISK:
FIRST 30-MINUTE PLAN:

Then build the minimum tests and implementation needed to close Gate C.
```

## Success

```bash
pytest -q
```

with core tests green.

---

# 6. CODER 3 — INTEGRATION / PRODUCT / DEMO

## Branch

```bash
git switch packet/integration
git pull --ff-only
```

## Mission

> **Make the product work end-to-end.**

## Own

```text
resolve/runtime.py
resolve/context.py
resolve/tools.py
resolve/mongo_store.py
simulator/**
FastAPI
static/**
tests/test_end_to_end.py
demo/replay scripts
```

Do NOT edit:

```text
resolve/case.py
resolve/contract.py
resolve/approval.py
resolve/journal.py
```

Treat Business 1's `cases/primary/**` facts as read-only unless they explicitly change them.

## First Cursor prompt

```text
You are CODER 3 for LAN LORDS / Resolve.

Mission: MAKE THE PRODUCT WORK END-TO-END.

Work only on branch packet/integration and your owned integration/product files.

Read first:
START_HERE.md
HACK_NYC_MASTER_PLAN.md
TEAM_SPLIT.md
ARCHITECTURE.md
MONGODB_P0.md
P0_TEST_PLAN.md
PHASE_GATES.md
docs/starter_pack/05_CASE_REFERENCE_PACKS/PRIMARY_CASE_LOCK_PAYMENT.md

Start immediately using mocks/stubs.
Do NOT wait for Coder 1 or Coder 2.

You own:
resolve/runtime.py
resolve/context.py
resolve/tools.py
resolve/mongo_store.py
simulator/**
FastAPI
static/**
tests/test_end_to_end.py
demo/replay scripts

You do NOT own:
resolve/case.py
resolve/contract.py
resolve/approval.py
resolve/journal.py

Do not silently rewrite cases/primary/**.

Build the minimum product path:

incident success = 79%
-> local role outputs
-> GLOBAL 100% candidate
-> core interface returns BLOCKED
-> targeted evidence added
-> bounded US Visa/Mastercard <= $5,000 / 17.4% total candidate
-> rehearsal PASS
-> WAITING_HUMAN
-> exact approval
-> mutate US to GLOBAL
-> old approval INVALID
-> restore signed candidate
-> COMMIT simulator
-> verifier reads ACTUAL simulator state
-> VERIFIED
-> MongoDB journal/replay

MongoDB rule:
MongoDB is the audit substrate, not the authority.

Keep resolve/mongo_store.py deliberately small.

Required methods:
connect()
health()
ensure_indexes()
insert_case_snapshot(...)
append_journal_event(...)
insert_candidate(...)
insert_approval(...)
insert_verification(...)
list_journal(run_id)
export_run(run_id)

Use mocks for unfinished model/core interfaces until the real owners merge them.

The UI should be simple and demo-first:
- incident
- evidence
- candidate
- gate result
- approval
- commit
- verify
- audit/replay

Do not build a generic dashboard.

Before edits, respond only:

BRANCH:
SHA:
MOCKED INTERFACES:
REAL INTERFACES AVAILABLE:
MONGO STATUS:
SIMULATOR STATUS:
API STATUS:
UI STATUS:
BIGGEST E2E BLOCKER:
FILES I WILL TOUCH:
FIRST 30-MINUTE PLAN:

Then build the smallest E2E slice that can later swap the mocks for the real runtime/core.
```

## Success

One complete run from evidence to independently verified outcome.

---

# 7. BUSINESS 1 — PRIMARY CASE / EVIDENCE

## Mission

> **Make the primary case precise enough that nobody invents facts.**

## Own

```text
cases/primary/case.yaml
cases/primary/evidence/**
cases/primary/EXPECTED.md
```

Do not edit engineering code.

If using Git, work only in these content files and submit a small reviewed commit/PR.

## First prompt

```text
You are BUSINESS 1 for LAN LORDS / Resolve.

Mission: MAKE THE PRIMARY CASE PRECISE ENOUGH THAT NOBODY INVENTS FACTS.

Read:
START_HERE.md
HACK_NYC_MASTER_PLAN.md
TEAM_SPLIT.md
docs/starter_pack/05_CASE_REFERENCE_PACKS/PRIMARY_CASE_LOCK_PAYMENT.md

You own only:
cases/primary/case.yaml
cases/primary/evidence/**
cases/primary/EXPECTED.md

Do NOT edit engineering source.

Freeze these facts:

normal payment success = 98.6%
incident payment success = 79%

bad candidate:
Processor B
region = GLOBAL
traffic_pct = 100

hard rule:
Processor B is not authorized for unrestricted global traffic.

bounded candidate:
Processor B
country = US
networks = visa, mastercard
maximum_transaction_value_usd = 5000
traffic_share = 0.174 of total traffic

human approval = required

verification:
read the actual simulator state after commit.

Stage the evidence deliberately.

STAGE 1:
Enough to prove the global action is unsafe.
Capacity evidence is stale, so the bounded candidate must first return MORE_EVIDENCE_REQUIRED.

STAGE 2:
Only the current capacity, affected-cohort, traffic-distribution and rehearsal evidence needed to justify the bounded candidate.

Your files must make these questions unambiguous:

What happened?
What is the objective?
What must be protected?
What is the tempting wrong action?
What exact fact blocks it?
What material information is initially missing?
What later evidence resolves that uncertainty?
What action becomes permissible?
Who may approve it?
What counts as success?
How is success independently verified?

Before writing, respond only:

CASE STATUS:
FACTS FROZEN:
MISSING FACTS:
STAGE-1 FILES:
STAGE-2 FILES:
EXPECTED BLOCKED CANDIDATE:
EXPECTED FINAL CANDIDATE:
VERIFICATION RULE:
FILES I WILL TOUCH:

Then create only the case, evidence and EXPECTED files.
```

---

# 8. BUSINESS 2 — JUDGE STORY / CROSS-DOMAIN / SUBMISSION

## Mission

> **Make the proof legible enough that a judge understands it in 30 seconds.**

## Own

```text
loss-leader fixture content
README demo wording
5-minute pitch
90-second backup narration
judge FAQ
rubric map
screenshots
evidence index
submission copy
slide content
business value
```

Do not invent engineering results.

Use only actual screenshots/receipts/tests from the coders.

## First prompt

```text
You are BUSINESS 2 for LAN LORDS / Resolve.

Mission: MAKE THE PROOF LEGIBLE ENOUGH THAT A JUDGE UNDERSTANDS IT IN 30 SECONDS.

Read:
START_HERE.md
HACK_NYC_MASTER_PLAN.md
TEAM_SPLIT.md
RUBRIC_MAP.md
docs/starter_pack/04_PITCH/FIVE_MINUTE_RUN.md
docs/starter_pack/04_PITCH/JUDGE_QA.md
docs/starter_pack/05_CASE_REFERENCE_PACKS/06_objective_loss_leader/
docs/starter_pack/03_QA/BEHAVIOR_CALIBRATION.md

Do not modify deterministic core behavior.
Do not invent proof that engineering has not produced.

Own two tracks.

TRACK A — CROSS-DOMAIN INTENT PROOF

Prepare/validate:

OBJECTIVE-01
strategic role missing
-> MORE_EVIDENCE_REQUIRED

OBJECTIVE-02
strategic_role = loss_leader
candidate attempts margin-maximizing price increase
-> BLOCKED: OBJECTIVE_CONFLICT

OBJECTIVE-03
authorized strategy changed to direct profitability
-> INTENT PASS
-> continue through remaining gates

No second polished UI.

TRACK B — JUDGE / SUBMISSION

Continuously maintain:
- 5-minute pitch;
- 90-second backup narration;
- README demo section;
- rubric map;
- business value;
- judge FAQ;
- screenshots;
- runtime/test receipts;
- architecture graphic inputs;
- evidence index;
- submission copy;
- slide content.

Core story:

A recommendation is not permission.

The local model finds a plausible global failover.
Resolve blocks it deterministically.
It obtains the missing evidence.
It proposes a bounded action.
A human approves that exact action.
Changing one material parameter invalidates the approval.
Only the signed action commits.
The result is independently verified.
MongoDB reconstructs the audit trail.
Everything runs locally.

Before writing, respond only:

RUBRIC GAPS:
ENGINEERING PROOF AVAILABLE:
ENGINEERING PROOF STILL NEEDED:
LOSS-LEADER STATUS:
PITCH STATUS:
SUBMISSION STATUS:
NEXT 30-MINUTE DELIVERABLES:
FILES I WILL TOUCH:

Then proceed only with content/judge/submission work.
```

---

# 9. TEAM LEAD / CODEX PROMPT

Use Codex as reviewer/orchestrator, not as a fourth coder.

```text
You are the build reviewer/orchestrator for LAN LORDS / Resolve.

Read:
START_HERE.md
HACK_NYC_MASTER_PLAN.md
TEAM_SPLIT.md
ARCHITECTURE.md
MONGODB_P0.md
P0_TEST_PLAN.md
PHASE_GATES.md
RUBRIC_MAP.md
docs/starter_pack/CODEX_START_HACK_NYC.md

Do not reopen the architecture unless an organizer rule makes it impossible.

Protect:
- single-writer boundaries;
- deterministic permission;
- MongoDB separation;
- local-only inference;
- OpenShell P0;
- primary payment case facts;
- Gate E before optional features.

When diagnosing a problem answer:

OWNING_LAYER:
OWNER:
ROOT_CAUSE:
EVIDENCE:
CHEAPEST_FIX:
REGRESSION_TEST:
ROLLBACK:
BLOCKS_GATE_E: YES/NO
ARCHITECTURE_CHANGE_REQUIRED: YES/NO

Then print:

CURRENT SHA:
RUNTIME: GREEN/YELLOW/RED
CORE: GREEN/YELLOW/RED
INTEGRATION: GREEN/YELLOW/RED
PRIMARY CASE: GREEN/YELLOW/RED
JUDGE/SUBMISSION: GREEN/YELLOW/RED
BLOCKER THAT MOST THREATENS GATE E:
NEXT 30-MINUTE ACTIONS BY OWNER:

Do not implement across another owner's files merely because they are blocked.
```

---

# 10. 30-MINUTE TEAM UPDATE

Every person posts:

```text
OWNER:
STATUS: GREEN / YELLOW / RED
LAST PASS:
CURRENT BLOCKER:
NEXT 30 MIN:
NEEDS FROM:
FILES / ARTIFACTS PRODUCED:
```

No long status meeting.

---

# 11. GATE E — STOP AND SAVE

As soon as the first end-to-end run works:

```text
[ ] one clean live run
[ ] one clean replay
[ ] screen recording
[ ] exact Git SHA/tag
[ ] verified Git bundle
[ ] MongoDB journal/export
[ ] model/runtime manifest
[ ] zero-egress receipt
[ ] pytest receipt
[ ] doctor receipt
[ ] successful case.yaml
[ ] video copied to WD
[ ] video copied to another physically carried device
[ ] video plays without GB10
```

Then optional work may begin.

Optional order:

```text
1. approval mutation
2. counterfactual / calibration
3. telemetry
4. OpenClaw/NemoClaw only if low risk
5. tiny second CLI case
```

---

# 12. HARD CLOCK

```text
16:15
HARD FEATURE FREEZE

17:30
NO PRODUCT CHANGES
submission/export/verification only

18:00
STOP CODING
STOP CURSOR PROMPTING
STOP CODEX IMPLEMENTATION PROMPTING
```

After 18:00, pitch preparation only.

---

# 13. ONE-LINERS

```text
CODER 1
Make the machine boring.

CODER 2
Make permission deterministic.

CODER 3
Make the product work end-to-end.

BUSINESS 1
Make the primary case precise enough that nobody invents facts.

BUSINESS 2
Make the proof legible enough that a judge understands it in 30 seconds.
```

One product. Five non-overlapping responsibilities.
