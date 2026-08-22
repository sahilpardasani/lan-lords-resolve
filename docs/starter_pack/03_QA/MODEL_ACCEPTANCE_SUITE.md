# GB10 Model Acceptance Suite — Current Ladder

Run only the checks needed to establish a reliable local endpoint and tool path. Do not turn this into a model benchmark.

## Frozen ladder

1. **PRIMARY:** `unsloth/Qwen3.8-27B-NVFP4` + vLLM
2. **FALLBACK 1:** `Qwen/Qwen3.8-27B-FP8` + separately validated vLLM launch profile
3. **DISASTER BACKUP:** verified `unsloth/Qwen3.8-27B-GGUF` + llama.cpp if the vLLM path itself is unavailable

Do not reorder this ladder.

## A0 — artifact/tokenizer
- exact repo/revision/hash recorded;
- tokenizer/config present;
- no silent tiny-context truncation;
- NVFP4 tokenizer `.truncation` is `null` if that is part of the frozen receipt.

## A1 — GPU/server path
- server boots;
- GB10 GPU is actually used;
- no accidental CPU-only fallback;
- process remains stable.

## A2 — short correctness
Run a handful of small deterministic prompts. Do not over-benchmark.

## A3 — structured output
Require valid JSON/Pydantic-compatible output for the Resolve role schema.

## A4 — actual local tool dispatch
Expose one harmless local tool and require 3 real dispatches. Raw JSON that is never dispatched is a FAIL.

## A5 — long-context sentinel
If the demo needs long context, verify sentinel retrieval around the intended evidence length. Do not spend time proving context lengths the demo does not use.

## A6 — evidence -> tool
Place a required tool argument late in a representative evidence bundle and require the correct real tool call.

## A7 — selected sponsor component
Organizer requires at least **1 of NemoClaw / OpenClaw / OpenShell**.

P0 uses **OpenShell**.

Prove:
- public external request -> BLOCKED;
- local inference -> PASS;
- local Resolve tool -> PASS.

OpenClaw/NemoClaw are optional after Gate E unless organizers separately require them.

## A8 — zero egress receipt
Only after the evidence exists may the UI say:

`ZERO EGRESS VERIFIED`

## A9 — brief soak
Run enough repeated requests/tool calls to catch obvious instability. Stop once the path is credible.

## Switch rules

- If NVFP4 cannot become credible within the remaining model-debug timebox, switch to FP8.
- FP8 needs its own validated vLLM profile; do not assume model-name substitution.
- If **vLLM itself** is the failure surface, move to GGUF + llama.cpp.
- Do not reopen model comparison after one primary path is green.

## Product abstraction

Resolve talks only to:

`LOCAL_OPENAI_COMPATIBLE_ENDPOINT`
