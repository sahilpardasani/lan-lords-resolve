# HACKNYC TEAM SPLIT — 3 CODERS + 2 BUSINESS
## LAN LORDS / Resolve
### Execution plan for the current team

We have **5 people total**:

- **3 coders**
- **2 people focused on business case, evidence, files, judge story, and submission**

The goal is to keep all five people productive in parallel without creating merge conflicts or making the coders invent business logic.

---

# 1. TEAM ASSIGNMENTS

## CODER 1 — RUNTIME / GB10 / INFRASTRUCTURE

### Mission
> **Make the machine boring.**

Own:

```text
GB10 bring-up
Qwen3.8-27B NVFP4
Qwen3.8-27B FP8 fallback
vLLM
OpenShell
local MongoDB process
zero-egress proof
runtime manifest
model acceptance evidence
system diagnostics
```

### Success condition

```text
[ ] one local Qwen endpoint works
[ ] Gate A passes
[ ] OpenShell works
[ ] external egress is blocked
[ ] local inference still works
[ ] MongoDB is running locally
[ ] exact runtime versions are recorded
```

### Hard rule

```text
10:35
NVFP4 not green?
→ switch to FP8
```

Do not spend the morning defending the primary checkpoint.

### Do NOT touch

```text
resolve/case.py
resolve/contract.py
resolve/approval.py
business policy logic
UI behavior
```

---

# 2. CODER 2 — RESOLVE CORE / CONTRACT / APPROVAL

### Mission
> **Make permission deterministic.**

This person is the protected core owner.

### Single-writer ownership

```text
resolve/case.py
resolve/contract.py
resolve/approval.py
resolve/journal.py
```

Own:

- `DecisionInput`
- case validation
- PASS / FAIL / UNKNOWN
- disposition logic
- INTENT
- EVIDENCE
- CONSTRAINTS
- CONSEQUENCE
- REVERSIBILITY
- REHEARSAL
- AUTHORITY
- VERIFICATION
- candidate fingerprints
- approval fingerprints
- expiry
- one-time-use approval
- material mutation invalidation
- journal hash/HMAC integrity
- loss-leader conformance logic
- deterministic pytest suite

### Required behavior

```text
missing material evidence
→ MORE_EVIDENCE_REQUIRED

hard declared constraint
→ BLOCKED

material candidate mutation
→ APPROVAL INVALID

expired approval
→ INVALID

reused one-time approval
→ INVALID

journal modification
→ TAMPER DETECTED
```

### Architecture rule

```text
contract.py MUST NOT import MongoDB.
contract.py MUST NOT query MongoDB.
```

MongoDB records decisions. It does not decide them.

### Success condition

```bash
pytest -q
```

Core tests green.

---

# 3. CODER 3 — INTEGRATION / PRODUCT / DEMO

### Mission
> **Make the product work end-to-end.**

Start immediately.

Do **not** wait for Coder 1 or Coder 2 to finish.

Use mocks/stubs for unfinished interfaces.

Own:

```text
resolve/runtime.py
resolve/context.py
resolve/tools.py
resolve/mongo_store.py
FastAPI
static/index.html
payment simulator
role orchestration
rehearsal
commit
verification
replay
demo flow
end-to-end tests
```

### Important ownership rule

Coder 3 owns:

```text
resolve/mongo_store.py
```

Coder 1 only owns making MongoDB available locally.

Boundary:

```text
Coder 1:
"MongoDB is alive."

Coder 3:
"Resolve persists to it."

Coder 2:
"My contract logic does not care whether MongoDB exists."
```

### Primary demo

Payment success:

```text
98.6% → 79%
```

Tempting action:

```text
GLOBAL FAILOVER TO PROCESSOR B
```

But B is only authorized for bounded traffic.

Expected sequence:

```text
investigate
→ global candidate
→ challenge
→ BLOCKED
→ obtain missing evidence
→ bounded candidate
→ rehearsal PASS
→ WAITING_HUMAN
→ approve exact action
→ mutate US to GLOBAL
→ APPROVAL INVALID
→ restore US
→ COMMIT
→ verifier reads actual simulator state
→ VERIFIED
```

### Success condition

One complete live run from evidence to verified outcome.

---

# 4. BUSINESS PERSON 1 — PRIMARY CASE / EVIDENCE OWNER

