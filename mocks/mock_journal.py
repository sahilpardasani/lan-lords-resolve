"""
mocks/mock_journal.py  --  THROWAWAY stand-in for Coder 2's resolve/journal.py

Local append-only NDJSON journal so Resolve survives MongoDB being down.
Delete this when the real resolve/journal.py lands. It lives in mocks/ so it
never collides with Coder 2's file.

Responsibilities (the journal side of the handshake):
  - append events to runtime/journal.ndjson (survives Mongo outage)
  - track which events are unsynced
  - verify local hash-chain integrity
  - on recovery, hand unsynced events to mongo_store.sync_run()
"""

import os
import json
import hashlib

JOURNAL_PATH = os.environ.get("RESOLVE_JOURNAL", "runtime/journal.ndjson")


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def _canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def reset():
    os.makedirs(os.path.dirname(JOURNAL_PATH) or ".", exist_ok=True)
    open(JOURNAL_PATH, "w").close()


def _read_all():
    if not os.path.exists(JOURNAL_PATH):
        return []
    with open(JOURNAL_PATH) as f:
        return [json.loads(line) for line in f if line.strip()]


def append(event: dict) -> dict:
    """Append one event locally, chaining prev_hash. Always succeeds even if
    MongoDB is down -- that's the whole point of the black box."""
    existing = _read_all()
    prev_hash = existing[-1]["event_hash"] if existing else "GENESIS"
    rec = dict(event)
    rec["previous_event_hash"] = prev_hash
    rec["event_hash"] = _sha(_canon({k: v for k, v in rec.items()
                                     if k not in ("event_hash", "synced")}))
    rec["synced"] = False
    os.makedirs(os.path.dirname(JOURNAL_PATH) or ".", exist_ok=True)
    with open(JOURNAL_PATH, "a") as f:
        f.write(json.dumps(rec, default=str) + "\n")
    return rec


def unsynced():
    return [e for e in _read_all() if not e.get("synced")]


def verify_integrity() -> dict:
    """Recompute the local chain; detect tamper/reorder/deletion."""
    events = _read_all()
    prev = "GENESIS"
    for e in events:
        recomputed = _sha(_canon({k: v for k, v in e.items()
                                  if k not in ("event_hash", "synced")}))
        if e.get("previous_event_hash") != prev:
            return {"intact": False, "broken_at": e.get("sequence"),
                    "reason": "prev_hash mismatch"}
        if e.get("event_hash") != recomputed:
            return {"intact": False, "broken_at": e.get("sequence"),
                    "reason": "event_hash mismatch"}
        prev = e["event_hash"]
    return {"intact": True, "events": len(events)}


def mark_synced(sequences):
    events = _read_all()
    s = set(sequences)
    for e in events:
        if e.get("sequence") in s:
            e["synced"] = True
    with open(JOURNAL_PATH, "w") as f:
        for e in events:
            f.write(json.dumps(e, default=str) + "\n")
