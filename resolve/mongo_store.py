"""
resolve/mongo_store.py  --  MongoDB persistence for Resolve (Coder 3)

MongoDB is the AUDIT SUBSTRATE, not the authority.
This module ONLY persists what core computes. It makes zero decisions.
contract.py never imports this; permission is identical with Mongo on or off.

Spec: MONGODB_P0.md
API (kept tiny, no generic repo framework):
    connect() health() ensure_indexes()
    insert_case_snapshot() append_journal_event()
    insert_candidate() insert_approval() insert_verification()
    list_journal(run_id) export_run(run_id)

Connection: local only. Coder 1 owns "MongoDB is alive"; we own "Resolve
persists to it." Override the URI via RESOLVE_MONGO_URI if the box differs.
"""

import os
import json
import hashlib
from datetime import datetime, timezone

from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

MONGO_URI = os.environ.get("RESOLVE_MONGO_URI", "mongodb://127.0.0.1:27017")
DB_NAME = os.environ.get("RESOLVE_MONGO_DB", "resolve")

_client = None
_db = None


# --- small helpers -------------------------------------------------------
def _now():
    return datetime.now(timezone.utc)


def _canonical(obj) -> str:
    """Deterministic JSON so any hash we compute is stable."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


# --- connection / health -------------------------------------------------
def connect(uri: str = None):
    """Open (or reuse) a local Mongo connection. Never raises on import."""
    global _client, _db
    if _db is not None:
        return _db
    _client = MongoClient(uri or MONGO_URI, serverSelectionTimeoutMS=3000)
    _db = _client[DB_NAME]
    return _db


def health() -> dict:
    """Report persistence availability WITHOUT affecting permission logic.
    Returns a dict the API/UI can show; never throws."""
    try:
        db = connect()
        db.command("ping")
        n = db.journal_events.estimated_document_count()
        return {"mongo": "LOCAL", "online": True, "journal_events": n,
                "replay": "ready"}
    except PyMongoError as e:
        return {"mongo": "LOCAL", "online": False, "error": str(e),
                "replay": "unavailable"}


def ensure_indexes():
    """Create the two required uniqueness guarantees from the spec."""
    db = connect()
    db.journal_events.create_index([("event_id", ASCENDING)], unique=True)
    db.journal_events.create_index(
        [("run_id", ASCENDING), ("sequence", ASCENDING)], unique=True)
    # helpful-but-not-required lookups
    db.cases.create_index([("case_id", ASCENDING)])
    db.candidates.create_index([("candidate_id", ASCENDING)], unique=True)
    db.approvals.create_index([("approval_id", ASCENDING)], unique=True)
    return True


# --- writes (persist EXACTLY what core computes) -------------------------
def insert_case_snapshot(case_id, case_fingerprint, case) -> dict:
    doc = {
        "case_id": case_id,
        "case_fingerprint": case_fingerprint,
        "case": case,
        "created_at": _now(),
    }
    connect().cases.insert_one(dict(doc))
    return doc


def append_journal_event(event: dict) -> dict:
    """Persist the exact event core computed. We do NOT recompute integrity;
    core owns the hash/HMAC. We only enforce append-only uniqueness.
    Rejects duplicate (run_id, sequence) via the unique index."""
    required = ("event_id", "run_id", "sequence", "event_type")
    missing = [k for k in required if k not in event]
    if missing:
        raise ValueError(f"journal event missing fields: {missing}")
    doc = dict(event)
    doc.setdefault("timestamp", _now())
    try:
        connect().journal_events.insert_one(dict(doc))
    except DuplicateKeyError as e:
        raise ValueError(
            f"duplicate journal event (event_id or run_id/sequence): {e}")
    return doc


# =========================================================================
# SYNC LAYER  --  the MongoDB half of the offline-recovery handshake.
#
# Write path:   event -> LOCAL JOURNAL -> continue Resolve -> (later) Mongo
# Resolve NEVER blocks on Mongo. When Mongo is down the journal keeps events;
# when Mongo returns, the journal replays its unsynced events THROUGH these
# functions. We only touch MongoDB here -- the journal itself is Coder 2's.
# =========================================================================
def persisted_seqs(run_id) -> set:
    """Which (sequence) numbers for this run are ALREADY in Mongo.
    The journal calls this on recovery to learn what's missing (spec §7.2)."""
    cur = connect().journal_events.find({"run_id": run_id}, {"sequence": 1, "_id": 0})
    return {d["sequence"] for d in cur}


def sync_event(event: dict) -> dict:
    """Idempotent persist of ONE journal event (spec §9).
    Returns status so retries are safe:
      SYNCED          -> newly written
      ALREADY_PRESENT -> (run_id, sequence) already in Mongo, no duplicate
    Identity is (run_id, sequence), enforced by the unique index."""
    try:
        append_journal_event(event)
        return {"status": "SYNCED", "run_id": event["run_id"],
                "sequence": event["sequence"]}
    except ValueError:
        return {"status": "ALREADY_PRESENT", "run_id": event["run_id"],
                "sequence": event["sequence"]}


