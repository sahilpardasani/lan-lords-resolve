# Resolve

**Local execution-assurance for consequential enterprise AI.**

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

> The AI proposes the fix. Resolve decides whether that exact action has earned permission.

Resolve sits between a local model and an operational system. The model can investigate, argue, and recommend. A typed, deterministic contract decides whether that *exact* recommendation is admissible. MongoDB records what happened. It never grants permission.

Built by **LAN LORDS** at Dell × NVIDIA HackNYC (August 22, 2026). ChatGPT, Cursor, and Codex were development tools only. They are not imported by the runtime and are not part of any live inference path.

**Repositories:** public product [`YashM1503/lan-lords-resolve`](https://github.com/YashM1503/lan-lords-resolve) · day-of archive [`YashM1503/lan-lords-resolve-hacknyc`](https://github.com/YashM1503/lan-lords-resolve-hacknyc)

**License:** [Apache License 2.0](LICENSE)

---

## Why this exists

Enterprise AI already writes good recommendations. The failure mode is not “the model is silent.” It is “the model is confident, the action is consequential, and nothing in the path can prove that *this exact action* was allowed.”

Resolve treats permission as a separate computational problem from reasoning:

| Layer | What it may do | What it may not do |
|---|---|---|
| Local Qwen (five logical roles) | Retrieve evidence, form hypotheses, propose a bounded candidate, attack that candidate | Authorize itself, emit gate tokens that the runtime trusts, talk to a cloud LLM |
| Resolve contract | Validate structured facts and compute a disposition | Call the model, query MongoDB, read the clock, or “helpfully” relax policy |
| Human approval | Bind one exact candidate, for a bounded time, once | Approve a class of future actions, survive a material mutation, or be preloaded |
| MongoDB journal | Persist case, evidence, candidates, approvals, verification, replay | Change a verdict if the database is down or edited |

The architecture claim is **deterministic permission around nondeterministic cognition**. The model’s wording can vary. The same `DecisionInput` must produce the same contract verdict.

---

## How a run works

```text
local files / MongoDB
        │
        ▼
 local Qwen on GB10          five logical roles
 (127.0.0.1:8000/v1)         main · scout · investigator
        │                    planner · challenger
        ▼
 deterministic Resolve contract     eight gates, fail-closed
        │
        ▼
 exact human approval               fingerprint + expiry + one-use
        │
        ▼
 bounded local effect               simulator / admitted action
        │
        ▼
 independent verification           read actual state, not the model
        │
        ▼
 MongoDB journal / replay           audit substrate, not authority
```

Required stack: Dell Pro Max / GB10, local Qwen, OpenShell, MongoDB, Python / FastAPI, a local deterministic simulator.

### Five roles, one model

One local Qwen process plays five *logical* roles. There is no swarm of remote agents.

| Role | Job |
|---|---|
| `main` | Orchestrate the bounded loop. It does not grant permission. |
| `scout` | Retrieve and cite evidence by ID. |
| `investigator` | Hold competing hypotheses and name discriminating tests. |
| `planner` | Propose a *bounded* candidate, not “do whatever works.” |
| `challenger` | Try to falsify the candidate. The Challenger is not a judge. |

No LLM Judge. No model-produced `PASS` / `FAIL` token is treated as authorization. The Python contract recomputes every gate.

### Eight-gate contract

Implemented in [`resolve/contract.py`](resolve/contract.py). The module has no model, network, database, clock, or filesystem access.

| Gate | Question |
|---|---|
| **Intent** | Are we optimizing the authorized objective, not an anti-objective? |
| **Evidence** | Is material evidence present, current, and referenced by ID? |
| **Constraints** | Does the candidate violate a hard typed rule? |
| **Consequence** | What is the downside class if this is wrong (`C0`–`C4`)? |
| **Reversibility** | Can it be undone when the case requires that? |
| **Rehearsal** | Did the required bounded simulation pass? |
| **Authority** | Is the correct human role bound to *this* fingerprint? |
| **Verification** | Can actual post-action success or failure be observed? |

Each gate is `PASS`, `FAIL`, or `UNKNOWN`. Disposition is fail-closed:

```text
any required hard gate FAIL     → BLOCKED
any required material UNKNOWN   → MORE_EVIDENCE_REQUIRED
gates pass + human required     → WAITING_HUMAN
all required gates pass         → ADMISSIBLE
otherwise                       → BLOCKED
```

Approvals bind the exact candidate, case, evidence, starting state, decision, authority, and expiry. Change a material field (for example `17.4% → 50%`, or `US → GLOBAL`) and the old approval is dead. One use. No class-of-actions signatures.

### MongoDB is the audit substrate

MongoDB is required and used for real documents:

- case snapshots
- evidence references
- candidate snapshots
- approval artifacts
- verification events
- canonical journal events
- replay / export

It is **not** the authority. `contract.py` never queries Mongo. The same `DecisionInput` must yield the same verdict if Mongo is offline, empty, or tampered. A hash-chained journal records decisions; it does not grant them.

---

## The primary demo

**Case:** `payment_failover_001`  
**Classification:** synthetic demonstration data. Not JPMorgan, Mastercard, processor, merchant, or customer incident data.

Payment authorization success falls from **98.6% to 79.0%**. A tempting “fix” is a GLOBAL / 100% failover onto Processor B. That candidate is `BLOCKED` (`COUNTRY_NOT_ALLOWED`, `TRAFFIC_CAP_EXCEEDED`) whether or not the model notices the restriction. Typed policy is the authority.

The Planner’s bounded alternative covers **17.4% of total traffic** (87 of 500 records): only affected U.S. Visa/Mastercard transactions at or below $5,000, under a hard cap of **20% of total traffic** plus per-transaction eligibility. “20% of eligible traffic” is retired language.

| Beat | What must happen |
|---|---|
| Stage 1 | Stale Processor B capacity → `MORE_EVIDENCE_REQUIRED` |
| Stage 2 | Current capacity + passing rehearsal → `WAITING_HUMAN` |
| Approval | Created live, bound to this fingerprint. Nothing valid is preloaded. |
| Mutation | `17.4% → 50%` (or `US → GLOBAL`) invalidates the approval |
| Commit | Exactly 87 incident failures route to B and recover |
| Verify | Success ≥ 95%, **0** unauthorized B routes, **0** policy violations |

Canonical 500-row cohort (one identity across baseline / incident / recovery):

| Metric | Value |
|---|---|
| Baseline successes | 493 / 500 (**98.6%**) |
| Incident successes | 395 / 500 (**79.0%**) |
| Recovery successes | 482 / 500 (**96.4%**) |
| Incident failures | 105 |
| Routed to Processor B | **87** (17.4% of total) |
| Left on Processor A (still failed) | 18 |
| Unauthorized B routes | **0** |
| Policy violations | **0** |
| Weighted cohort flow | $12.5M modeled throughput |

The **$8.33M** figure is a duration sensitivity: that amount of modeled payment flow returns to normal processing sooner when modeled recovery time falls from 30 minutes to 10. It is **not** revenue, profit, guaranteed savings, or “87 transactions = $8.33M.”

Validate the fixture before any demo claim:

```bash
python3 scripts/validate_payment_fixture.py
python3 scripts/import_mongo_fixture.py --dry-run
```

See [case expectations](cases/primary/EXPECTED.md), [source reconciliation](docs/SOURCE_RECONCILIATION.md), and [what is still integration work](docs/IMPLEMENTATION_STATUS.md).

---

## What is in this repository

```text
resolve/                 Deterministic core + integration surface
  case.py                Case normalize / fingerprint
  contract.py            Eight-gate permission contract
  approval.py            Exact, one-use, mutation-invalidated approval
  journal.py             Hash-chained journal integrity (pure)
  mongo_store.py         Persistence adapter (records; does not decide)
  runtime.py             Run loop (swap mocks → live Qwen + contract)
  context.py, tools.py   Evidence / tool context
cases/primary/           Frozen payment case + staged evidence
data/canonical/          500-row cohort, policy, expected metrics
data/mongodb/import/     Pre-run fixtures only (no live approval)
runtime/                 GB10 vLLM, Mongo, OpenShell, doctor
app.py                   FastAPI: health, run, replay, journal, audit
cli.py                   Terminal narrator for the same run
static/                  Operator dashboard (legacy projection until live bind)
Resolve_Showcase.html    Static judge / investor walkthrough of the loop
simulator/               Deterministic local effect
scripts/                 Fixture validator, Mongo import, public QA sweep
tests/                   Contract, approval, journal, fixture, store
evidence/                Runtime and model-acceptance receipts
docs/                    Architecture, deploy, licensing, hackathon archive
```

Model weights, Docker images, and Hugging Face caches are **not** in Git.

---

## Quick start

You do not need a GB10 to read the contract, validate the fixture, or open the showcase. You do need a GB10 for local Qwen.

### 1. Install the Python surface

```bash
git clone https://github.com/YashM1503/lan-lords-resolve.git
cd lan-lords-resolve
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Python 3.12+ for the app; 3.13 is what the current core tests were run on.

### 2. Prove the fixture and the core

```bash
python3 scripts/validate_payment_fixture.py
bash scripts/qa_public_sweep.sh
```

The sweep expects a clean tree (no `.env`, weights, or Mongo data files) and runs the Mongo-store plus deterministic-core tests.

### 3. Look at the product without a GPU

| Artifact | What you see |
|---|---|
| [`Resolve_Showcase.html`](Resolve_Showcase.html) | Full permission-loop walkthrough, including the 17.4% → 50% mutation beat |
| `python3 demo_offline.py` | Offline narrator against mocks |
| `uvicorn app:app --host 127.0.0.1 --port 8080` | HTTP API + `static/index.html` (bind **8080**, never 8000) |

### 4. Run on a GB10

vLLM already owns **8000**. Resolve owns **8080**. Mongo is loopback `:27017`.

```text
1. runtime/run_vllm.sh      → http://127.0.0.1:8000/v1   alias qwen3.8-resolve
2. runtime/run_mongodb.sh   → mongodb://127.0.0.1:27017
3. uvicorn app:app --host 127.0.0.1 --port 8080
4. curl -sS http://127.0.0.1:8080/health
5. python3 runtime/doctor.py
```

OpenShell P0 (deny-by-default):

```text
public HTTP     → BLOCKED
local Qwen      → PASS    (127.0.0.1:8000)
local Resolve   → PASS    (127.0.0.1:8080/health)   after Resolve is actually up
```

Full operator order: [DEPLOY.md](DEPLOY.md). Runtime internals: [runtime/README.md](runtime/README.md).

---

## HTTP surface

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Static dashboard |
| `GET` | `/health` | Mongo / journal / contract-core status |
| `POST` | `/run` | Execute one Resolve run |
| `GET` | `/runs/{run_id}` | Export a recorded run |
| `GET` | `/journal/{run_id}` | Ordered journal events |
| `GET` | `/replay/{run_id}` | Replay projection |
| `GET` | `/audit` | Aggregation views |
| `GET` | `/why-blocked/{run_id}` | Blocked-decision record |
| `POST` | `/tamper/{run_id}` | Demo-only journal tamper (integrity check) |

CLI: `python3 cli.py`, `python3 cli.py --audit`, `python3 cli.py --replay RUN_ID`.

Environment ([`.env.example`](.env.example)):

```text
LOCAL_OPENAI_COMPATIBLE_ENDPOINT=http://127.0.0.1:8000/v1
RESOLVE_MODEL_ALIAS=qwen3.8-resolve
RESOLVE_MONGO_URI=mongodb://127.0.0.1:27017
RESOLVE_PORT=8080
```

Do not point `LOCAL_OPENAI_COMPATIBLE_ENDPOINT` at a remote model.

---

## Honest status

The repository can claim a tested deterministic core, a validated 500-row canonical fixture, GB10 runtime receipts (NVFP4 + vLLM gates A0–A7, local Mongo, OpenShell public-block / local-Qwen-pass), and a static showcase of the intended loop.

It cannot yet claim a completed live GB10 *model → contract → approval → effect → verify* trial. [`docs/IMPLEMENTATION_STATUS.md`](docs/IMPLEMENTATION_STATUS.md) lists the remaining binds: live Qwen in place of `mocks.mock_ai`, `resolve.contract` in place of `mocks.mock_contract`, load `cases/primary` instead of a hard-coded context, a real human-approval action (the current runtime auto-approves `WAITING_HUMAN`), independent verification against actual routing, and OpenShell local-Resolve PASS after 8080 is healthy.

Until those pass on the GB10 at a published SHA, do not say Gate E is done.

---

## Documentation map

Start at [docs/README.md](docs/README.md).

| Doc | Contents |
|---|---|
| [START_HERE.md](START_HERE.md) | Shortest path to a local checkout |
| [DEPLOY.md](DEPLOY.md) | GB10 start order, ports, OpenShell proofs |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Frozen P0 architecture |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to change this repo without breaking the contract |
| [SECURITY.md](SECURITY.md) | What to report, what stays loopback |
| [docs/LICENSING.md](docs/LICENSING.md) | Apache-2.0 boundary vs third-party artifacts |
| [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) | Pinned model / image / Mongo / OpenShell identities |
| [docs/IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md) | What is green vs still integration |
| [docs/HACKATHON.md](docs/HACKATHON.md) | Event process files kept as archive |

---

## License and data

LAN LORDS-authored source and documentation are [Apache-2.0](LICENSE). See [NOTICE](NOTICE).

Model weights, NVIDIA NGC images, MongoDB Server, OpenShell, CUDA, and host binaries are **separate works**. They are referenced, not redistributed. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and [docs/LICENSING.md](docs/LICENSING.md).

The payment incident, operational rules, and telemetry in this repository are **synthetic**. They are not real customer records.

---

## Provenance

Initialized during the official HackNYC build window. The GB10 runtime history was joined through an explicit unrelated-history merge so both lineages remain auditable.

The day-of working repository — packets, start prompts, receipts, and merge history — is archived at [`YashM1503/lan-lords-resolve-hacknyc`](https://github.com/YashM1503/lan-lords-resolve-hacknyc). This public tree is the product snapshot.
