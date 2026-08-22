# Deploy Resolve (local GB10)

This is the public operator path. It does not call ChatGPT, Cursor, or Codex.

```text
local files / MongoDB
→ local Qwen on GB10 (127.0.0.1:8000)
→ five logical roles
→ deterministic Resolve contract
→ exact approval
→ local simulator
→ independent verification
→ MongoDB journal / replay
```

Resolve HTTP must bind **8080**. vLLM already owns **8000**.

Public product repo: `https://github.com/YashM1503/lan-lords-resolve`  
Hackathon archive: `https://github.com/YashM1503/lan-lords-resolve-hacknyc`

## Prerequisites

- Dell Pro Max / GB10 with the frozen NVFP4 + vLLM container
- Local MongoDB at `mongodb://127.0.0.1:27017`
- OpenShell deny-by-default policy
- Python 3.12+ for the Resolve app (3.13 for the current core tests)
- Model weights on local disk, not in Git

## One-time

```bash
git clone https://github.com/YashM1503/lan-lords-resolve.git
cd lan-lords-resolve
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Do not copy Hugging Face caches, `.env` secrets, or `MODELS/` into Git.

## Start order on GB10

1. Frozen vLLM profile: `runtime/run_vllm.sh` → `http://127.0.0.1:8000/v1`
2. Mongo: `runtime/run_mongodb.sh` or the existing `resolve-mongodb` container
3. Resolve app on **8080**, not 8000:

```bash
source .venv/bin/activate
set -a && [ -f .env ] && . ./.env && set +a
uvicorn app:app --host 127.0.0.1 --port "${RESOLVE_PORT:-8080}"
```

4. Health: `curl -sS http://127.0.0.1:8080/health`
5. OpenShell proofs after Resolve is actually up:

```text
public HTTP     → BLOCKED
local Qwen      → PASS   (127.0.0.1:8000)
local Resolve   → PASS   (127.0.0.1:8080/health)
```

Read-only readiness:

```bash
python3 runtime/doctor.py
```

## Data

Canonical payment fixtures:

```text
cases/primary/
data/canonical/
data/mongodb/import/
scripts/validate_payment_fixture.py
```

If those files are not on the checked-out SHA, do not invent a second dataset. Wait for that SHA, then:

```bash
python3 scripts/validate_payment_fixture.py
python3 scripts/import_mongo_fixture.py --dry-run
```

Import only pre-run fixtures (case, policy, cohort, evidence). Do not pre-load live approval, commit, verification, or a completed journal.

## QA before a public or judge machine

```bash
bash scripts/qa_public_sweep.sh
```

## Do not

- Point `LOCAL_OPENAI_COMPATIBLE_ENDPOINT` at a remote model
- Upgrade a working vLLM / Mongo stack mid-demo
- Drop unrelated Mongo databases
- Bind Resolve to port 8000
- Claim a completed live GB10 trial until [IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md) is green and a survival bundle exists