### Mission
> **Make the primary case precise enough that engineering never has to invent facts.**

Own:

```text
cases/primary/
├── case.yaml
├── evidence/
│   ├── incident.json
│   ├── processor_health.json
│   ├── processor_b_authority.json
│   └── traffic_distribution.json
└── EXPECTED.md
```

They must answer:

```text
What happened?
What is the operator trying to achieve?
What is the tempting wrong action?
What exact fact makes it unsafe?
What evidence is initially missing?
What bounded action becomes permissible?
Who may approve it?
What counts as success?
How is success independently verified?
```

### Suggested case facts

```text
Starting payment success: 79%
Target: >95%

Bad candidate:
processor_b
region=GLOBAL
traffic_pct=100

Constraint:
processor_b permitted only for US traffic

Good candidate:
processor_b
region=US
traffic_pct=40

Human approval:
required

Verification:
read actual simulator success rate after commit
```

### Deliverables

```text
[ ] frozen case.yaml
[ ] frozen evidence files
[ ] expected candidate
[ ] expected blocked candidate
[ ] expected final candidate
[ ] expected verification outcome
```

---

# 5. BUSINESS PERSON 2 — CROSS-DOMAIN PROOF / JUDGE STORY / SUBMISSION

### Mission
> **Make the proof understandable in 30 seconds.**

Own two workstreams.

## A. Loss-leader conformance case

Produce the evidence and expected behavior for:

### OBJECTIVE-01

```text
strategic role missing
→ MORE_EVIDENCE_REQUIRED
```

### OBJECTIVE-02

```text
strategic_role = loss_leader
proposed price increase violates declared policy
→ BLOCKED: OBJECTIVE_CONFLICT
```

### OBJECTIVE-03

```text
authorized strategy changes to direct profitability
→ INTENT PASS
→ continue through remaining gates
```

No second polished UI required.

## B. Judge-facing material

Own:

```text
README demo section
5-minute pitch structure
90-second backup demo narration
business value
judge FAQ
screenshots
architecture graphic inputs
submission copy
slide content
evidence organization
```

Continuously collect actual engineering evidence from the coders.

Do not wait until 17:00.

---

# 6. HOW THE FIVE PEOPLE CONNECT

```text
                 CODER 1
          GB10 / MODEL / INFRA
                   │
                   │
                   ▼
BUSINESS 1 ───► CODER 3 ◄──── CODER 2
CASE + FILES     INTEGRATION      CORE
                   │
                   ▼
              WORKING DEMO
                   │
                   ▼
              BUSINESS 2
          STORY / DECK / SUBMIT
```

Business people feed engineering:

```text
facts
constraints
expected behavior
business meaning
```

Engineering feeds business:

```text
actual screenshots
test receipts
runtime proof
demo results
limitations
```

---

# 7. SHARED INTERFACES — FREEZE EARLY

## Candidate

```json
{
  "action_type": "payments.failover",
  "target": "processor_b",
  "parameters": {
    "region": "US",
    "traffic_pct": 40
  }
}
```

## Contract result

```json
{
  "gates": {
    "intent": "PASS",
    "evidence": "PASS",
    "constraints": "PASS",
    "consequence": "PASS",
    "reversibility": "PASS",
    "rehearsal": "PASS",
    "authority": "PASS",
    "verification": "PASS"
  },
  "disposition": "WAITING_HUMAN",
  "reason_codes": []
}
```

## Approval artifact

```json
{
  "candidate_fingerprint": "...",
  "case_fingerprint": "...",
  "approver": "...",
  "expires_at": "...",
  "nonce": "...",
  "used": false,
  "integrity": "..."
}
```

## Journal event

```json
{
  "event_id": "...",
  "case_id": "...",
  "sequence": 12,
  "timestamp": "...",
  "event_type": "CONTRACT_EVALUATED",
  "payload": {},
  "payload_hash": "...",
  "prev_hash": "...",
  "event_hash_or_mac": "..."
}
```

Freeze the journal shape before the first Mongo insert.

---

# 8. MONGODB RULE

Say this consistently:

> **MongoDB is the audit substrate, not the authority.**

Use:

```text
resolve/journal.py
```

for pure integrity logic.

Use:

```text
resolve/mongo_store.py
```

