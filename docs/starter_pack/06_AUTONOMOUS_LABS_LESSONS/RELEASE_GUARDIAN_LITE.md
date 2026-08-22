# Autonomous Labs Lessons — Hackathon Lite

Use the lessons, not the implementation.

## Carry over
- One canonical journal/source of truth.
- One deterministic state machine.
- One admission path before every material model/tool/action call.
- Evidence records separated from model interpretation.
- Bounded retries; no blind retry of unknown side effects.
- Cancellation checked before admission.
- Exact approval binding for consequential/reversible actions.
- Reversibility before consequence.
- Commit followed by independent verification.
- UI as a projection of canonical events.
- Small reversible changes.
- Baseline before remediation.
- One canonical rule + many consumers.

## Do not carry over for this hackathon
- multi-tenancy;
- production identity/OIDC;
- watches/schedules;
- distributed queues;
- multi-host leases;
- remote providers;
- HA/failover;
- production billing/quotas;
- a large plugin ecosystem;
- autonomous external write paths.

## Determinism language
Never say “Resolve is deterministic.” Say:
**“The model output can vary; the evidence, admission, state, approval, commit and verification invariants do not.”**

## Minimal consequence stance
All hackathon actions should terminate in a **local simulator**. External systems are read-only or absent. This is enough to demonstrate trustworthy decision-to-action mechanics without adding irreversible risk.
