# Hack NYC — Live Master Plan

**Team:** LAN LORDS  
**Product:** Resolve  
**Build status:** hackathon is live  
**Primary demo:** payment authorization outage  
**Architecture:** one local Qwen model + five reasoning roles + deterministic permission kernel + local MongoDB audit/replay  
**P0 sponsor component:** OpenShell

---

## 1. Organizer-confirmed constraints

Treat `01_KICKOFF/ORGANIZER_RULES_CONFIRMED_2026-08-22.md` as authoritative.

- no pre-built functioning agents;
- plans/scaffolds/libraries allowed;
- at least 1 of NemoClaw/OpenClaw/OpenShell;
- MongoDB required;
- inference local on GB10;
- submit before 18:00;
- no coding/prompting after 18:00;
- slides due 19:00;
- pitches 19:30.

---

## 2. What judges should remember

> **A recommendation is not permission.**

Demo behavior:

`messy incident -> plausible unsafe fix -> deterministic BLOCK -> targeted evidence -> bounded fix -> exact human approval -> material mutation invalidates approval -> signed local action -> independent verification -> MongoDB replay`

Do not pitch “five agents.”

---

## 3. Architecture lock

### Local cognition
One local Qwen endpoint serves five logical roles:
`main, scout, investigator, planner, challenger`.

### Permission
`contract.py` is deterministic Python.

Eight gates:
1. INTENT
2. EVIDENCE
3. CONSTRAINTS
4. CONSEQUENCE
5. REVERSIBILITY
6. REHEARSAL
7. AUTHORITY
8. VERIFICATION

Gate values:
`PASS | FAIL | UNKNOWN`

Disposition:
- hard FAIL -> `BLOCKED`
- material UNKNOWN -> `MORE_EVIDENCE_REQUIRED`
- all required PASS + human -> `WAITING_HUMAN`
- all required PASS + no human -> `ADMISSIBLE`

### Persistence
MongoDB is required and used for durable audit/replay.

**MongoDB is the audit substrate, not the authority.**

`contract.py` never queries MongoDB.

### Sponsor component
P0: OpenShell.

Proof:
- public HTTP -> BLOCKED
- local Qwen -> PASS
- local Resolve tool -> PASS

OpenClaw/NemoClaw are optional after Gate E.

---

## 4. Model ladder

Do not reopen model strategy.

1. **PRIMARY:** Qwen3.8-27B NVFP4 + vLLM
2. **FALLBACK:** Qwen3.8-27B FP8 + separately validated vLLM profile
3. **DISASTER BACKUP:** verified Qwen3.8 GGUF + llama.cpp if vLLM path fails

All product calls use `LOCAL_OPENAI_COMPATIBLE_ENDPOINT`.

---

## 5. Primary payment case

Starting state:
- baseline success 98.6%
- current success 79%

Tempting candidate:
`processor_b / GLOBAL / 100%`

Hard problem:
Processor B is not authorized for unrestricted global traffic.

Expected flow:
1. investigate;
2. propose global candidate;
3. challenge;
4. deterministic `BLOCKED`;
5. obtain targeted traffic/replay evidence;
6. propose bounded `US / 40%`;
7. rehearsal PASS;
8. `WAITING_HUMAN`;
9. approve exact action;
10. mutate `US -> GLOBAL`;
11. approval INVALID;
12. restore exact signed candidate;
13. COMMIT;
14. verifier reads actual simulator state;
15. VERIFIED;
16. MongoDB reconstructs the entire trace.

See `05_CASE_REFERENCE_PACKS/PRIMARY_CASE_LOCK_PAYMENT.md`.

---

## 6. Team split

See `07_TEAM/TEAM_SPLIT.md`.

### Coder 1
Runtime / model / OpenShell / Mongo availability.

### Coder 2
Pure deterministic core / approval / journal integrity.

### Coder 3
Runtime integration / Mongo store / simulator / API / UI / replay.

