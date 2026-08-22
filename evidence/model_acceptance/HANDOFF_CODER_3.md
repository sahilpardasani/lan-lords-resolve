MODEL ENDPOINT: http://127.0.0.1:8000/v1
MODEL ALIAS: qwen3.8-resolve
OPENAI COMPATIBLE: YES
CONTEXT: 32768
TOOLS: PASS — qwen3_coder parser; three consecutive real tool events verified
THINKING: PASS — qwen3 parser; enable per request
RUNTIME PROFILE: evidence/model_acceptance/NVFP4_KNOWN_GOOD_PROFILE.md
MONGODB: mongodb://127.0.0.1:27017 — PASS, persistence verified

INTEGRATION RULES:
- Consume the existing OpenAI-compatible endpoint; do not tune or restart the model runtime unless an integration test proves a blocker.
- Keep model, MongoDB, and OpenShell startup independent.
- Do not place model weights, credentials, MongoDB data, or raw logs in Git.
- When the local Resolve endpoint is ready, send Coder 1 its exact loopback URL and health/tool route so the final OpenShell local-allow proof can be captured.

## Follow-up prompt for Coder 3

```text
You are Coder 3 for LAN LORDS / Resolve. Integrate the product with the already accepted local runtime; do not redesign or tune the runtime.

Use:
- OpenAI-compatible base URL: http://127.0.0.1:8000/v1
- Model alias: qwen3.8-resolve
- Context: 32768
- MongoDB: mongodb://127.0.0.1:27017
- Runtime profile: evidence/model_acceptance/NVFP4_KNOWN_GOOD_PROFILE.md

The model passed A0-A7, including deterministic short/structured output, three consecutive real tool calls, long-context retrieval, long-context tool selection, and the thinking challenger. MongoDB persistence passed. Treat this runtime profile as frozen.

Your tasks:
1. Point Resolve's OpenAI client at the base URL and model alias above.
2. Integrate application persistence with the MongoDB URI without making model boot depend on MongoDB.
3. Preserve the existing product contracts and business semantics; Coder 1 owns only runtime/infrastructure.
4. Run the smallest end-to-end integration test that proves Resolve can call the model and its local tool path.
5. Report the exact loopback Resolve endpoint and health/tool route to Coder 1 so OpenShell's local-Resolve allow proof can be completed.

Do not request model tuning unless you provide a reproducible failing integration request and response. Report: integration status, endpoint used, model alias used, tool-call status, MongoDB status, Resolve loopback URL, and any exact blocker.
```
