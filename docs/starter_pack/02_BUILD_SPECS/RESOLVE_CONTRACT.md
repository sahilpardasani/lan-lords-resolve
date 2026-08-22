# Resolve Contract — Frozen P0 Reference

## Eight gates
| Gate | Question |
|---|---|
| INTENT | Are we optimizing the authorized objective? |
| EVIDENCE | Is material evidence sufficient and properly referenced? |
| CONSTRAINTS | Does the candidate violate a hard rule? |
| CONSEQUENCE | What is the downside if wrong? |
| REVERSIBILITY | Can it be undone when required? |
| REHEARSAL | Did required bounded test/simulation pass? |
| AUTHORITY | Is the correct authority bound to this exact action? |
| VERIFICATION | Can actual post-action success/failure be observed? |

Machine gate values: `PASS | FAIL | UNKNOWN`.

## Deterministic disposition
```python
if any(required_hard_gate == "FAIL"):
    disposition = "BLOCKED"
elif any(required_material_gate == "UNKNOWN"):
    disposition = "MORE_EVIDENCE_REQUIRED"
elif human_approval_required and all_required_gates_pass:
    disposition = "WAITING_HUMAN"
elif all_required_gates_pass:
    disposition = "ADMISSIBLE"
else:
    disposition = "BLOCKED"  # fail closed
```

The exact implementation is built day-of; this is the behavioral contract.

## Required candidate/contract fields
At minimum:
- `candidate_id`;
- normalized action + parameters;
- objective/protected outcomes;
- material evidence IDs;
- hard constraints checked;
- consequence class;
- reversibility contract;
- rehearsal requirement/result;
- authority requirement;
- verification plan;
- candidate/evidence/state fingerprint;
- resulting gate vector and disposition.

## Important boundary
The model may propose semantic facts in structured form. Do not treat `"intent":"PASS"` or any other model-produced gate token as deterministic authorization. The runtime validates structured facts/evidence and computes permission consequences.

## Approval binding
Approval must bind exact action, parameters, case/evidence/state fingerprint, approver/authority, expiration, one-time use, and consequence envelope. Material mutation invalidates it.
