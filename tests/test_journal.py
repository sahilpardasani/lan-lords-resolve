"""Tamper-evident canonical journal tests."""

from __future__ import annotations

import ast
import inspect
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

import resolve.journal as journal_module
from resolve.journal import (
    GENESIS_HASH,
    JournalEvent,
    JournalStatus,
    JournalValidationError,
    create_event,
    journal_event_from_dict,
    verify_chain,
    verify_event,
)

SECRET = b"resolve-journal-test-key-material-32-bytes-minimum"
OTHER_SECRET = b"different-journal-test-key-material-32-bytes"
START = datetime(2026, 8, 22, 13, 30, tzinfo=UTC)


def first_event(**changes: object) -> JournalEvent:
    values = {
        "event_id": "EVT-0001",
        "case_id": "payment-outage-001",
        "run_id": "RUN-0001",
        "sequence": 1,
        "timestamp": START,
        "event_type": "RUN_CREATED",
        "payload": {"baseline_success_rate": 0.986},
        "prev_hash": GENESIS_HASH,
        "secret_key": SECRET,
    }
    values.update(changes)
    return create_event(**values)


def event_chain() -> tuple[JournalEvent, ...]:
    first = first_event()
    second = create_event(
        event_id="EVT-0002",
        case_id=first.case_id,
        run_id=first.run_id,
        sequence=2,
        timestamp=START + timedelta(seconds=1),
        event_type="CANDIDATE_PROPOSED",
        payload={
            "candidate": {
                "action_type": "payments.failover",
                "target": "processor_b",
                "parameters": {"region": "GLOBAL", "traffic_pct": 100},
            }
        },
        prev_hash=first.event_hash_or_mac,
        secret_key=SECRET,
    )
    third = create_event(
        event_id="EVT-0003",
        case_id=first.case_id,
        run_id=first.run_id,
        sequence=3,
        timestamp=START + timedelta(seconds=2),
        event_type="CONTRACT_EVALUATED",
        payload={
            "disposition": "BLOCKED",
            "reason_codes": ["HARD_CONSTRAINT_VIOLATION"],
        },
        prev_hash=second.event_hash_or_mac,
        secret_key=SECRET,
    )
    return first, second, third


def test_event_contains_canonical_integrity_fields() -> None:
    event = first_event()

    assert len(event.payload_hash) == 64
    assert event.prev_hash == GENESIS_HASH
    assert len(event.event_hash_or_mac) == 64
    assert verify_event(event, secret_key=SECRET).status is JournalStatus.VALID


def test_identical_event_input_produces_identical_hashes() -> None:
    assert first_event() == first_event()


def test_payload_dictionary_order_does_not_change_integrity() -> None:
    left = first_event(payload={"a": 1, "b": 2})
    right = first_event(payload={"b": 2, "a": 1})

    assert left.payload_hash == right.payload_hash
    assert left.event_hash_or_mac == right.event_hash_or_mac


def test_payload_hash_preserves_material_string_whitespace() -> None:
    plain = first_event(payload={"command": "abc"})
    spaced = first_event(payload={"command": " abc "})

    assert plain.payload_hash != spaced.payload_hash
    assert spaced.to_dict()["payload"] == {"command": " abc "}


def test_cyclic_payload_fails_with_stable_validation_error() -> None:
    payload: dict = {}
    payload["cycle"] = payload

    with pytest.raises(JournalValidationError, match="cyclic"):
        first_event(payload=payload)


def test_indirect_tuple_cycle_fails_closed_but_shared_subtree_is_allowed() -> None:
    cyclic_list: list = []
    cyclic_tuple = (cyclic_list,)
    cyclic_list.append(cyclic_tuple)
    shared = {"value": 1}

    with pytest.raises(JournalValidationError, match="cyclic"):
        first_event(payload={"cycle": cyclic_tuple})
    assert verify_event(
        first_event(payload={"left": shared, "right": shared}),
        secret_key=SECRET,
    ).valid


def test_excessively_deep_payload_fails_closed() -> None:
    payload: dict = {}
    nested = payload
    for _ in range(40):
        child: dict = {}
        nested["child"] = child
        nested = child

    with pytest.raises(JournalValidationError, match="nesting depth"):
        first_event(payload=payload)


def test_oversized_payload_string_fails_closed() -> None:
    with pytest.raises(JournalValidationError, match="65,536 bytes"):
        first_event(payload={"value": "x" * 65_537})


def test_payload_member_and_total_node_counts_are_bounded() -> None:
    too_many_members = {f"key-{index}": index for index in range(10_001)}
    too_many_nodes = {"items": [None] * 10_000}

    with pytest.raises(JournalValidationError, match="member count"):
        first_event(payload=too_many_members)
    with pytest.raises(JournalValidationError, match="node count"):
        first_event(payload=too_many_nodes)


def test_payload_rejects_oversized_keys_and_integers() -> None:
    with pytest.raises(JournalValidationError, match="mapping key"):
        first_event(payload={"x" * 65_537: 1})
    with pytest.raises(JournalValidationError, match="integer exceeds"):
        first_event(payload={"value": 1 << 4_096})


