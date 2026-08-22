# Resolve — P0 Test Plan

> **Archive.** Day-of test checklist. Current status: [docs/IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md). Event file map: [docs/HACKATHON.md](docs/HACKATHON.md).

## Model
- [ ] exact primary model revision/hash recorded;
- [ ] real GB10 GPU use;
- [ ] short correctness;
- [ ] structured output;
- [ ] long-context sentinel if required by final demo;
- [ ] actual local tool dispatch.

## OpenShell / local-first
- [ ] OpenShell is the selected mandatory sponsor component;
- [ ] public HTTP request BLOCKED;
- [ ] local inference PASS;
- [ ] local Resolve tool PASS;
- [ ] zero-egress receipt saved before UI says VERIFIED.

## MongoDB required stack
- [ ] local MongoDB health PASS;
- [ ] exact MongoDB version recorded;
- [ ] `mongo_store.py` connect/health works;
- [ ] indexes created;
- [ ] case snapshot insert/read;
- [ ] journal append/read in sequence;
- [ ] duplicate `(run_id, sequence)` rejected;
- [ ] candidate fingerprint round-trips;
- [ ] approval artifact round-trips;
- [ ] verification record stored;
- [ ] successful run exports/replays from MongoDB;
- [ ] `contract.py` has no Mongo dependency;
- [ ] same DecisionInput gives same verdict with persistence mocked/offline.

## Deterministic core
- [ ] case validation fails closed;
- [ ] case normalization/hash stable;
- [ ] eight gates produce `PASS|FAIL|UNKNOWN`;
- [ ] hard FAIL -> `BLOCKED`;
- [ ] material UNKNOWN -> `MORE_EVIDENCE_REQUIRED`;
- [ ] all required PASS + human -> `WAITING_HUMAN`;
- [ ] all required PASS + no human -> `ADMISSIBLE`;
- [ ] model cannot set final permission;
- [ ] material claims require valid evidence IDs;
- [ ] missing evidence cannot increase autonomy;
- [ ] deterministic business/rehearsal math matches fixture.

## Approval / effects
- [ ] approval binds exact action/parameters/case/evidence/authority/expiry/one-use;
- [ ] US -> GLOBAL mutation invalidates approval;
- [ ] expired approval invalid;
- [ ] reused approval invalid;
- [ ] blocked/waiting action cannot commit without valid grant;
- [ ] duplicate commit produces <=1 simulator effect;
- [ ] unknown commit outcome is reconciled, not blindly retried;
- [ ] commit followed by independent state read.

## Primary payment behavior
- [ ] baseline 98.6%, incident 79%;
- [ ] first attractive candidate is global failover;
- [ ] hard authorization rule blocks it;
- [ ] stale capacity evidence yields `MORE_EVIDENCE_REQUIRED` for the bounded candidate;
- [ ] current capacity, affected-cohort, traffic-distribution and rehearsal evidence support the 17.4% total-traffic candidate;
- [ ] rehearsal passes;
- [ ] human approval required;
- [ ] final simulator state verifies expected recovery;
- [ ] Mongo journal reconstructs complete run.

## Cross-domain / anti-hardcode
- [ ] loss-leader objective missing -> `MORE_EVIDENCE_REQUIRED`;
- [ ] loss-leader strategy conflict -> `BLOCKED`;
- [ ] authorized strategy changed -> INTENT PASS then remaining gates;
- [ ] materially different case loads without `contract.py` edits;
- [ ] irrelevant reorder/rephrase preserves disposition;
- [ ] material evidence change can change result.

## Demo survival
- [ ] one clean live run;
- [ ] one clean replay;
- [ ] screen recording saved;
- [ ] exact Git SHA/tag;
- [ ] verified Git bundle;
- [ ] Mongo journal export;
- [ ] runtime manifest;
- [ ] zero-egress receipt;
- [ ] pytest receipt;
- [ ] doctor receipt;
- [ ] exact `case.yaml`;
- [ ] video copied to WD and a physically carried device.
