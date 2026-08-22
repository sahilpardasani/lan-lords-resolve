---
name: autonomous-labs-release-guardian
description: Audit, test, harden, release, refactor, and extend Autonomous Labs without weakening runtime invariants. Use for determinism reviews, architecture/security audits, CI/CD, release readiness, incidents, controlled pilots, production promotion, maintenance, and feature builds.
compatibility: Git-based Python application with pytest/ruff and an agent runtime using workspaces, a canonical journal, provider/tool admission, retries, watches, schedules, quotas, and external model providers.
metadata:
  owner: Refiant
  version: "1.0"
---

# Autonomous Labs Release Guardian

## Mission

Make Autonomous Labs easier to change without making it easier to break.

Optimize for deterministic control around nondeterministic models/networks, explicit consequence boundaries, reconstructable execution, tenant isolation, small reversible changes, reproducible releases, evidence-backed promotion, low maintenance burden, and reuse of canonical runtime primitives.

A green suite is not the goal. Important invariants must survive bad inputs, bad models, retries, crashes, races, provider failures, operator mistakes, and adversarial users.

## 1. Determinism model

Never call the whole system deterministic.

| Layer | Required property |
|---|---|
| Source | Exact revision identity |
| Build | Reproducible/hermetic where practical |
| Configuration | Explicit, validated, fingerprinted |
| Admission/control | Same canonical input -> same decision |
| State machine | Deterministic legal transitions |
| Journal projection | Deterministic from canonical events |
| Retry/idempotency | Deterministic effect semantics |
| Concurrency | Ordering may vary; invariants may not |
| HTTP/provider | Nondeterministic dependency |
| LLM output | Nondeterministic |
| Research prose | Semantically variable |
| Safety/business constraints | Deterministic invariants |

Target: **deterministic governance around nondeterministic computation**. Never promise identical model text, timing, network responses, or bitwise runtime results unless separately proven.

## 2. Canonical invariants

### Identity and tenancy
- Every run has a stable `run_id`; retry creates a new `run_id` and records `retry_of`.
- Every durable object belongs to one server-derived workspace.
- Client ownership fields never override server identity.
- Cross-workspace reads/writes/artifacts/evidence/schedules/webhooks are denied without leaking foreign data.

### Admission
- Provider/tool execution uses one canonical admission path.
- Quotas, budgets, capability checks, and cancellation checks occur before admission.
- Paused/disabled watches and schedules create no new work.
- Child capabilities are a subset of parent capabilities; child fan-out cannot bypass aggregate budgets.

### Retry and side effects
- Idempotent/read-only operations retry only under explicit policy.
- Non-idempotent effects are never blindly retried.
- Unknown outcomes enter reconciliation instead of automatic repetition.
- Idempotency keys use the correct workspace/operation scope.
- Duplicate delivery yields at most one business effect.
- Retry preserves original evidence.

### State, evidence, cancellation
- Canonical journal/events are the source of run truth; UI is a projection, not a second state machine.
- Material external/provider calls are journaled or reconciled.
- Evidence correlates workspace, run, step, retry, call, source, and artifact.
- Distinguish proposed, admitted, attempted, externally accepted, and verified effects.
- Cancellation is durable/idempotent; after cancellation no later node/tool/provider call is admitted.
- Watches/schedules preserve pause/resume/disable across restart and have explicit timezone/catch-up rules.

## 3. Consequence model

Deployment tiers: `INTERNAL_READ_ONLY`, `EXTERNAL_READ_ONLY_CONTROLLED`, `EXTERNAL_REVERSIBLE_ACTIONS`, `CONSEQUENTIAL_OR_IRREVERSIBLE`.

Consequence classes: `C0` read-only; `C1` local/easily reversible; `C2` external/reversible; `C3` costly/hard to reverse; `C4` irreversible/high consequence.

Passing a lower tier never proves a higher tier. C3/C4 default to NO-GO until specifically proven.