def test_payload_total_string_budget_is_bounded() -> None:
    payload = {f"field-{index}": "x" * 60_000 for index in range(20)}

    with pytest.raises(JournalValidationError, match="total string budget"):
        first_event(payload=payload)

    payload = {(f"{index:02d}" + "k" * 59_998): index for index in range(20)}
    with pytest.raises(JournalValidationError, match="total string budget"):
        first_event(payload=payload)


def test_event_payload_is_deeply_immutable() -> None:
    event = first_event(payload={"nested": {"values": [1, 2]}})

    with pytest.raises(TypeError):
        event.payload["new"] = "tamper"
    with pytest.raises(TypeError):
        event.payload["nested"]["new"] = "tamper"


def test_event_serializes_to_mongo_safe_shape() -> None:
    serialized = first_event().to_dict()

    assert serialized == {
        "event_id": "EVT-0001",
        "case_id": "payment-outage-001",
        "run_id": "RUN-0001",
        "sequence": 1,
        "timestamp": "2026-08-22T13:30:00Z",
        "event_type": "RUN_CREATED",
        "payload": {"baseline_success_rate": 0.986},
        "payload_hash": first_event().payload_hash,
        "prev_hash": GENESIS_HASH,
        "event_hash_or_mac": first_event().event_hash_or_mac,
    }


def test_event_round_trips_through_a_strict_persistence_boundary() -> None:
    restored = journal_event_from_dict(first_event().to_dict())

    assert restored == first_event()
    assert verify_event(restored, secret_key=SECRET).valid is True


@pytest.mark.parametrize(
    "mutation",
    [
        lambda record: record.pop("event_id"),
        lambda record: record.update({"unexpected": "field"}),
        lambda record: record.update({1: "field"}),
        lambda record: record.update({"sequence": True}),
        lambda record: record.update({"timestamp": 0}),
        lambda record: record.update({"timestamp": "not-a-timestamp"}),
        lambda record: record.update({"timestamp": "2" * 129}),
        lambda record: record.update({"payload": []}),
        lambda record: record.update({"event_hash_or_mac": "invalid"}),
    ],
)
def test_malformed_persisted_event_fails_closed(mutation) -> None:
    record = first_event().to_dict()
    mutation(record)

    with pytest.raises(JournalValidationError):
        journal_event_from_dict(record)


def test_non_mapping_persisted_event_fails_closed() -> None:
    with pytest.raises(JournalValidationError, match="must be a mapping"):
        journal_event_from_dict([])


@pytest.mark.parametrize(
    ("field", "tampered_value", "expected_status"),
    [
        (
            "payload",
            {"baseline_success_rate": 1.0},
            JournalStatus.PAYLOAD_HASH_MISMATCH,
        ),
        ("payload_hash", "c" * 64, JournalStatus.PAYLOAD_HASH_MISMATCH),
        ("sequence", 2, JournalStatus.EVENT_INTEGRITY_INVALID),
        ("event_type", "RUN_CLOSED", JournalStatus.EVENT_INTEGRITY_INVALID),
        ("prev_hash", "d" * 64, JournalStatus.EVENT_INTEGRITY_INVALID),
        ("event_hash_or_mac", "e" * 64, JournalStatus.EVENT_INTEGRITY_INVALID),
    ],
)
def test_event_tampering_is_detected(
    field: str, tampered_value: object, expected_status: JournalStatus
) -> None:
    tampered = replace(first_event(), **{field: tampered_value})

    assert verify_event(tampered, secret_key=SECRET).status is expected_status


def test_wrong_hmac_key_is_detected() -> None:
    result = verify_event(first_event(), secret_key=OTHER_SECRET)

    assert result.status is JournalStatus.EVENT_INTEGRITY_INVALID


def test_chain_returns_the_first_event_integrity_failure() -> None:
    first, second, third = event_chain()
    tampered_second = replace(second, payload={"candidate": "tampered"})

    result = verify_chain((first, tampered_second, third), secret_key=SECRET)

    assert result.status is JournalStatus.PAYLOAD_HASH_MISMATCH
    assert result.failed_sequence == 2


def test_complete_chain_verifies() -> None:
    result = verify_chain(event_chain(), secret_key=SECRET)

    assert result.valid is True
    assert result.status is JournalStatus.VALID
    assert result.failed_sequence is None


def test_anchored_complete_chain_verifies() -> None:
    chain = event_chain()

    result = verify_chain(
        chain,
        secret_key=SECRET,
        expected_final_sequence=3,
        expected_final_hash=chain[-1].event_hash_or_mac,
    )

    assert result.status is JournalStatus.VALID


def test_anchor_detects_deleted_final_event() -> None:
    chain = event_chain()

    result = verify_chain(
        chain[:-1],
        secret_key=SECRET,
        expected_final_sequence=3,
        expected_final_hash=chain[-1].event_hash_or_mac,
    )

    assert result.status is JournalStatus.TERMINAL_SEQUENCE_MISMATCH


