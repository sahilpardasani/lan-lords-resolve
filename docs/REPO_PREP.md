# Repo cleaning and prepare methods

Use this before a public push, a judge clone, or a GB10 fetch.

## Lane split

| Lane | Owner | Do not touch from this hygiene branch |
|---|---|---|
| Canonical case + 500-row fixture + validator | Codex / Mac handoff | `cases/primary/**`, `data/**`, `docs/SOURCE_RECONCILIATION.md`, `docs/source_material/original/**`, `scripts/validate_payment_fixture.py`, `scripts/import_mongo_fixture.py`, `evidence/data_integrity/**` |
| Deterministic core | Coder 2 | `resolve/case.py`, `resolve/contract.py`, `resolve/approval.py`, `resolve/journal.py` |
| Product integration | Coder 3 | `resolve/runtime.py`, `resolve/context.py`, `resolve/tools.py`, `resolve/mongo_store.py`, `app.py`, `simulator/**`, `static/**` |
| GB10 runtime | Coder 1 | `runtime/**`, `evidence/model_acceptance/**`, `evidence/openshell/**` |
| Public/legal/deploy docs | this lane | LICENSE, NOTICE, README, DEPLOY, CONTRIBUTING, SECURITY, requirements, `.env.example` |

## Clean checklist

```text
[ ] git status --short is understood
[ ] no .env, *.pem, *.key, credentials/
[ ] no MODELS/, *.gguf, *.safetensors, hf_cache/
[ ] no mongodb-data/ or data/db/
[ ] no recordings/ or SURVIVAL/ binaries
[ ] no AppleDouble ._* files
[ ] LICENSE is Apache-2.0
[ ] NOTICE and THIRD_PARTY_NOTICES.md present
[ ] requirements.txt and .env.example present
[ ] scripts/qa_public_sweep.sh PASS
```

## Public product vs hackathon archive

| Repository | Role |
|---|---|
| `YashM1503/lan-lords-resolve` | Public product snapshot |
| `YashM1503/lan-lords-resolve-hacknyc` | Day-of working archive |

Do not flip the archive repo to public. Do not rewrite `cases/primary/` or `data/` to make a README prettier.

## Prepare for public GitHub

1. Stay on a docs/hygiene branch if Codex is writing case/data files.
2. Do not rewrite Business 1 / Codex facts to make a README prettier.
3. Use synthetic-data wording only.
4. Keep the repository free of model weights. Link to the local GB10 path in ops docs.
5. After review: `git push` the hygiene branch, then merge to `main` if it does not collide with the Codex SHA.
6. Public snapshot excludes local secrets, model weights, `docs/source_material/original/` binaries, and raw `server.log` files.

## Prepare for GB10 fetch

The GB10 must check out the **exact Mac/GitHub SHA**. Do not regenerate canonical rows on GB10.

```bash
git fetch origin
git rev-parse HEAD   # must equal the published SHA
bash scripts/qa_public_sweep.sh
# then, only if present:
python scripts/validate_payment_fixture.py
```

## Claims

Do not claim a live GB10 trial, OpenShell local-Resolve PASS, or `$8.33M` savings from this hygiene commit. Those require the Codex data SHA and a real GB10 run.
