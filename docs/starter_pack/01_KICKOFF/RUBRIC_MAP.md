# Hack NYC — Rubric / Mandatory-Rule Map

Organizer-confirmed mandatory items must be visible in the demo/submission even if they are not separately weighted.

| Item | Status | Where judges see it | Proof | Owner |
|---|---|---|---|---|
| Functioning agent built day-of | REQUIRED | repo/provenance | kickoff SHA + commit history | Coder 2 / Business 2 |
| Local inference on GB10 | REQUIRED | runtime header + architecture | model/runtime receipt | Coder 1 |
| At least 1 of NemoClaw/OpenClaw/OpenShell | REQUIRED | architecture/demo | OpenShell policy + local tool proof | Coder 1 |
| MongoDB | REQUIRED | audit/replay panel | local Mongo health + journal/replay | Coder 1 + Coder 3 |
| Submission before 18:00 | REQUIRED | BuilderBase | submission receipt | Business 2 |
| No coding/prompting after 18:00 | REQUIRED | team process | hard freeze | Everyone |

## Published judging categories

| Criterion | Weight | Where judges see it | Proof | Owner | Status |
|---|---:|---|---|---|---|
| Technical execution | TBD | live demo | local Qwen + OpenShell + MongoDB + deterministic contract + commit + verify | Coders | OPEN |
| Usefulness | TBD | first 60 sec + result | payment success 98.6% -> 79%, unsafe shortcut, bounded recovery | Business 1 | OPEN |
| Local-first design | TBD | runtime proof | GB10 local inference + public egress blocked + local tool pass | Coder 1 | OPEN |
| Pitch quality | TBD | 5-min pitch | live behavior, approval mutation, replay, crisp close | Business 2 | OPEN |

## Rule

Every row needs visible proof. Do not merely mention MongoDB/OpenShell in architecture; show one real receipt or behavior.