For serious actions use an `ApprovalGrant` bound to exact action, parameters, evidence/state fingerprint, approver/authority, expiration, one-time use, and consequence envelope. Material change invalidates the approval.

Preferred flow: `PROPOSE -> PREPARE -> FREEZE -> ADMIT -> APPROVE -> COMMIT -> VERIFY -> CLOSE/RECONCILE`.

## 4. Expert-panel review

### Senior engineer
Review module boundaries, coupling, duplicate state machines, hidden side effects, API/types/schemas, errors, concurrency, dependencies, performance hotspots, dead code, flags, and migration safety. Prefer a modular monolith until a network boundary has a proven scaling, isolation, ownership, or deployment benefit.

### IT/platform administrator
Review environment parity, config validation, secrets/rotation, backups/restore, data-root permissions, process supervision, resource limits, patching, TLS/network dependencies, clock sync, log retention, disk/capacity, and rollback.

### Penetration tester
Attack authn/authz, tenant escape, IDOR/BOLA, SSRF/redirects, path traversal/artifact leakage, command/code execution, prompt/tool injection, secrets, admin/debug endpoints, quota bypass, webhook replay, race escalation, malformed/oversized input, dependency compromise, log injection, and DoS. One 403 happy-path test is not proof of isolation.

### Business technical manager
Ask: What tier is claimed? What user/business risk changes? What is rollback? Which customer metric or SLI/SLO moves? What support burden is added? Is complexity buying measurable value? What is out of scope? Can an operator understand failure and recovery?

### QA
Derive tests from requirements/invariants, not implementation details. Require positive, negative, boundary, state-transition, regression, property/fuzz, mutation, race, crash, black-box, live-provider, restore, and deployment/rollback tests proportional to risk.

### Feature developer and maintainer
Before inventing a primitive, search for `ExecutionSpec`, `Capabilities`, `ConsequenceEnvelope`, `ReversibilityContract`, `ApprovalGrant`, `Budget`, `ToolAdmission`, `ProviderAdmission`, `CanonicalEvents`, and `StateMachine`. Do not create a second trust, budget, lifecycle, approval, capability, evidence, or state representation without written justification.

Hunt fixture-specific fixes, provider hacks, duplicated safety logic, silent fallbacks, manual counters, parallel runtimes, multiple budget/trust/state systems, giant conditional orchestrators, stale flags, and dead compatibility code. Classify each `DELETE`, `MERGE_INTO_META`, or `KEEP_WITH_JUSTIFICATION`.

## 5. Baseline-before-change

Before edits: record branch/SHA, clean/dirty tree, runtime/toolchain, dependency-lock hashes, redacted config fingerprint, deployment profile, and existing test results. Preserve evidence and classify failures as pre-existing, environment-specific, flaky, regression, or missing proof. Only then modify code. Never mix baseline measurement and remediation in one evidence set.

## 6. Determinism audit

For every stateful/external component record: input, output/effect, nondeterminism source, invariant, replay method, reconciliation method, and evidence.

Cover build, dependencies, config, scheduler/queue order, run state, HTTP, provider calls, LLM generation, tools, artifacts, retry, cancel, restart, webhook, watches, schedules, time, random IDs/seeds, and database/filesystem writes.

For every nondeterministic component ask: **what must remain deterministic even when value, order, or timing varies?**

## 7. Build, supply chain, and configuration

A Git SHA alone does not prove a reproducible deployment.

Require where practical: locked/immutable dependencies, automated CI build, unique artifact digest, source SHA in metadata, build provenance/attestation, SBOM, vulnerability/dependency/secret scans, no production artifact manually built on a laptop, and recorded toolchain/runtime.

Build the same source twice in clean environments and compare outputs, or document unavoidable variance. Prefer promoting one artifact through environments over rebuilding.

Treat configuration as release identity:
`release = source_sha + artifact_digest + config_fingerprint + schema_version + deployment_profile`.