### Business 1
Primary case facts/evidence/staging.

### Business 2
Cross-domain objective proof / judge story / deck / submission.

Critical single-writer boundary:
- Coder 2 owns `case.py`, `contract.py`, `approval.py`, `journal.py`.
- Coder 3 owns `mongo_store.py` and product integration.
- Business 1 owns primary case facts; engineering consumes them.

---

## 7. Git workflow

Use `01_KICKOFF/GITHUB_BOOTSTRAP.md`.

Branches:
- `packet/runtime`
- `packet/core`
- `packet/integration`

Main gets reviewed merges only.

GitHub is useful collaboration. It is **not** the only recovery mechanism.

After first success create and verify a Git bundle and copy it to the WD.

---

## 8. Build order from now

Parallel work starts immediately.

### Track A — Coder 1
1. GB10/model endpoint.
2. OpenShell.
3. zero-egress receipt.
4. local MongoDB.
5. runtime/version manifest.

### Track B — Coder 2
No model or Mongo dependency:
1. case validation/hash;
2. contract gates/disposition;
3. approval fingerprint/expiry/one-use;
4. mutation invalidation;
5. journal integrity;
6. objective tests.

### Track C — Coder 3
Start against mocks:
1. simulator;
2. FastAPI;
3. basic UI;
4. role orchestration interface;
5. `mongo_store.py`;
6. E2E skeleton.

### Business 1
Freeze primary facts and staged evidence.

### Business 2
Freeze loss-leader tests and judge/submission story.

The deterministic core and product mock path **must not wait for runtime setup**.

---

## 9. Gate sequence

### Gate A — model
One local endpoint credible.

### Gate B — OpenShell / zero egress
Public blocked; local model/tool pass.

### Gate B2 — MongoDB
Mongo health + insert/read + indexes.

### Gate C — deterministic core
Core pytest green.

### Gate D — full payment E2E
All layers connected.

### Gate E — survival floor
Immediately capture:
- live run
- replay
- recording
- SHA/tag
- Git bundle
- Mongo export
- model/runtime receipt
- zero-egress receipt
- pytest/doctor
- case.yaml
- video on WD and another physical device

Nothing optional before Gate E.

---

## 10. Optional work after Gate E

Order:
1. approval mutation beat;
2. counterfactual/evidence sensitivity;
3. calibration receipt;
4. lightweight telemetry;
5. OpenClaw/NemoClaw only if low-risk;
6. tiny second CLI case.

No second UI.

---

## 11. Hard clocks

- **16:15:** hard feature freeze.
- **17:30:** no product changes; submission/export/verification only.
- **18:00:** stop all coding and Cursor/Codex prompting.
- **19:00:** deck due.
- **19:30:** top-8 pitches.

Target actual BuilderBase submission before 17:45.

---

## 12. What not to build

Do not add:
- universal cartridge compiler;
- arbitrary SOP ingestion;
- vector DB;
- Redis/Postgres;
- Kubernetes;
- generic workflow builder;
- second polished case/UI;
- LLM final judge;
- model voting;
- cloud inference;
- autonomous external/irreversible actions.

If it does not improve live reliability, mandatory stack proof, differentiation, or judge memorability, do not build it.

---

## 13. Q&A anchors

**Isn't this five agents agreeing?**  
No. Agents produce cognition. Final permission is deterministic Python.

**Why MongoDB?**  
It gives durable audit/replay of the exact evidence, candidates, approvals and verification. It never decides permission.

**Why OpenShell?**  
It proves sensitive local inference/tools can work while unauthorized external egress is blocked.

**What if the model changes its wording?**  
Model text may vary. Permission consequences are applied to validated structured facts/candidates.

**How do we know it isn't hardcoded?**  
Change a material fact/case input and show a different contract outcome; also use the loss-leader objective conformance case.

---

## 14. Final sentence

> **The AI recommends. Resolve decides whether that exact recommendation has earned permission.**
