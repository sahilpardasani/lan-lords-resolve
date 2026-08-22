# Coder 1 local operations

This guide operates only the frozen local GB10 stack. Never change the image/model digests, quantization, 32K context, concurrency of one, or `--enforce-eager` without an evidence-backed blocker and explicit review.

## vLLM

### Start

Confirm port 8000 is free and the exact pinned image is local. From the repository root run `runtime/run_vllm.sh`. It creates `resolve-vllm`, mounts `/home/dell/Desktop/LAN_LORDS_HACKNYC/MODELS/NVFP4` read-only, prevents pulls, and publishes loopback plus the private OpenShell bridge address.

### Check

Run `curl --fail --silent http://127.0.0.1:8000/v1/models` and confirm `qwen3.8-resolve`. Run `python3 runtime/doctor.py` for the full read-only check.

### Stop / restart

Use `docker stop resolve-vllm` to stop. Use `docker start resolve-vllm` to restart the accepted existing container. Follow logs with `docker logs --tail 100 -f resolve-vllm`. Startup takes several minutes while the checkpoint loads.

### Recover

If the existing container is missing, verify the model hashes and pinned local image first, confirm ports are free, then run `runtime/run_vllm.sh`. A name conflict means an existing container must be inspected; do not delete or replace it blindly. `--enforce-eager` is required: without it, the accepted image failed in the Torch AOT path. Do not permit downloads as a recovery shortcut.

## MongoDB

### Start / check

Run `runtime/run_mongodb.sh` only when no `resolve-mongodb` container exists. Check with `docker exec resolve-mongodb mongosh --quiet --eval 'db.runCommand({ping:1})'`. Data lives in named volume `resolve-mongo-data`.

### Stop / restart

Use `docker stop resolve-mongodb` and `docker start resolve-mongodb`. After restart, wait for ping before testing reads. MongoDB is the audit substrate, not Resolve decision authority.

### Recover

Inspect `docker logs --tail 100 resolve-mongodb`, confirm the exact digest and named volume, then start the existing container. Do not delete the volume. This local hackathon profile has no Mongo authentication; it must not contain production data or be treated as production-ready.

## OpenShell

### Start / check

The gateway is system-managed and must not be reinstalled. Check `/usr/bin/openshell --version`, `/usr/bin/openshell gateway info`, and `/usr/bin/openshell sandbox list`. Expected versions are CLI/gateway `0.0.91` and sandbox `resolve-containment` in `Ready` phase.

### Stop / restart / recover

Do not stop or restart the gateway as routine application lifecycle. If unhealthy, collect `gateway info`, sandbox status, effective policy, and logs and report the regression before repair. The accepted policy is `runtime/openshell-zero-egress.yaml`; do not claim containment from DNS failure alone.

## Verify

Run `python3 runtime/doctor.py` followed by `python3 -m unittest -v runtime.tests.test_runtime`. The authoritative acceptance profile is `evidence/model_acceptance/NVFP4_KNOWN_GOOD_PROFILE.md`.

## Frozen changes

Do not modify Ubuntu, kernel, NVIDIA driver, CUDA, Docker, NVIDIA Container Toolkit, vLLM image, model, quantization, eager mode, MTP/speculation, context, or public port exposure. Restore code from `origin/feat/gb10-nvfp4-runtime`; never delete model artifacts or database volumes as part of code recovery.
