# HACKNYC TEAM SPLIT — 3 CODERS + 2 BUSINESS

**Team:** LAN LORDS  
**Product:** Resolve

Five people are building one demo through five non-overlapping responsibilities.

## Coder 1 — Runtime / GB10 / Infrastructure

**Mission:** Make the machine boring.

Own:
- GB10 bring-up
- Qwen3.8 NVFP4 primary
- Qwen3.8 FP8 fallback
- vLLM
- OpenShell P0
- local MongoDB availability/config
- zero-egress proof
- runtime manifest
- model acceptance evidence
- system diagnostics

Success:
- local Qwen endpoint works
- chosen Gate-A model tests pass
- OpenShell works
- public egress blocked
- local inference/tool still works
- MongoDB is alive locally
- versions recorded

If NVFP4 is still not credible within a short remaining model-debug timebox, switch to FP8. Do not defend the checkpoint emotionally.

Do not touch:
- `resolve/case.py`
- `resolve/contract.py`
- `resolve/approval.py`
- `resolve/journal.py`
- primary business facts
- UI behavior

## Coder 2 — Resolve Core / Contract / Approval

**Mission:** Make permission deterministic.

Single writer:
- `resolve/case.py`
- `resolve/contract.py`
- `resolve/approval.py`
- `resolve/journal.py`

Own:
- DecisionInput
- case validate/normalize/hash
- PASS / FAIL / UNKNOWN
- final dispositions
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
- one-time use
- material mutation invalidation
- journal hash/HMAC integrity
- loss-leader conformance tests

Hard rule:
- `contract.py` must not import/query MongoDB.
- MongoDB records verdicts; it never creates them.

Required behaviors:
- missing material evidence -> `MORE_EVIDENCE_REQUIRED`
- hard constraint -> `BLOCKED`
- material candidate mutation -> approval invalid
- expired approval -> invalid
- reused one-time approval -> invalid
- journal modification -> tamper detected

## Coder 3 — Integration / Product / Demo

**Mission:** Make the product work end-to-end.

Start immediately against mocks; do not wait for Coder 1/2.

Own:
- `resolve/runtime.py`
- `resolve/context.py`
- `resolve/tools.py`
- `resolve/mongo_store.py`
- FastAPI
- `static/`
- `simulator/`
- role orchestration
- rehearsal
- commit
- independent verification
- replay
- demo flow
- E2E tests

Mongo boundary:
- Coder 1: **MongoDB is alive**
- Coder 3: **Resolve persists to it**
- Coder 2: **permission logic does not care whether MongoDB exists**

**Important conflict fix:** Coder 3 does **not** rewrite Business 1's facts/evidence/case.yaml just to make integration pass.

## Business 1 — Primary Payment Case / Evidence

**Mission:** Make the case precise enough that engineering never invents facts.

Single writer for:
- `cases/primary/case.yaml`
- `cases/primary/evidence/**`
- `cases/primary/EXPECTED.md`

Freeze:
- what happened
- objective
- protected outcomes
- tempting wrong action
- exact hard constraint
- what evidence is available initially
- what evidence is revealed later
- bounded permissible candidate
- approver authority
- success condition
- independent verification rule

Primary facts:
- baseline payment success: 98.6%
- current success: 79%
- bad candidate: Processor B, GLOBAL, 100%
- hard rule: Processor B is authorized only for eligible bounded traffic
- good candidate: Processor B, US, 40%
- human approval required
- verification reads actual simulator state

Evidence staging:
1. initial evidence is enough to show global failover violates a hard rule;
2. later evidence supplies traffic/replay facts needed to choose the bounded 40% candidate;
3. do not reveal every answer on the first pass.

## Business 2 — Cross-Domain Proof / Judge Story / Submission

**Mission:** Make the proof understandable in 30 seconds.

Own:

### Loss-leader INTENT conformance
- strategy absent -> `MORE_EVIDENCE_REQUIRED`
- loss-leader strategy + margin-max candidate -> `BLOCKED: OBJECTIVE_CONFLICT`
- authorized strategy changed -> `INTENT PASS`, continue remaining gates

### Judge-facing assets
- README demo section
- five-minute pitch
- 90-second backup narration
- business value
- judge FAQ
- screenshots
- slide content
- submission copy
- evidence organization

Collect actual engineering receipts continuously.

## Shared interfaces — freeze early

### Candidate
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

### Contract result
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

### Approval
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

### Journal event
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

Freeze journal shape before first Mongo insert.

## Branches

- Coder 1 -> `packet/runtime`
- Coder 2 -> `packet/core`
- Coder 3 -> `packet/integration`
- main -> reviewed merges only

## Current execution window

### NOW -> first checkpoint
- Coder 1: runtime + OpenShell + MongoDB green
- Coder 2: minimum deterministic contract green
- Coder 3: payment simulator/API/UI against mocks
- Business 1: freeze staged payment case/evidence
- Business 2: freeze loss-leader fixtures + demo narrative

### Next ~60 min
Merge interfaces, replace mocks, run integration.

### First full run
Get one complete payment run as soon as interfaces connect.

### Gate E
Record the first successful run immediately.

### Hard clocks
- 16:15 hard feature freeze
- 17:30 no product changes
- 18:00 stop coding and prompting

## Status update format

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

## Five one-liners

- Coder 1: **Make the machine boring.**
- Coder 2: **Make permission deterministic.**
- Coder 3: **Make the product work end-to-end.**
- Business 1: **Make the primary case precise enough that nobody invents facts.**
- Business 2: **Make the proof legible enough that a judge understands it in 30 seconds.**
