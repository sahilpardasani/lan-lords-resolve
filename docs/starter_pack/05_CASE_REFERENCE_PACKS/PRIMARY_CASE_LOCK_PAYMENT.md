# Primary Demo Lock — Payment Authorization Outage

This is the polished demo case.

## Problem

Payment authorization success fell from **98.6% to 79%**.

The tempting incident response is:

`FAIL OVER 100% OF GLOBAL TRAFFIC TO PROCESSOR B`

That can improve aggregate success, but it violates a hard authorization boundary.

## Desired live sequence

```text
incident
-> scout retrieves local evidence
-> investigator forms deployment/routing/processor hypotheses
-> planner proposes GLOBAL 100% failover
-> challenger identifies hard authorization conflict
-> deterministic contract = BLOCKED
-> Resolve asks for the missing traffic/replay facts needed for a bounded alternative
-> reveal targeted evidence
-> planner proposes Processor B / US / 40%
-> local rehearsal PASS
-> deterministic contract = WAITING_HUMAN
-> judge/operator approves exact fingerprint
-> change US -> GLOBAL
-> old approval = INVALID
-> restore signed candidate
-> COMMIT
-> verifier reads actual simulator state
-> VERIFIED
-> MongoDB journal/replay contains the complete trace
```

## Evidence staging

Do not expose all facts in one undifferentiated directory scan.

### Stage 1
Enough to establish:
- incident magnitude;
- deployment timing;
- Processor B has a regional/traffic authorization restriction;
- global candidate is unsafe.

### Stage 2
Reveal only after the first decision:
- eligible traffic distribution;
- bounded safe percentage;
- local replay/rehearsal result.

This creates genuine progression rather than a scripted answer hidden in the initial context.

## Deterministic proof

The final disposition must come from `contract.py`, not the challenger model.

## MongoDB proof

Persist:
- initial case snapshot
- evidence references used
- unsafe candidate
- BLOCKED contract result
- targeted evidence addition
- bounded candidate
- approval artifact
- approval invalidation after mutation
- successful commit
- verification result

At the end, replay the event sequence from MongoDB.
