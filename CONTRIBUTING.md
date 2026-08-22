# Contributing

Resolve was built during Dell × NVIDIA HackNYC. The architecture is frozen: deterministic permission around a local, nondeterministic model. Please keep that boundary intact.

## Before you change anything

1. Read [README.md](README.md) and [ARCHITECTURE.md](ARCHITECTURE.md).
2. Do not point the runtime at a cloud LLM.
3. Do not teach `contract.py` to query MongoDB.
4. Do not preload a valid approval, commit, or verification into the fixture.
5. Do not rewrite `cases/primary/` or `data/canonical/` to make a README prettier.

```bash
bash scripts/qa_public_sweep.sh
python3 scripts/validate_payment_fixture.py
git status --short
```

## Where code lives

| Path | Responsibility |
|---|---|
| `resolve/case.py`, `contract.py`, `approval.py`, `journal.py` | Deterministic permission core. No I/O. |
| `resolve/runtime.py`, `context.py`, `tools.py`, `mongo_store.py`, `app.py`, `simulator/`, `static/` | Integration, HTTP, simulator, UI |
| `runtime/`, `evidence/model_acceptance/`, `evidence/runtime/` | GB10 / vLLM / OpenShell / Mongo process |
| `cases/primary/**`, `data/**`, `docs/SOURCE_RECONCILIATION.md`, `scripts/validate_payment_fixture.py` | Canonical synthetic fixture |

Do not silently edit another lane to make a test pass. If two lanes must meet, add an adapter — do not weaken a gate.

## Runtime rule

ChatGPT, Cursor, and Codex are development tools only. They must not be imported by the Resolve application path. All inference stays on `LOCAL_OPENAI_COMPATIBLE_ENDPOINT`.

## Claims

Do not claim a live GB10 trial, OpenShell local-Resolve PASS, or `$8.33M` savings from a docs-only change. Those require the published fixture SHA and a real GB10 run. The $8.33M figure is modeled payment throughput returning sooner, not revenue.

## Pull requests

Small, reviewed merges only. Describe *why* the change exists. Link the gate or fixture invariant it preserves.