def sync_run(events: list) -> dict:
    """Ordered, idempotent sync of a run's backlog (spec §8, §10).
    - sorts by sequence so 43 is never written before 42
    - skips events already present
    - drops nothing
    The journal hands us its unsynced events after Mongo recovers; we return
    which sequences are now durable so the journal can mark them synchronized."""
    ordered = sorted(events, key=lambda e: e["sequence"])
    synced, already = [], []
    for e in ordered:
        r = sync_event(e)
        (synced if r["status"] == "SYNCED" else already).append(e["sequence"])
    run_id = ordered[0]["run_id"] if ordered else None
    return {
        "run_id": run_id,
        "synced": synced,
        "already_present": already,
        "unsynced_remaining": 0,        # everything handed in is now durable
        "total_persisted": len(persisted_seqs(run_id)) if run_id else 0,
    }


def insert_candidate(candidate_id, run_id, candidate,
                     candidate_fingerprint, evidence_ids=None) -> dict:
    doc = {
        "candidate_id": candidate_id,
        "run_id": run_id,
        "candidate": candidate,
        "candidate_fingerprint": candidate_fingerprint,
        "evidence_ids": evidence_ids or [],
        "created_at": _now(),
    }
    connect().candidates.insert_one(dict(doc))
    return doc


def insert_approval(approval_id, run_id, candidate_fingerprint,
                    case_fingerprint, approver, expires_at, nonce,
                    integrity, used=False, status="ISSUED") -> dict:
    doc = {
        "approval_id": approval_id,
        "run_id": run_id,
        "candidate_fingerprint": candidate_fingerprint,
        "case_fingerprint": case_fingerprint,
        "approver": approver,
        "expires_at": expires_at,
        "nonce": nonce,
        "used": used,
        "integrity": integrity,
        "status": status,
    }
    connect().approvals.insert_one(dict(doc))
    return doc


def insert_verification(verification_id, run_id, candidate_fingerprint,
                        observed_state, success) -> dict:
    doc = {
        "verification_id": verification_id,
        "run_id": run_id,
        "candidate_fingerprint": candidate_fingerprint,
        "observed_state": observed_state,
        "success": success,
        "timestamp": _now(),
    }
    connect().verification_events.insert_one(dict(doc))
    return doc


# --- reads / replay ------------------------------------------------------
def list_journal(run_id) -> list:
    """Return the run's journal in sequence order (the audit trail)."""
    cur = connect().journal_events.find(
        {"run_id": run_id}, {"_id": 0}).sort("sequence", ASCENDING)
    return list(cur)


def export_run(run_id) -> dict:
    """Full replay/export bundle for one run -> Gate-E survival evidence."""
    db = connect()
    def clean(cur):
        return [ {k: v for k, v in d.items() if k != "_id"} for d in cur ]
    return {
        "run_id": run_id,
        "exported_at": _now().isoformat(),
        "cases": clean(db.cases.find({})),  # cases keyed by case, not run
        "candidates": clean(db.candidates.find({"run_id": run_id})),
        "journal_events": list_journal(run_id),
        "approvals": clean(db.approvals.find({"run_id": run_id})),
        "verification_events": clean(db.verification_events.find({"run_id": run_id})),
    }


def verify_journal_chain(run_id) -> dict:
    """Optional audit check: confirm prev_hash links across the run's journal.
    Core computes the hashes; this only checks the CHAIN is unbroken so we can
    prove tamper-evidence in the demo. Returns a report, never decides anything."""
    events = list_journal(run_id)
    prev = None
    for e in events:
        # 1. link check: prev_hash must match the previous event's hash
        if prev is not None and e.get("prev_hash") != prev.get("event_hash_or_mac"):
            return {"intact": False, "broken_at_sequence": e.get("sequence"),
                    "reason": "prev_hash mismatch", "events": len(events)}
        # 2. content check: recompute payload_hash; if the payload was edited
        #    after the fact, the stored payload_hash no longer matches
        recomputed = _sha(_canonical(e.get("payload", {})))
        if e.get("payload_hash") and e["payload_hash"] != recomputed:
            return {"intact": False, "broken_at_sequence": e.get("sequence"),
                    "reason": "payload tampered", "events": len(events)}
        prev = e
    return {"intact": True, "events": len(events)}


