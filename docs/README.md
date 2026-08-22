# Documentation

Resolve documentation is split so a public reader can learn the product without walking the day-of hackathon packet.

## Product (start here)

| Document | Audience |
|---|---|
| [../README.md](../README.md) | What Resolve is, how a run works, demo numbers, repo map |
| [../START_HERE.md](../START_HERE.md) | Shortest checkout → fixture → tests → app path |
| [../DEPLOY.md](../DEPLOY.md) | GB10 operator order (vLLM 8000, Resolve 8080, Mongo 27017) |
| [../ARCHITECTURE.md](../ARCHITECTURE.md) | Frozen P0 architecture: roles, contract, Mongo, OpenShell |
| [../cases/primary/EXPECTED.md](../cases/primary/EXPECTED.md) | Canonical payment-failover beats |
| [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) | What is proven vs still integration |

## Data and audit

| Document | Audience |
|---|---|
| [SOURCE_RECONCILIATION.md](SOURCE_RECONCILIATION.md) | How the 500-row fixture was derived from source materials |
| [../data/mongodb/README.md](../data/mongodb/README.md) | What may be imported into Mongo (never a live approval) |

Do not invent a second cohort. If `cases/primary/` or `data/canonical/` is missing on a checkout, wait for that SHA.

## Runtime (Dell GB10)

| Document | Audience |
|---|---|
| [../runtime/README.md](../runtime/README.md) | vLLM / Mongo / doctor / OpenShell policy |
| [C1_OPERATIONS.md](C1_OPERATIONS.md) | Lifecycle and recovery |
| [OPENSHELL_HANDOFF.md](OPENSHELL_HANDOFF.md) | Public-block / local-Qwen / local-Resolve proofs |
| [C1_QA_REPORT.md](C1_QA_REPORT.md) | Acceptance gates |
| [C1_RED_TEAM.md](C1_RED_TEAM.md) | Negative tests |
| [../evidence/model_acceptance/NVFP4_KNOWN_GOOD_PROFILE.md](../evidence/model_acceptance/NVFP4_KNOWN_GOOD_PROFILE.md) | Frozen NVFP4 launch profile |

## Legal and hygiene

| Document | Audience |
|---|---|
| [../LICENSE](../LICENSE) | Apache-2.0 |
| [../NOTICE](../NOTICE) | Attribution |
| [LICENSING.md](LICENSING.md) | What Apache-2.0 covers vs third-party artifacts |
| [../THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) | Pinned images, model revision, Mongo, OpenShell |
| [../SECURITY.md](../SECURITY.md) | How to report issues |
| [../CONTRIBUTING.md](../CONTRIBUTING.md) | Single-writer boundaries and test bar |
| [REPO_PREP.md](REPO_PREP.md) | Public-push / judge-clone checklist |

## Event archive

Day-of process files (team split, start prompts, master plan, starter pack) live under [HACKATHON.md](HACKATHON.md). They are historical. They are not the product specification when they disagree with `README.md`, `cases/primary/`, or `resolve/contract.py`.