def test_anchor_detects_wrong_terminal_hash() -> None:
    result = verify_chain(
        event_chain(),
        secret_key=SECRET,
        expected_final_sequence=3,
        expected_final_hash="f" * 64,
    )

    assert result.status is JournalStatus.TERMINAL_HASH_MISMATCH


def test_replay_anchor_requires_sequence_and_hash_together() -> None:
    with pytest.raises(JournalValidationError, match="must be provided together"):
        verify_chain(event_chain(), secret_key=SECRET, expected_final_sequence=3)


def test_replay_anchor_rejects_invalid_sequence() -> None:
    with pytest.raises(JournalValidationError, match="positive integer"):
        verify_chain(
            event_chain(),
            secret_key=SECRET,
            expected_final_sequence=0,
            expected_final_hash=event_chain()[-1].event_hash_or_mac,
        )


def test_empty_chain_is_not_a_replay_receipt() -> None:
    result = verify_chain((), secret_key=SECRET)

    assert result.status is JournalStatus.EMPTY_CHAIN
    assert result.valid is False


def test_deleted_middle_event_breaks_chain() -> None:
    first, _, third = event_chain()

    result = verify_chain((first, third), secret_key=SECRET)

    assert result.status is JournalStatus.SEQUENCE_INVALID
    assert result.failed_sequence == 3


def test_reordered_events_break_chain() -> None:
    first, second, third = event_chain()

    result = verify_chain((first, third, second), secret_key=SECRET)

    assert result.status is JournalStatus.SEQUENCE_INVALID


def test_broken_previous_hash_is_detected() -> None:
    first, second, third = event_chain()
    resigned_second = create_event(
        event_id=second.event_id,
        case_id=second.case_id,
        run_id=second.run_id,
        sequence=second.sequence,
        timestamp=second.timestamp,
        event_type=second.event_type,
        payload=second.payload,
        prev_hash="f" * 64,
        secret_key=SECRET,
    )

    result = verify_chain((first, resigned_second, third), secret_key=SECRET)

    assert result.status is JournalStatus.PREV_HASH_MISMATCH
    assert result.failed_sequence == 2


@pytest.mark.parametrize(
    ("field", "changed", "expected_status"),
    [
        ("run_id", "RUN-OTHER", JournalStatus.RUN_MISMATCH),
        ("case_id", "case-other", JournalStatus.CASE_MISMATCH),
        ("event_id", "EVT-0001", JournalStatus.DUPLICATE_EVENT_ID),
    ],
)
def test_chain_identity_invariants(
    field: str, changed: str, expected_status: JournalStatus
) -> None:
    first, second, third = event_chain()
    replacement = create_event(
        event_id=changed if field == "event_id" else second.event_id,
        case_id=changed if field == "case_id" else second.case_id,
        run_id=changed if field == "run_id" else second.run_id,
        sequence=second.sequence,
        timestamp=second.timestamp,
        event_type=second.event_type,
        payload=second.payload,
        prev_hash=first.event_hash_or_mac,
        secret_key=SECRET,
    )

    result = verify_chain((first, replacement, third), secret_key=SECRET)

    assert result.status is expected_status


@pytest.mark.parametrize(
    "changes",
    [
        {"event_id": ""},
        {"event_id": "x" * 4_097},
        {"case_id": ""},
        {"run_id": ""},
        {"sequence": 0},
        {"sequence": True},
        {"timestamp": datetime(2026, 8, 22, 13, 30)},  # noqa: DTZ001
        {"event_type": ""},
        {"payload": []},
        {"payload": {1: "invalid-key"}},
        {"payload": {"value": float("nan")}},
        {"payload": {"value": {"unsupported"}}},
        {"prev_hash": "invalid"},
        {"secret_key": b"short"},
        {"secret_key": b"x" * 4_097},
    ],
)
def test_invalid_event_creation_fails_closed(changes: dict[str, object]) -> None:
    with pytest.raises(JournalValidationError):
        first_event(**changes)


def test_verification_rejects_non_event_and_weak_key() -> None:
    with pytest.raises(JournalValidationError, match="JournalEvent"):
        verify_event({}, secret_key=SECRET)
    with pytest.raises(JournalValidationError, match="at least 32 bytes"):
        verify_event(first_event(), secret_key=b"short")


def test_chain_rejects_non_event_member() -> None:
    with pytest.raises(JournalValidationError, match="JournalEvent"):
        verify_chain((first_event(), {}), secret_key=SECRET)


def test_chain_length_is_bounded_before_replay_work() -> None:
    with pytest.raises(JournalValidationError, match="maximum chain length"):
        verify_chain((first_event(),) * 10_001, secret_key=SECRET)


def test_journal_uses_constant_time_hmac_comparison() -> None:
    assert "compare_digest" in inspect.getsource(journal_module)
    assert "resolve:journal:v1" in inspect.getsource(journal_module)


def test_journal_has_no_mongodb_imports() -> None:
    tree = ast.parse(inspect.getsource(journal_module))
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module)

    assert not any(
        "pymongo" in name or "mongo_store" in name for name in imported_modules
    )
