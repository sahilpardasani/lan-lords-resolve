# Payment demo source reconciliation

The source files are evidence and reference inputs, not canonical runtime truth. All operational rules, transaction outcomes, and incident telemetry below remain explicitly synthetic.

| Source file | What it supported | What was inconsistent | Canonical decision | Derived files | Validation result |
|---|---|---|---|---|---|
| `Resolve_Payments_Real_Business_Data.xlsx` (`a6f5af4f…3db52f`) | Public-scale anchors, the 500-record sample size, 98.6% baseline, 79.0% incident, 96.4% post-action, and the $8.33M duration sensitivity | The headline rates reconcile, but routing does not explain recovery: only 36 rows route to B, 28 of those were already incident successes, and 81 of the 87 incident-failure-to-post-success transitions occur on A. The workbook also describes a 20% cap as a percentage of eligible traffic. | Retain the headline rates and one 500-identity cohort. Route exactly the 87 affected incident failures to B, leave the other 18 failures on A, and define the cap as 20% of total traffic subject to per-transaction eligibility. | `data/canonical/*`, `data/mongodb/import/payment_events.ndjson` | PASS through `scripts/validate_payment_fixture.py` |
| `resolve_mongodb_demo.ndjson` (`d29a06f0…60a35c`) | Useful MongoDB document shapes, phase rates, typed policy concepts, candidate/approval examples, and a 3,008-document audit reference | It uses separate 1,000-event baseline/incident/recovery populations, a 20% candidate, and preloaded approval/execution/verification state. Ordinal reconciliation finds 174 incident failures later marked successful: 153 recover on A and only 21 on B; 57 of the 79 B-routed recovery rows were already incident successes. | Do not use it as the live run database. Import only the canonical case, evidence, and one 500-record transaction cohort. Generate candidate, approval, commit, verification, journal, and replay state live. | `data/mongodb/import/*`, `data/mongodb/reference_expected_trace/expected_trace.ndjson` | PASS; reference trace is marked `reference_only` |
| `Hackathon 082226.docx` (`2619562c…ed7420`) | Pitch framing, public-scale context, financial sensitivity, local-inference story, and the synthetic-data disclosure | It uses older language such as “20% of eligible traffic,” says Resolve constructs the largest permitted alternative, and presents commercial projections that are hypotheses rather than runtime facts. The rendered document also contains heading typos and leaves the Mastercard calculation result lines visually empty. | Use only as story source material. Describe Resolve as execution assurance, make the Planner the proposer, make typed policy the deterministic authority, state 17.4% of total traffic under a 20% total cap, and classify $8.33M as payment throughput returning sooner. | `README.md`, `cases/primary/EXPECTED.md` | Reviewed as six rendered pages; not imported into runtime state |
| `resolve_enterprise_payment_live_demo.html` | Intended visual and interaction reference only | The named file was not provided and was not found in the user directories searched. Substituting a different HTML file would hide source provenance. | No substitute was silently adopted. The existing repository UI remains a legacy mock projection until the backend-driven GB10 integration is completed. | None | Source gap; not required for canonical data validation |

## Independently recomputed source results

### Workbook

- Rows: 500
- Baseline: 493 successes (98.6%)
- Incident: 395 successes (79.0%)
- Post-action: 482 successes (96.4%)
- Eligible for B: 162
- Routed to B: 36 (7.2% of total)
- Incident failure → post success: 87 total; 6 on B and 81 on A
- Weighted cohort: 500 × $25,000 = $12.5M

### Original Mongo fixture

- Documents: 3,008, including 3,000 payment events
- Baseline: 1,000 / 986 successes
- Incident: 1,000 / 790 successes
- Recovery: 1,000 / 964 successes
- Recovery rows on B: 79
- Preloaded live-state-shaped records: one approval, one approval validation, one execution, and one verification

## Frozen canonical decisions

1. The workbook headline rates are retained because they are internally consistent.
2. Original workbook routing is not retained because it does not causally account for the 87 recovered outcomes.
3. The old “20% of eligible traffic” wording is retired.
4. Processor B may receive at most 20% of total traffic, and every B-routed transaction must separately satisfy country, network, amount, incident-failure, affected-cohort, and approval conditions.
5. The 1,000-event-per-phase Mongo populations are replaced by one canonical 500-identity cohort.
6. The bounded candidate is 17.4% of total traffic, not 20% and not 40%.
7. Valid live approvals, executions, verifications, journal chains, and replay records are never preloaded.
8. The 87 transaction recoveries and the $8.33M duration sensitivity are separate claims. The latter means modeled payment flow returning to normal processing sooner, not revenue, profit, guaranteed savings, or guaranteed avoided loss.

## Source naming note

The handoff referred to `(1)` filename variants. The supplied files did not use those suffixes, so the repository preserves the exact supplied filenames and records their SHA-256 hashes in `data/canonical/dataset_manifest.json`.
