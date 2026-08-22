# Implementation status after Mac data preparation

Starting point: GitHub `main` at `76bc682ae3f0b1b8920c3aca859ece916fd68ba9`.

## Green now

- Deterministic case normalization, contract gates, exact approval binding, one-use approval behavior, journal integrity, and Mongo persistence primitives have unit coverage.
- GB10 runtime assets, pinned local-model/Mongo container references, model acceptance artifacts, and OpenShell containment receipts are present.
- The payment business fixture is now one causal 500-transaction cohort with staged evidence and validated Mongo imports.
- No valid approval, execution, verification, live journal, or replay is preloaded by the fixture.

## Coding still required for a real end-to-end claim

1. Replace `mocks.mock_ai` with the local OpenAI-compatible Qwen client and structured role outputs.
2. Replace `mocks.mock_contract` in `resolve/runtime.py` with `resolve.contract` receipt builders and deterministic evaluation.
3. Load `cases/primary/case.yaml` and staged evidence instead of the hard-coded context dictionary.
4. Add the bounded stage-1 evaluation so stale capacity produces a real `MORE_EVIDENCE_REQUIRED` beat before stage 2.
5. Replace the legacy `US / 40%` candidate shape with the canonical `US / visa+mastercard / <= $5,000 / 17.4% of total` candidate.
6. Expose a real human approval API/UI action. The current runtime automatically issues approval when it sees `WAITING_HUMAN`.
7. Bind commit to the exact evaluated decision and consumed approval using the real approval module; add an idempotency/effect receipt and reconciliation path for unknown commit outcomes.
8. Make verification independently read actual routing and cohort outcomes, including zero unauthorized B routes and zero policy violations.
9. Project `MORE_EVIDENCE_REQUIRED`, `WAITING_HUMAN`, mutation invalidation, commit, independent verification, and Mongo replay from backend state in the dashboard. The current UI is a legacy animated mock flow.
10. Bind the Resolve application endpoint to the private OpenShell bridge and prove public egress blocked, local Qwen allowed, and local Resolve allowed from the same contained execution path.
11. Run and capture the complete trial on the GB10 at the exact pushed SHA, then produce live Mongo journal/replay and zero-egress receipts.

Until those items pass on the GB10, the repository can claim a tested deterministic core and a validated canonical fixture, but not a completed live local-model execution loop.
