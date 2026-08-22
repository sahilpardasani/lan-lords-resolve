# Runtime operations

GB10 / vLLM / Mongo / OpenShell operators start here. Product context: [../README.md](../README.md). Start order: [../DEPLOY.md](../DEPLOY.md).

The scripts in this directory reproduce the accepted local services. Read the corresponding script before running it, and do not launch a duplicate container while the accepted service is already healthy.

Resolve HTTP is **8080**. This directory's vLLM script binds **8000**. Do not swap those ports.

## Components

- `run_vllm.sh` starts the NVIDIA-pinned vLLM image with the NVFP4 model mounted read-only, loopback-only host exposure, a 32K context window, and concurrency of one.
- `run_mongodb.sh` starts ARM64 MongoDB with a named volume and loopback-only host exposure.
- `model_acceptance.py` exercises the model acceptance gates and writes receipts under `evidence/model_acceptance/`.
- `openshell-zero-egress.yaml` is the deny-by-default OpenShell policy used for the public-block/local-model-pass proof.

## Stable integration contract

```text
OpenAI base URL: http://127.0.0.1:8000/v1
Model:           qwen3.8-resolve
MongoDB URI:     mongodb://127.0.0.1:27017
```

The model endpoint is independent of MongoDB and OpenShell. Application startup must not make model availability conditional on either service.

The accepted vLLM profile currently uses eager execution for GB10 stability. Parser support is `qwen3` for reasoning and `qwen3_coder` for tool calls. See the frozen profile for the exact image digest and launch command.

## Evidence

Operational receipts are versioned under `evidence/runtime/`; model requests and results are under `evidence/model_acceptance/`. Raw logs and generated runtime data are intentionally ignored.


## Read-only readiness and negative tests

Run `python3 runtime/doctor.py` for PASS/WARN/FAIL diagnostics. Run `python3 -m unittest -v runtime.tests.test_runtime` for non-destructive live/static checks. Neither command installs, repairs, restarts, or rewrites runtime configuration.

Lifecycle and recovery commands are documented in `docs/C1_OPERATIONS.md`. OpenShell application integration is documented in `docs/OPENSHELL_HANDOFF.md`.
