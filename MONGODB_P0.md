# MongoDB P0 — Required Integration

> Day-of Mongo rule. The product README restates this as current truth: Mongo records decisions; it does not make them. Event file map: [docs/HACKATHON.md](docs/HACKATHON.md).

## One sentence

> **MongoDB is the audit substrate, not the authority.**

MongoDB is required by the organizer. Use it for something Resolve genuinely needs: durable case/journal/approval/verification evidence and replay.

## Architectural boundary

`resolve/contract.py` must be pure decision logic.

It must **not**:
- import `pymongo`;
- query MongoDB;
- use DB availability as a permission signal;
- derive permission from persistence success.

Required invariant:

`same validated DecisionInput -> same ContractResult`

whether MongoDB is online or offline.

`resolve/mongo_store.py` owns persistence.

## Minimal collections

P0 can use these collections:

### `cases`
Stores normalized case snapshots and fingerprints.

Suggested fields:
- `case_id`
- `case_fingerprint`
- `case`
- `created_at`

### `journal_events`
Canonical append-only event projection.

Suggested fields:
- `event_id`
- `case_id`
- `run_id`
- `sequence`
- `timestamp`
- `event_type`
- `payload`
- `payload_hash`
- `prev_hash`
- `event_hash_or_mac`

Indexes:
- unique `event_id`
- unique `(run_id, sequence)`

### `candidates`
- `candidate_id`
- `run_id`
- `candidate`
- `candidate_fingerprint`
- `evidence_ids`
- `created_at`

### `approvals`
- `approval_id`
- `run_id`
- `candidate_fingerprint`
- `case_fingerprint`
- `approver`
- `expires_at`
- `nonce`
- `used`
- `integrity`
- `status`

### `verification_events`
- `verification_id`
- `run_id`
- `candidate_fingerprint`
- `observed_state`
- `success`
- `timestamp`

Optional:
### `runtime_receipts`
Exact model/runtime/OpenShell/Mongo versions and proof receipts.

## Write path

Preferred:

```text
core computes event + integrity
        ↓
MongoStore persists exact event
        ↓
UI/API reads projection
```

Do not make MongoDB a second state machine.

## Failure semantics

If MongoDB is unavailable:
- contract evaluation must still be deterministic;
- the system must clearly report persistence failure;
- do not claim a durable/auditable successful commit without its required journal receipt;
- recover persistence rather than weakening the contract.

For demo P0, MongoDB should be green before the complete end-to-end run because it is required stack.

## Minimum API

`mongo_store.py` should stay tiny:

```text
connect()
health()
ensure_indexes()
insert_case_snapshot(...)
append_journal_event(...)
insert_candidate(...)
insert_approval(...)
insert_verification(...)
list_journal(run_id)
export_run(run_id)
```

Avoid a generic repository framework.

## Minimum tests

- Mongo health succeeds locally.
- Insert/read one case snapshot.
- Append/read journal in sequence order.
- Duplicate `(run_id, sequence)` is rejected.
- `contract.py` gives identical verdict with Mongo on/off.
- Candidate and approval fingerprints round-trip unchanged.
- Approval mutation creates a new candidate fingerprint and old approval does not become valid.
- Verification record can be replayed/exported.
- Mongo export for one successful run is copied into Gate-E survival evidence.

## Demo proof

Show a small status line only if true:

`MongoDB LOCAL | journal events: <n> | replay: ready`

Judge explanation:

> “The model does the reasoning. Python owns permission. MongoDB gives us the durable audit and replay trail.”
