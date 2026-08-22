# Coder 1 final regression — 2026-08-22

The frozen image, model, flags, and exposure were not changed. Expensive 15K gates were not repeated because the runtime profile was unchanged.

GB10=PASS — `nvidia-smi` reports NVIDIA GB10 and driver 580.159.03
VLLM=PASS — container running; vLLM 0.21.0+2325b6f0.dev; pinned digest matches
MODEL=PASS — `/v1/models` contains `qwen3.8-resolve`; exact `RESOLVE_OK` smoke passed
STRUCTURED_OUTPUT=PASS — schema parsed with BLOCK / TRAFFIC_CAP / KEEP_CURRENT_ROUTING
TOOL_CALL=PASS — actual `lookup_test_fact(fact_id="FACT-742")` event and local result passed
MONGODB=PASS — ping returned `{ ok: 1 }`
MONGO_PERSISTENCE=PASS — `C1_FINAL_PASS` probe remained after container restart and readiness wait
OPENSHELL=PASS — `/usr/bin/openshell` and gateway both report 0.0.91; sandbox Ready
PUBLIC_EGRESS_BLOCK=PASS — sandbox curl to `http://example.com/` received policy HTTP 403 and curl exit 22
LOCAL_MODEL_ACCESS=PASS — sandbox curl to `http://host.openshell.internal:8000/v1/models` returned `qwen3.8-resolve`

Note: the first Mongo read immediately after restart raced server startup and returned connection refused. The bounded readiness poll then succeeded and the persisted document was present. This is expected restart warm-up, not data loss.

VLLM_RESTART_RECOVERY=PASS — existing frozen container recovered `/v1/models` in 185 seconds; post-restart `RESOLVE_OK` passed