for persistence.

MongoDB may store:

```text
case snapshots
evidence references
journal events
candidate snapshots
approval artifacts
verification events
```

But:

```text
same DecisionInput
→ same contract verdict
```

even if MongoDB is offline.

---

# 9. NVIDIA P0

Use **OpenShell** first.

Required proof:

```text
external HTTP
→ BLOCKED

local Qwen
→ PASS

local Resolve tool
→ PASS
```

OpenClaw and NemoClaw are optional after the first working demo.

Do not let them delay Gate E.

---

# 10. MODEL LADDER

```text
PRIMARY
Qwen3.8-27B NVFP4 + vLLM

FALLBACK
Qwen3.8-27B FP8 + validated vLLM profile

DISASTER BACKUP
Qwen3.8 GGUF + llama.cpp
```

Mental model:

```text
NVFP4 = try first
FP8   = switch without emotion
GGUF  = independent escape hatch
```

---

# 11. BRANCH PLAN

Use three engineering branches only:

```text
packet/runtime
packet/core
packet/integration
```

Business files can land through small reviewed commits or a dedicated content folder, but should not create overlapping engineering branches.

Main branch:

```text
main
↑
small reviewed merges only
```

---

# 12. FILE OWNERSHIP

## Coder 1

May freely change:

```text
runtime manifests
OpenShell configs
Mongo startup/config
scripts/system*
scripts/model*
evidence/model_acceptance/
evidence/openshell/
evidence/mongodb/
```

## Coder 2

May freely change:

```text
resolve/case.py
resolve/contract.py
resolve/approval.py
resolve/journal.py
tests/test_contract.py
tests/test_approval.py
tests/test_journal.py
tests/test_objective.py
cases/conformance/
```

## Coder 3

May freely change:

```text
resolve/runtime.py
resolve/context.py
resolve/tools.py
resolve/mongo_store.py
static/
cases/primary/
tests/test_end_to_end.py
demo scripts
```

No dual writing on:

```text
case.py
contract.py
approval.py
```

---

# 13. CURRENT TIME PLAN

## 11:35–12:15

### Coder 1
```text
runtime + OpenShell + Mongo green
```

### Coder 2
```text
minimum deterministic contract green
```

### Coder 3
```text
payment simulator/API/UI against mocks
```

### Business 1
```text
freeze payment case.yaml + evidence
```

### Business 2
```text
freeze loss-leader fixtures + demo narrative
```

## 12:15–13:15

```text
merge technical paths
replace mocks
run first integration tests
```

## 13:15–14:00

```text
first full payment run
```

## ≤14:15

```text
record first successful demo
```

## 14:15–15:00

```text
approval mutation
tamper demonstration
replay
```

## 15:00–16:15

```text
testing
calibration
demo polish
judge proof
```

## 16:15

```text
HARD FEATURE FREEZE
```

## 17:30

```text
NO PRODUCT CHANGES
submission/export/verification only
```

## 18:00

```text
STOP CODING
STOP CURSOR/CODEX PROMPTING
```

---

# 14. GATE E — SURVIVAL FLOOR

Required before optional work:

```text
[ ] one clean live run
[ ] one clean replay
[ ] screen recording
[ ] exact Git SHA
[ ] git bundle
[ ] Mongo journal export
[ ] model/runtime manifest
[ ] zero-egress receipt
[ ] pytest receipt
[ ] doctor receipt
[ ] case.yaml copied
[ ] video copied to WD
[ ] video copied to a device we physically carry
[ ] video plays without GB10
```

---

# 15. TEAM UPDATE FORMAT

Every person reports:

```text
OWNER:
STATUS: GREEN / YELLOW / RED
LAST PASS:
CURRENT BLOCKER:
NEXT 30 MIN:
NEEDS FROM:
FILES / ARTIFACTS PRODUCED:
```

No long status meetings.

---

# 16. THE FIVE ONE-LINERS

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

---

# 17. OPERATING PRINCIPLE

```text
runtime failure
does not stop core work

database failure
does not change permission logic

model uncertainty
does not grant authority

business ambiguity
does not get silently invented by engineering

UI failure
does not invalidate backend evidence
```

The five people are not building five things.

They are building **one Resolve demo through five non-overlapping responsibilities**.
