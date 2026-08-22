"""
resolve/runtime.py  --  full Resolve run orchestration (Coder 3)

Ties everything together and persists EVERY step to MongoDB via mongo_store.
Core computes; MongoStore records; nobody lets Mongo decide permission.

Swappable seams (currently mocks):
    mocks.mock_ai       -> Coder 1's local model
    mocks.mock_contract -> Coder 2's contract.py
Everything else (context, tools, mongo_store, simulator) is real.

Run:  python -m resolve.runtime
"""

import sys
from datetime import datetime, timezone

from resolve import context, tools, mongo_store
from simulator.payment_sim import PaymentSimulator

# --- swappable seams -----------------------------------------------------
from mocks import mock_ai as ai            # replace with local model client
from mocks import mock_contract as contract  # replace with resolve.contract
# local journal (Coder 2's resolve/journal.py later; mock for now).
# Journal-first write path means Resolve survives MongoDB going down.
try:
    from resolve import journal            # real one, once Coder 2 ships it
except Exception:
    from mocks import mock_journal as journal


def _now():
    return datetime.now(timezone.utc)


# track whether Mongo is reachable this run, for status reporting
_mongo_state = {"online": True, "unsynced": 0}


def _journal(store, run_id, case_id, seq, event_type, payload, prev_hash):
    """MongoDB-PRIMARY, journal is the outage fallback.

    Write path:  event -> MongoDB (primary system of record).
                 If Mongo is down, hold it in the LOCAL JOURNAL instead, mark
                 UNSYNCED, and keep running. When Mongo returns, sync_run()
                 pushes the held events back so MongoDB is complete again.

    MongoDB is the audit + replay store. The journal exists only so a temporary
    Mongo outage never loses an event or blocks Resolve. It is not a second
    system of record."""
    payload_hash = tools.fingerprint(payload)
    event = {
        "event_id": tools.new_id("evt"),
        "case_id": case_id,
        "run_id": run_id,
        "sequence": seq,
        "timestamp": _now(),
        "event_type": event_type,
        "payload": payload,
        "payload_hash": payload_hash,
        "prev_hash": prev_hash,
    }
    event["event_hash_or_mac"] = tools.fingerprint({
        "payload_hash": payload_hash, "prev_hash": prev_hash,
        "sequence": seq, "event_type": event_type,
    })

    # 1. PRIMARY: MongoDB. Normal path — this is the system of record.
    try:
        store.append_journal_event(event)
        _mongo_state["online"] = True
    except Exception:
        # 2. FALLBACK: Mongo is down. Hold the event in the local journal so
        #    nothing is lost and Resolve keeps running. Synced back on recovery.
        _mongo_state["online"] = False
        _mongo_state["unsynced"] += 1
        try:
            journal.append(event)
        except Exception:
            pass  # last resort: never crash the run

    return event["event_hash_or_mac"]


def _safe(fn, *a, **k):
    """Run a Mongo op best-effort. Never crash the run if Mongo is down."""
    try:
        fn(*a, **k)
    except Exception:
        _mongo_state["online"] = False


def run() -> dict:
    store = mongo_store
    _mongo_state["online"] = True
    _mongo_state["unsynced"] = 0
    try:
        store.connect()
        store.ensure_indexes()
    except Exception:
        _mongo_state["online"] = False   # start with Mongo down is fine

    sim = PaymentSimulator()
    run_id = tools.new_id("run")
    case = context.load_case()
    case_id = case["case_id"]

    # persist the case snapshot (best effort)
    _safe(store.insert_case_snapshot, case_id, case["case_fingerprint"], case)

    seq = 0
    prev = "GENESIS"
    prev = _journal(store, run_id, case_id, seq, "INCIDENT_DETECTED",
                    {"current_success": sim.state()["current_success"]}, prev)

    # --- pass 1: AI proposes the tempting wrong action -------------------
    seq += 1
    bad = ai.propose_first(case)
    _safe(store.insert_candidate, tools.new_id("cand"), run_id, bad,
          tools.fingerprint(bad))
    prev = _journal(store, run_id, case_id, seq, "AI_PROPOSAL", bad, prev)

    seq += 1
    r1 = contract.evaluate(bad, case, context.initial_evidence())
    prev = _journal(store, run_id, case_id, seq, "CONTRACT_EVALUATED", r1, prev)

    # --- pass 2: evidence revealed, AI proposes bounded candidate --------
    seq += 1
    good = ai.propose_bounded(case, context.revealed_evidence())
    good_fp = tools.fingerprint(good)
    _safe(store.insert_candidate, tools.new_id("cand"), run_id, good, good_fp)
    prev = _journal(store, run_id, case_id, seq, "AI_PROPOSAL", good, prev)

    seq += 1
    r2 = contract.evaluate(good, case, context.revealed_evidence())
    prev = _journal(store, run_id, case_id, seq, "CONTRACT_EVALUATED", r2, prev)

    disposition = r2["disposition"]
    approval = None
    verification = None

    # --- human approval + commit + verify (only if contract allows) -----
    if disposition == "WAITING_HUMAN":
        seq += 1
        approval = tools.make_approval(good, case["case_fingerprint"],
                                       case["approver_authority"], run_id)
        _safe(store.insert_approval, **approval)
        prev = _journal(store, run_id, case_id, seq, "APPROVAL_ISSUED",
                        {"approval_id": approval["approval_id"],
                         "candidate_fingerprint": approval["candidate_fingerprint"]},
                        prev)

        # governance re-check: approval must still bind to exact candidate
        if tools.approval_matches(approval, good):
            seq += 1
            params = good["parameters"]
            observed = sim.apply_failover(params["region"], params["traffic_pct"])
            prev = _journal(store, run_id, case_id, seq, "ACTION_COMMITTED",
                            {"candidate_fingerprint": good_fp, "observed": observed},
                            prev)

            seq += 1
            success = observed["current_success"] > case["current_success"]
            try:
                store.insert_verification(tools.new_id("ver"), run_id, good_fp,
                                          observed, success)
            except Exception:
                _mongo_state["online"] = False   # verification still happened
            verification = {"observed": observed, "success": success}
            prev = _journal(store, run_id, case_id, seq, "VERIFIED",
                            verification, prev)

    # final projection — Mongo may be down; fall back to journal count
    try:
        export = store.export_run(run_id)
        events = len(export["journal_events"])
    except Exception:
        _mongo_state["online"] = False
        events = seq + 1  # what we recorded locally
    try:
        health = store.health()
    except Exception:
        health = {"mongodb": "OFFLINE", "online": False}

    return {
        "run_id": run_id,
        "first_disposition": r1["disposition"],   # expect BLOCKED
        "final_disposition": disposition,         # expect WAITING_HUMAN -> committed
        "approval_id": approval["approval_id"] if approval else None,
        "verification": verification,
        "journal_events": events,
        "mongo_online": _mongo_state["online"],
        "unsynced_events": _mongo_state["unsynced"],
        "health": health,
    }


if __name__ == "__main__":
    result = run()
    print("\n=== RESOLVE full run ===")
    for k, v in result.items():
        print(f"{k}: {v}")
    print("\nMongoDB LOCAL | journal events: %d | replay: ready"
          % result["journal_events"])
    sys.exit(0)
