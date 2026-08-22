"""
tests/test_mongo_store.py  --  P0 persistence tests (Coder 3)

Covers the MONGODB_P0.md "Minimum tests" that live on the persistence side.
Uses mongomock so it runs in CI / offline without a live mongod.
(Contract-on/off determinism is Coder 2's test, not here.)

Run:  pytest tests/test_mongo_store.py -v
"""

import importlib
import pytest

mongomock = pytest.importorskip("mongomock")


@pytest.fixture
def store():
    """Fresh in-memory Mongo per test, wired into mongo_store."""
    import resolve.mongo_store as ms
    importlib.reload(ms)
    client = mongomock.MongoClient()
    ms.connect = lambda uri=None: client[ms.DB_NAME]
    ms.ensure_indexes()
    return ms


def _journal(event_id, run_id, seq, prev="GENESIS", h=None):
    import resolve.mongo_store as ms
    payload = {"seq": seq}
    return {
        "event_id": event_id,
        "case_id": "case_primary",
        "run_id": run_id,
        "sequence": seq,
        "event_type": "CONTRACT_EVALUATED",
        "payload": payload,
        "payload_hash": ms._sha(ms._canonical(payload)),  # real hash
        "prev_hash": prev,
        "event_hash_or_mac": h or f"h{seq}",
    }


def test_case_snapshot_round_trip(store):
    store.insert_case_snapshot("case_primary", "cf_abc", {"objective": "restore"})
    got = store.export_run("run1")["cases"]
    assert any(c["case_fingerprint"] == "cf_abc" for c in got)


def test_journal_sequence_order(store):
    for i in range(3):
        store.append_journal_event(_journal(f"e{i}", "run1", i,
                                            prev="GENESIS" if i == 0 else f"h{i-1}"))
    seqs = [e["sequence"] for e in store.list_journal("run1")]
    assert seqs == [0, 1, 2]


def test_duplicate_run_sequence_rejected(store):
    store.append_journal_event(_journal("e0", "run1", 0))
    with pytest.raises(ValueError):
        store.append_journal_event(_journal("eX", "run1", 0))  # same (run,seq)


def test_duplicate_event_id_rejected(store):
    store.append_journal_event(_journal("e0", "run1", 0))
    with pytest.raises(ValueError):
        store.append_journal_event(_journal("e0", "run1", 5))  # same event_id


def test_missing_required_fields_rejected(store):
    with pytest.raises(ValueError):
        store.append_journal_event({"run_id": "run1", "sequence": 0})


def test_candidate_fingerprint_round_trip(store):
    store.insert_candidate("cand1", "run1",
                           {"target": "processor_b", "region": "US", "traffic_pct": 40},
                           "fp_good")
    c = store.export_run("run1")["candidates"][0]
    assert c["candidate_fingerprint"] == "fp_good"


def test_approval_round_trip_and_unused(store):
    store.insert_approval("appr1", "run1", "fp_good", "cf_abc",
                          "payments_ops_lead", "2026-08-22T23:00:00Z",
                          "nonce123", "integrity_1")
    a = store.export_run("run1")["approvals"][0]
    assert a["candidate_fingerprint"] == "fp_good"
    assert a["used"] is False
    assert a["status"] == "ISSUED"


def test_mutated_candidate_distinct_fingerprint(store):
    store.insert_candidate("cand1", "run1",
                           {"target": "processor_b", "region": "US", "traffic_pct": 40},
                           "fp_good")
    store.insert_candidate("cand2", "run1",
                           {"target": "processor_b", "region": "GLOBAL", "traffic_pct": 100},
                           "fp_bad")
    cands = {c["candidate_id"]: c["candidate_fingerprint"]
             for c in store.export_run("run1")["candidates"]}
    assert cands["cand1"] != cands["cand2"]


def test_verification_export(store):
    store.insert_verification("ver1", "run1", "fp_good",
                              {"success_rate": 97.2}, True)
    exp = store.export_run("run1")
    assert len(exp["verification_events"]) == 1
    assert exp["verification_events"][0]["success"] is True


def test_export_bundle_complete(store):
    store.insert_case_snapshot("case_primary", "cf_abc", {"objective": "restore"})
    for i in range(2):
        store.append_journal_event(_journal(f"e{i}", "run1", i,
                                            prev="GENESIS" if i == 0 else f"h{i-1}"))
    store.insert_candidate("cand1", "run1", {"region": "US"}, "fp_good")
    store.insert_approval("appr1", "run1", "fp_good", "cf_abc", "lead",
                          "2026-08-22T23:00:00Z", "n1", "i1")
    store.insert_verification("ver1", "run1", "fp_good", {"ok": True}, True)
    exp = store.export_run("run1")
    assert exp["run_id"] == "run1"
    assert len(exp["journal_events"]) == 2
    assert len(exp["candidates"]) == 1
    assert len(exp["approvals"]) == 1
    assert len(exp["verification_events"]) == 1


def test_journal_chain_intact(store):
    for i in range(3):
        store.append_journal_event(_journal(f"e{i}", "run1", i,
                                            prev="GENESIS" if i == 0 else f"h{i-1}"))
    report = store.verify_journal_chain("run1")
    assert report["intact"] is True
    assert report["events"] == 3


def test_journal_chain_detects_break(store):
    store.append_journal_event(_journal("e0", "run1", 0))
    # next event points at the wrong prev_hash -> chain must break
    store.append_journal_event(_journal("e1", "run1", 1, prev="WRONG"))
    report = store.verify_journal_chain("run1")
    assert report["intact"] is False
    assert report["broken_at_sequence"] == 1