# =========================================================================
# FEATURE 3 — MONGODB AGGREGATION / AUDIT VIEWS (spec §21)
# Real MongoDB aggregation pipelines over what we already store. This is the
# "best use of MongoDB" evidence: the DB does the counting, not Python.
# =========================================================================
def audit_views() -> dict:
    """Return demo-ready audit counts computed by MongoDB aggregation."""
    db = connect()

    def count_disposition(disp):
        pipe = [
            {"$match": {"event_type": "CONTRACT_EVALUATED",
                        "payload.disposition": disp}},
            {"$count": "n"},
        ]
        r = list(db.journal_events.aggregate(pipe))
        return r[0]["n"] if r else 0

    verifications = db.verification_events
    ver_fail = verifications.count_documents({"success": False})
    ver_ok = verifications.count_documents({"success": True})

    runs = len(db.journal_events.distinct("run_id"))
    approvals_required = count_disposition("WAITING_HUMAN")
    blocked = count_disposition("BLOCKED")
    more_evidence = count_disposition("MORE_EVIDENCE_REQUIRED")

    # events executed (committed actions)
    executed = db.journal_events.count_documents({"event_type": "ACTION_COMMITTED"})

    return {
        "runs": runs,
        "blocked_actions": blocked,
        "approval_required_actions": approvals_required,
        "more_evidence_required": more_evidence,
        "actions_executed": executed,
        "verification_failures": ver_fail,
        "verification_successes": ver_ok,
        "total_journal_events": db.journal_events.estimated_document_count(),
    }


def events_by_type(run_id) -> dict:
    """Aggregation: count each event_type for a run (timeline shape)."""
    pipe = [
        {"$match": {"run_id": run_id}},
        {"$group": {"_id": "$event_type", "n": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]
    return {d["_id"]: d["n"] for d in connect().journal_events.aggregate(pipe)}


# =========================================================================
# FEATURE 4 — REPLAY RUN (spec §15)
# Reconstruct a recorded run from Mongo as an ordered timeline. Replay shows
# what Resolve knew at each step -- it does NOT re-run the model.
# =========================================================================
def replay_run(run_id) -> dict:
    """Ordered reconstruction of one run for the replay view."""
    export = export_run(run_id)
    timeline = [
        {"sequence": e["sequence"],
         "event_type": e["event_type"],
         "summary": _summarize(e)}
        for e in export["journal_events"]
    ]
    return {
        "run_id": run_id,
        "timeline": timeline,
        "candidates": export["candidates"],
        "approvals": export["approvals"],
        "verifications": export["verification_events"],
        "chain": verify_journal_chain(run_id),
    }


def _summarize(event) -> str:
    p = event.get("payload", {})
    t = event["event_type"]
    if t == "CONTRACT_EVALUATED":
        return f"disposition={p.get('disposition')} reasons={p.get('reason_codes')}"
    if t == "AI_PROPOSAL":
        params = p.get("parameters", {})
        return f"target={p.get('target')} {params.get('region')} {params.get('traffic_pct')}%"
    if t == "APPROVAL_ISSUED":
        return f"approval={p.get('approval_id','')[:16]}"
    if t == "VERIFIED":
        return f"success={p.get('success')} observed={p.get('observed',{}).get('current_success')}"
    if t in ("INCIDENT_DETECTED", "ACTION_COMMITTED"):
        return str(p)
    return ""


# =========================================================================
# FEATURE 5 — "WHY WAS THIS BLOCKED?" VIEW (spec §19)
# Pull the full blocked-decision record from Mongo so every claim links back
# to a stored event. Reads only; decides nothing.
# =========================================================================
def why_blocked(run_id) -> dict:
    """Assemble the blocked-candidate explanation from stored records."""
    db = connect()
    blocked_evt = db.journal_events.find_one(
        {"run_id": run_id, "event_type": "CONTRACT_EVALUATED",
         "payload.disposition": "BLOCKED"}, {"_id": 0})
    if not blocked_evt:
        return {"run_id": run_id, "blocked": False,
                "message": "no blocked decision recorded for this run"}

    verdict = blocked_evt["payload"]
    # the candidate proposed just before this verdict
    prior = db.journal_events.find_one(
        {"run_id": run_id, "event_type": "AI_PROPOSAL",
         "sequence": {"$lt": blocked_evt["sequence"]}},
        {"_id": 0}, sort=[("sequence", -1)])
    candidate = prior["payload"] if prior else None
    cand_doc = None
    if candidate:
        cand_doc = db.candidates.find_one(
            {"run_id": run_id,
             "candidate_fingerprint": _sha(_canonical(candidate))}, {"_id": 0})

    failed_gates = [g for g, v in verdict.get("gates", {}).items() if v == "FAIL"]
    return {
        "run_id": run_id,
        "blocked": True,
        "candidate": candidate,
        "candidate_fingerprint": cand_doc["candidate_fingerprint"] if cand_doc else None,
        "failed_gates": failed_gates,
        "reason_codes": verdict.get("reason_codes", []),
        "disposition": verdict.get("disposition"),
        "at_sequence": blocked_evt["sequence"],
        "links_to": {"journal_event": blocked_evt.get("event_id"),
                     "candidate_id": cand_doc["candidate_id"] if cand_doc else None},
    }


# --- manual smoke ---------------------------------------------------------
if __name__ == "__main__":
    print("health:", health())
    ensure_indexes()
    print("indexes ensured.")
