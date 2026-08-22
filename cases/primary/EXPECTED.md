# Canonical payment failover expectations

This case is a synthetic conformance fixture. It is not JPMorgan, Mastercard, processor, merchant, or customer incident data.

1. The unsafe `GLOBAL / 100%` candidate is `BLOCKED` with at least `COUNTRY_NOT_ALLOWED` and `TRAFFIC_CAP_EXCEEDED`.
2. The bounded `US / visa+mastercard / <= $5,000 / 17.4%` candidate evaluated with stage-1 evidence is `MORE_EVIDENCE_REQUIRED` because Processor B capacity evidence is stale.
3. The same bounded candidate evaluated after stage-2 evidence is `WAITING_HUMAN`: the technical gates pass, but this C2 action requires a `payments_operations_lead` approval.
4. Approval is created during the live run and bound to the exact candidate, case, evidence, starting state, decision, authority, and expiry. No valid approval is preloaded.
5. The committed action routes exactly 87 incident failures to Processor B. Those 87 recover successfully; the remaining 18 incident failures stay on Processor A and remain failed.
6. Verification reads actual state and requires a success rate of at least 95%, zero unauthorized Processor B routes, and zero policy violations.
7. If the effect may have committed but state cannot be read, the expected outcome is `OUTCOME_UNKNOWN / RECONCILIATION_REQUIRED / NO_AUTOMATIC_RETRY`.

The 500-record cohort totals $12.5M of modeled weighted payment flow. The separate $8.33M statement is a duration sensitivity: approximately that amount of modeled payment flow returns to normal processing sooner when modeled recovery time falls from 30 to 10 minutes. It is not revenue, profit, guaranteed savings, or guaranteed avoided loss.
