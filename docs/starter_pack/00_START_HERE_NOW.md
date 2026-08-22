# LAN LORDS / Resolve — START HERE NOW

**Status:** live hackathon build  
**Organizer-confirmed rules:** use at least **1 of NemoClaw / OpenClaw / OpenShell**; **MongoDB is required**; all inference must run locally on the Dell GB10; submission is due before **18:00**; after 18:00 there is **no more coding or prompting**.

## Product lock

> **Resolve is a local AI troubleshooting and permission loop. The model can investigate and propose. Deterministic runtime logic decides whether the exact action has earned permission.**

P0 is now:

`local evidence -> five logical roles -> candidate -> challenger -> deterministic contract -> exact approval if needed -> bounded local action -> verify -> MongoDB audit/replay`

MongoDB is **the audit substrate, not the authority**.

## Primary demo lock

Use the **payment authorization outage**.

- baseline success: 98.6%
- incident success: 79%
- tempting candidate: 100% global failover to Processor B
- hard constraint: Processor B is authorized only for bounded eligible traffic
- safer candidate: bounded US failover, target 40%
- human approval: required
- memorable beat: approve exact action, mutate `US -> GLOBAL`, old approval becomes invalid
- verify: read the simulator's actual post-action state, not the model's claim

## Sponsor-stack priority

The organizer only requires at least one of:
- NemoClaw
- OpenClaw
- OpenShell

**P0: OpenShell first.** Prove:
`public HTTP -> BLOCKED`, `local Qwen -> PASS`, `local Resolve tool -> PASS`.

Do not let OpenClaw/NemoClaw delay the first working Resolve demo. Add them only if the core is already safe.

## MongoDB P0

Use MongoDB genuinely for:
- case snapshots
- evidence references
- canonical journal events
- candidate snapshots
- approval artifacts
- verification events
- replay

Never let `contract.py` query MongoDB. Same `DecisionInput` must produce the same contract verdict even if MongoDB is unavailable.

## Team now

- **Coder 1:** runtime / GB10 / model / OpenShell / local MongoDB
- **Coder 2:** deterministic core / contract / approval / journal integrity
- **Coder 3:** runtime integration / Mongo persistence adapter / simulator / API / UI / E2E
- **Business 1:** primary payment case facts, evidence and expected behavior
- **Business 2:** loss-leader proof, judge story, deck and submission

See `07_TEAM/TEAM_SPLIT.md`.

## Immediate checkpoints

### NOW -> first checkpoint
- Coder 1: local endpoint + OpenShell + MongoDB green
- Coder 2: minimum deterministic contract tests green
- Coder 3: payment simulator/API/UI running against mocks
- Business 1: freeze primary `case.yaml` + staged evidence
- Business 2: freeze loss-leader cases + judge narrative

### Next
Merge interfaces, replace mocks, run the first full payment case.

### Survival floor
Before optional work:
- one live successful run
- one replay
- screen recording
- exact Git SHA/tag
- Git bundle
- Mongo journal export
- runtime manifest
- zero-egress receipt
- pytest/doctor receipts
- exact case.yaml
- copy video/evidence to WD

### Hard clocks
- **16:15:** hard feature freeze
- **17:30:** submission/export/verification only
- **18:00:** STOP CODING and STOP CURSOR/CODEX PROMPTING
- **19:00:** slides/pitch deck due
- **19:30:** top-8 pitches begin

## One sentence everyone uses

> **The AI recommends. Resolve decides whether that exact recommendation has earned permission.**