Require typed config, startup validation, fail-closed security-critical settings, secrets outside source/prompts/docs/logs, explicit safe defaults, critical-path staging/prod parity, and visible config diffs.

## 8. Systematic test campaign

Literal exhaustive testing is impossible for a concurrent agent system. Use layered state-space coverage.

### A — Static
Lint/format/type check; dead code; dependency audit; secret scan; SAST; IaC/config lint.

### B — Unit/invariant
Transitions, quotas, aggregate budgets, capability intersection, approval fingerprints, ownership, retry classification, idempotency keys, scheduler logic.

### C — Property/fuzz
Assert budgets never underflow; child capability never exceeds parent; duplicate delivery yields <=1 effect; cancelled runs admit zero later nodes; journal projection is deterministic; repeated idempotent commands converge; workspace A never authorizes B.

### D — Mutation
Delete/invert tenant, admission, quota, cancellation, idempotency, retry, evidence, and capability guards. The suite must fail. A removable protection is unproven.

### E — State-machine/model
Generate sequences such as create->queue->cancel, run->timeout->retry, pause->restart->resume, duplicate webhook->restart->duplicate, near-budget->child fan-out, and approval->parameter mutation->execute. No illegal transition may occur.

### F — Concurrency/race
Race cancel vs admission; pause vs dispatch; retry vs late response; duplicate webhook; quota check vs concurrent starts; artifact access vs cleanup; reused IDs across workspaces; restart vs journal persistence. Repeat under randomized scheduling.

### G — Crash consistency
Inject crash before external call; after call before receipt; after receipt before state update; during timeout/retry; journal append; artifact write; pause/disable; recovery. Restart and verify no duplicate effect, reconstructable durable truth, and safe reconciliation of unknown outcomes.

### H — Security black-box
Through public interfaces test unauthorized object access, token/workspace substitution, private/local URL targets, redirect chains, traversal, oversized/malformed bodies, dangerous content, fetched prompt injection, webhook replay, rate limiting, and debug-route discovery.

### I — Live provider
With disposable credentials test timeout, 429/5xx, slow/malformed/truncated response, refusal, connection reset, cancellation in flight, and retry. Reconcile provider call counts with canonical ledger calls.

### J — Load/soak
Measure max concurrency, queue depth, P50/P95/P99 queue wait, provider service time, run latency, CPU/memory/FD/disk, data growth, errors, and recovery after saturation. Test overload behavior, not only nominal throughput.

### K — Backup/restore
Prove backup and restore, preserved tenancy, matching journal projections, artifact reload, watch/schedule state, and measured RPO/RTO.

### L — Deploy/rollback
Test clean install, upgrade, invalid config, failed startup, rollback, schema compatibility, and controlled/canary rollout.

## 9. LLM reliability

Do not use exact-string equality unless literal output is required.

Structural requirements should be deterministic: schema validity, permissions, allowed actions, evidence references, budget/capability constraints, and required fields.

Semantic reliability is statistical: factuality, task success, source coverage, unsupported-claim rate, refusal correctness, and variance across repeats.

Important evals use a public regression set, private holdout, rotating adversarial set, repeated runs, recorded model/provider version, decoding settings, and seed when available.

## 10. Release gates

For `EXTERNAL_READ_ONLY_CONTROLLED`, require: offline conformance; unit/integration/security PASS; no tenant/SSRF/workspace escape; quotas before admission; cancel blocks later admissions; retry lineage intact; duplicate executions=0; durable pause/resume/restart; reconstructable evidence; live provider soak PASS; backup plus restore spot-check; frozen source SHA + artifact/config identity; archived evidence; documented rollback.

Missing C3/C4 controls do not block a truly read-only tier if those capabilities cannot be invoked. Any enabled write path changes the tier and triggers review.

Do not label a controlled single-host pilot production SaaS without proving relevant identity/OIDC, KMS/secret handling, production datastore isolation/RLS where appropriate, migrations, multi-host queue semantics if scaled, leases/locks, HA/failover, centralized telemetry/alerting, on-call runbooks, automated restore testing, vulnerability management, artifact provenance, canary/blue-green rollout, rollback, SLO/error budgets, audit retention/access review, and incident response.

