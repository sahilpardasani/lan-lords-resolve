# Start here

This is the shortest path to a working checkout. The full product story is in [README.md](README.md). GB10 operators should continue to [DEPLOY.md](DEPLOY.md) after step 3.

```bash
git clone https://github.com/YashM1503/lan-lords-resolve.git
cd lan-lords-resolve
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Prove the repo before you claim anything

```bash
python3 scripts/validate_payment_fixture.py
python3 scripts/import_mongo_fixture.py --dry-run
bash scripts/qa_public_sweep.sh
```

Open [`Resolve_Showcase.html`](Resolve_Showcase.html) in a browser for the permission-loop walkthrough (including the 17.4% → 50% mutation beat).

## Run the HTTP surface (no GB10 required for mocks)

Resolve must bind **8080**. Port **8000** is reserved for local vLLM.

```bash
set -a && [ -f .env ] && . ./.env && set +a
uvicorn app:app --host 127.0.0.1 --port "${RESOLVE_PORT:-8080}"
```

```bash
curl -sS http://127.0.0.1:8080/health
```

Optional: `python3 demo_offline.py` or `python3 cli.py`.

## Product lock (does not change)

> The AI recommends. Resolve decides whether that exact recommendation has earned permission.

- Five logical roles on one local Qwen. No LLM Judge.
- Eight-gate Python contract. Fail closed.
- MongoDB records decisions. It does not make them.
- Same `DecisionInput` → same verdict, even if Mongo is offline.
- Primary demo: synthetic payment failover, 17.4% of *total* traffic, live approval, independent verification.

## If you have the GB10

1. `runtime/run_vllm.sh` → `http://127.0.0.1:8000/v1`
2. `runtime/run_mongodb.sh` → `mongodb://127.0.0.1:27017`
3. Resolve on 8080
4. `python3 runtime/doctor.py`
5. OpenShell: public HTTP blocked, local Qwen pass, local Resolve pass

Do not point `LOCAL_OPENAI_COMPATIBLE_ENDPOINT` at a cloud model.

Day-of team prompts and event clocks: [docs/HACKATHON.md](docs/HACKATHON.md).
