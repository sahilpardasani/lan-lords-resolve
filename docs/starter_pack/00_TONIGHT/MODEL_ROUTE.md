# Model Route — SUPERSEDED PRE-EVENT NOTE / CURRENT LIVE LADDER

This file existed in the earlier pre-event pack. The hack is now live and the model order is frozen.

## Current ladder

1. **PRIMARY:** `unsloth/Qwen3.8-27B-NVFP4` + vLLM
2. **FALLBACK 1:** `Qwen/Qwen3.8-27B-FP8` + separately validated vLLM profile
3. **DISASTER BACKUP:** verified `unsloth/Qwen3.8-27B-GGUF` + llama.cpp only if the vLLM serving path is unavailable

Do not compare or reorder them.

Resolve depends only on:

`LOCAL_OPENAI_COMPATIBLE_ENDPOINT`

The organizer requires at least **1 of NemoClaw / OpenClaw / OpenShell**. P0 uses **OpenShell**.

See:
- `/00_START_HERE_NOW.md`
- `/03_QA/MODEL_ACCEPTANCE_SUITE.md`
- `/HACK_NYC_MASTER_PLAN.md`
