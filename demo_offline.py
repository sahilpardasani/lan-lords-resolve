"""
demo_offline.py  --  MongoDB crash / recover / sync demo (spec §17)

Runs the headline story:
  1. Mongo up, events persist normally
  2. Mongo "crashes" mid-run -> Resolve keeps going, journal records locally
  3. Mongo returns -> auto-detect, sync backlog (ordered, idempotent)
  4. 0 unsynced, journal integrity verified
  5. tamper demo: corrupt a journal line, integrity check catches it

Uses the throwaway mock journal (mocks/mock_journal.py) + your real
mongo_store sync layer. Delete the mock when Coder 2's journal.py lands.

Run:  python demo_offline.py
"""

from resolve import mongo_store as store
from mocks import mock_journal as journal


_prev = {"hash": "GENESIS"}


def event(run_id, seq, etype, payload):
    payload_hash = store._sha(store._canonical(payload))
    prev = _prev["hash"]
    event_hash = store._sha(store._canonical(
        {"payload_hash": payload_hash, "prev_hash": prev,
         "sequence": seq, "event_type": etype}))
    _prev["hash"] = event_hash
    return {"event_id": f"{run_id}-{seq}", "case_id": "case_primary",
            "run_id": run_id, "sequence": seq, "event_type": etype,
            "payload": payload, "payload_hash": payload_hash,
            "prev_hash": prev, "event_hash_or_mac": event_hash}


def persist(ev, mongo_up):
    """Journal ALWAYS records. Mongo only when up. Returns whether it synced."""
    journal.append(ev)
    if mongo_up:
        store.append_journal_event(ev)
        journal.mark_synced([ev["sequence"]])
        return True
    return False


def line(txt=""):
    print(txt)


def run():
    store.connect(); store.ensure_indexes()
    journal.reset()
    run_id = "run_offline_demo"
    # clear any prior demo data for a clean run
    store.connect().journal_events.delete_many({"run_id": run_id})

    line("=" * 56)
    line("  RESOLVE  —  MongoDB crash / recover / sync demo")
    line("=" * 56)

    line("\n[1] MongoDB ONLINE — events persist normally")
    for seq, et in [(0, "INCIDENT_DETECTED"), (1, "AI_PROPOSAL"),
                    (2, "CONTRACT_EVALUATED")]:
        persist(event(run_id, seq, et, {"seq": seq}), mongo_up=True)
    line(f"    persisted seqs in Mongo: {sorted(store.persisted_seqs(run_id))}")
    line(f"    unsynced in journal:     {[e['sequence'] for e in journal.unsynced()]}")

    line("\n[2] *** MongoDB CRASHES mid-run ***")
    line("    Resolve keeps running. Journal records locally.")
    for seq, et in [(3, "APPROVAL_ISSUED"), (4, "ACTION_COMMITTED"),
                    (5, "VERIFIED")]:
        persist(event(run_id, seq, et, {"seq": seq}), mongo_up=False)
        line(f"    journal recorded seq {seq} ({et})  [UNSYNCED]")
    line(f"\n    MONGODB: OFFLINE | LOCAL JOURNAL: RECORDING | "
         f"UNSYNCED EVENTS: {len(journal.unsynced())}")

    line("\n[3] *** MongoDB RECOVERS ***")
    integ = journal.verify_integrity()
    line(f"    journal integrity: {'VERIFIED' if integ['intact'] else 'FAILED'}")
    backlog = journal.unsynced()
    already = store.persisted_seqs(run_id)
    missing = [e for e in backlog if e["sequence"] not in already]
    line(f"    Mongo already has: {sorted(already)}")
    line(f"    syncing missing:  {[e['sequence'] for e in missing]}")
    result = store.sync_run(missing)
    journal.mark_synced(result["synced"])
    line(f"    sync result: synced={result['synced']} "
         f"already_present={result['already_present']}")

    line("\n[4] FINAL STATE")
    line(f"    MONGODB: ONLINE")
    line(f"    persisted seqs: {sorted(store.persisted_seqs(run_id))}")
    line(f"    UNSYNCED EVENTS: {len(journal.unsynced())}")
    line(f"    JOURNAL INTEGRITY: "
         f"{'VERIFIED' if journal.verify_integrity()['intact'] else 'FAILED'}")

    line("\n[5] TAMPER DEMO — corrupt one Mongo journal event")
    store.connect().journal_events.update_one(
        {"run_id": run_id, "sequence": 2},
        {"$set": {"payload": {"seq": 999}}})
    chain = store.verify_journal_chain(run_id)
    line(f"    Mongo chain check: "
         f"{'INTACT' if chain['intact'] else 'TAMPER DETECTED at seq %s' % chain.get('broken_at_sequence')}")

    line("\n" + "=" * 56)
    line("  MongoDB LOCAL | journal preserved | sync complete | replay ready")
    line("=" * 56)


if __name__ == "__main__":
    run()
