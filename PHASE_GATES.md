# Hack NYC — Phase Gates / Kill Switches

> **Archive.** Day-of kill switches. Current status: [docs/IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md). Event file map: [docs/HACKATHON.md](docs/HACKATHON.md).

The hack is already underway. Targets are operational, not theoretical.

| Gate | Required proof | If it fails |
|---|---|---|
| A — model runtime | NVFP4 endpoint on GB10; basic correctness/schema/tool path | switch to FP8 after short remaining timebox; if vLLM itself fails, GGUF/llama.cpp |
| B — OpenShell + zero egress | public HTTP BLOCK + local inference PASS + local tool PASS | fix policy/routing; do not add OpenClaw/NemoClaw yet |
| B2 — MongoDB required stack | local Mongo health + insert/read + indexes | Coder 1 fixes service; Coder 3 keeps integration on a small store interface |
| C — deterministic core | case/contract/approval/journal tests + objective tests green | cut nonessential UI; keep pure Python core |
| D — payment E2E | investigate -> unsafe candidate -> BLOCKED -> targeted evidence -> bounded candidate -> approval -> commit -> verify -> Mongo journal | reduce agents/context/UI before weakening permission rules |
| E — survival floor | successful live run + replay + screen recording + SHA/tag + git bundle + Mongo export + runtime/zero-egress/test receipts | stop all optional work |
| Optional proof | approval mutation, counterfactual/calibration, telemetry | only after E |
| 16:15 | HARD FEATURE FREEZE | reliability/demo only |
| 17:30 | NO PRODUCT CHANGES | submission/export/verification only |
| 18:00 | STOP CODING + STOP CURSOR/CODEX PROMPTING | pitch prep only |

## Sponsor rule

Only one of NemoClaw/OpenClaw/OpenShell is mandatory. P0 is OpenShell.

Do not let optional OpenClaw/NemoClaw integration delay Gate E.

## Mongo rule

MongoDB is mandatory, but it is not the permission engine.

If Mongo integration is causing coupling:
- keep `contract.py` pure;
- make `mongo_store.py` smaller;
- persist canonical events after core calculation.

## Model ladder

1. NVFP4 + vLLM
2. FP8 + separately validated vLLM profile
3. GGUF + llama.cpp if vLLM path fails

Do not restart a model comparison exercise.