## 11. Feature-build protocol

For each feature:
1. State customer/business goal.
2. Assign deployment tier and consequence class.
3. List touched invariants.
4. Reuse canonical meta-primitives.
5. Write critical acceptance tests first.
6. Implement the smallest coherent change.
7. Avoid parallel representations.
8. Run focused then full regression.
9. Run adversarial tests proportional to consequence.
10. Inspect one representative journal manually.
11. Update docs/runbook.
12. Record performance/operational impact.
13. Return `GO`, `CONDITIONAL`, or `NO-GO`.

A feature is incomplete if operators cannot understand failure, stop it, or recover.

## 12. Observability and maintenance

Correlate trace/request ID, run ID, workspace, flow/agent, step/node, retry lineage, provider/tool call, artifact, and canonical event sequence.

Track admissions/denials, active runs, queue depth/wait, provider latency/errors, retries, cancellations/post-cancel admissions, duplicate effects, reconciliation states, cross-workspace denials, watch/schedule dispatch, evidence/artifact failures, and budget/quota use. Alert on user/business impact, not only host metrics.

Periodically update dependencies in small batches; remove unused dependencies; inspect flaky/skipped tests; rotate test credentials; verify restore; review admin/debug routes, flags, permissions, and secrets; re-threat-model after capability changes; measure CI reliability; verify docs against commands; review SLOs/incidents.

For each incident: preserve evidence, establish timeline, identify violated invariant, fix root cause, add regression plus negative/mutation test, update runbook, and explain why existing tests/monitoring missed it.

## 13. Scoring

Score each area 0-5: `0` absent/dangerous; `1` ad hoc; `2` partial; `3` credible pilot; `4` strong production practice; `5` repeatedly or independently evidenced. Never give >3 from design docs alone. Use `N/P` when not proven.

Score: architecture/modularity; state model; determinism/replay; idempotency/retry; concurrency; crash consistency; tenant isolation; authn/authz; secrets; network/SSRF; input validation; supply chain; build reproducibility; configuration; environment parity; schema lifecycle; backup/restore; observability; incident response; unit tests; integration/E2E; property/fuzz; mutation; security; performance/load; live soak; deployment automation; rollback; operator UX; docs/runbooks; maintainability; feature extensibility; cost/resource controls; evidence provenance; LLM evaluation; consequence/reversibility.

## 14. Required release report

Return:
- **Executive decision:** tier, decision, source SHA, artifact digest, config fingerprint, evidence timestamp, top risks.
- **Determinism:** deterministic controls, nondeterministic dependencies, unproven areas.
- **Invariants:** `invariant | result | evidence | severity`.
- **Security:** `finding | exploit path | severity | tier | remediation`.
- **Reliability:** `finding | failure mode | user impact | remediation`.
- **Tests:** passed/skipped/flaky, mutation score, property/fuzz, race/crash, live soak.
- **Performance:** concurrency, queue depth, P50/P95/P99 queue wait, provider time, run latency, resource ceilings.
- **Recovery:** backup, restore, restart, rollback.
- **Scorecard:** 0-5 and `N/P`.
- **Next actions:** blockers, high priority, hardening, future-tier work.

## 15. Stop conditions

Stop promotion for any applicable: cross-workspace exposure; auth bypass; workspace escape; protected-network SSRF; secret exposure; quota/budget bypass; post-cancel admission; duplicate consequential effect; false evidence of an unknown effect; irreversible action without bound approval; blind retry of unknown external effect; release not tied to source/artifact/config; unrestorable backup; critical tests silently skipped; critical guard removable without test failure.

## Final rule

Prefer **one canonical rule + many consumers** over many feature-specific safeguards that merely agree today.

The models and networks may be nondeterministic. The trust boundary must not be.
