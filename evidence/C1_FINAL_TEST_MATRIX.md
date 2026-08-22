# Coder 1 final test matrix — 2026-08-22

| Check | Status | Evidence |
|---|---|---|
| RUNTIME_BOOT | PASS | Existing pinned vLLM container recovered after restart in 185 seconds. |
| MODEL_ENDPOINT | PASS | `/v1/models` contains `qwen3.8-resolve`. |
| SHORT_INFERENCE | PASS | Exact `RESOLVE_OK`, including after restart. |
| STRUCTURED_OUTPUT | PASS | BLOCK / TRAFFIC_CAP / KEEP_CURRENT_ROUTING parsed against schema. |
| TOOL_CALL | PASS | Actual local `lookup_test_fact` event passed. |
| MONGO_PING | PASS | `{ ok: 1 }`. |
| MONGO_PERSISTENCE | PASS | Probe survived container restart/readiness wait. |
| OPENSHELL_PUBLIC_BLOCK | PASS | Explicit policy HTTP 403, curl exit 22. |
| OPENSHELL_LOCAL_MODEL | PASS | Sandbox model list contains accepted alias. |
| OPENSHELL_LOCAL_RESOLVE | PENDING | Genuine external dependency: Coder 3 has not supplied an application endpoint. |
| PORT_EXPOSURE | PASS | No wildcard host publication for vLLM/Mongo; gateway binds loopback/private bridge only. |
| MODEL_READ_ONLY | PASS | `/model` bind has `RW=false`. |
| SECRET_SCAN | PASS | No tracked credential signatures, env files, or private-key files detected. |
| WEIGHT_SCAN | PASS | No tracked safetensors, GGUF, or binary model files. |
| PATH_SCAN | PASS | No stale macOS absolute paths. |
| DOCTOR | PASS | 26 diagnostic lines, zero warnings/failures. |
| SHELL_SYNTAX | PASS | All tracked shell scripts pass `bash -n`. |
| PYTHON_SYNTAX | PASS | All runtime Python files compile. |
| RUNTIME_NEGATIVE_TESTS | PASS | 21 tests passed, zero failed. |
| GIT_DIFF_CHECK | PASS | `git diff --check` clean before commit. |
| LICENSE_FILES | PASS | Root MIT license limits scope to LAN LORDS-authored material. |
| THIRD_PARTY_NOTICES | PASS | Third-party boundaries, pins, and unresolved verification are explicit. |

Totals: PASS=21, FAIL=0, PENDING=1. The pending item is solely the external Coder 3 endpoint.
