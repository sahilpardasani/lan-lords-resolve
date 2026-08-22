# doctor.py — P0 Diagnostic / Safe Recovery Specification

Build after kickoff.

## Report layers
`SYSTEM, MODEL, LONG_CONTEXT, TOOL_CALL, NVIDIA_STACK, EGRESS, RESOLVE_CORE, CASE, INTEGRATION, UI_DEMO`

Each run must save:
- human-readable text;
- JSON;
- timestamp;
- observed evidence;
- likely owning layer;
- next safe action.

## Allowed safe repairs
- restart a frozen known local process;
- clear a stale PID;
- free a known demo port;
- recreate disposable simulator/SQLite from a checked-in seed;
- recreate temp/run directories;
- restart the frozen selected model command.

## Forbidden repairs
- rewrite `contract.py`;
- rewrite tests;
- rewrite evidence;
- change expected dispositions;
- weaken constraints;
- alter prompts to force the golden answer.

`doctor.py` diagnoses and restores known operational state. It does not optimize the product by self-editing.
