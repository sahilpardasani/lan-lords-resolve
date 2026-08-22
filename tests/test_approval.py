"""Exact, expiring, one-use approval tests for consequential actions."""

from __future__ import annotations

import ast
import inspect
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

import resolve.approval as approval_module
from resolve.approval import (
    ApprovalGrant,
    ApprovalStatus,
    ApprovalValidationError,
    approval_fingerprint,
    approval_from_dict,
    consume_approval,
    create_approval,
    create_approval_for_decision,
    validate_approval,
)
from resolve.case import candidate_fingerprint
from resolve.contract import (
    EvaluatedDecision,
    build_constraint_validation_receipt,
    build_decision_input,
    build_evidence_receipt,
    build_objective_receipt,
    build_rehearsal_receipt,
    build_verification_receipt,
    evaluate_decision,
)

SECRET = b"resolve-test-secret-key-material-32-bytes-minimum"
OTHER_SECRET = b"different-test-secret-key-material-32-bytes"
ISSUED_AT = datetime(2026, 8, 22, 13, 38, tzinfo=UTC)
EXPIRES_AT = ISSUED_AT + timedelta(minutes=10)
CASE_FINGERPRINT = "a" * 64
EVIDENCE_FINGERPRINT = "b" * 64
STATE_FINGERPRINT = "c" * 64
DECISION_FINGERPRINT = "d" * 64


def bounded_candidate() -> dict:
    return {
        "action_type": "payments.failover",
        "target": "processor_b",
        "parameters": {"region": "US", "traffic_pct": 40},
    }


def evaluated_payment_decision(*, consequence: str = "C2"):
    case = {
        "name": "payment_outage",
        "objective": {
            "primary": "restore payments with regional compliance",
            "protected_outcomes": ["payment_success"],
            "anti_objectives": ["unsafe_global_failover"],
        },
        "evidence_roots": ["evidence/"],
        "constraints": ["bounded_processor_b_traffic"],
        "actions": [
            {
                "id": "payments.failover",
                "consequence": consequence,
                "reversible": True,
                "authority": "incident_commander",
                "allowed_targets": ["processor_b"],
                "allowed_parameters": {
                    "region": ["US"],
                    "traffic_pct": {"minimum": 1, "maximum": 40},
                },
            }
        ],
        "verification": {"success_conditions": ["actual_state_matches"]},
    }
    candidate = bounded_candidate()
    evidence = build_evidence_receipt(
        evidence_registry={"E01": "1" * 64},
        required_evidence_ids=frozenset({"E01"}),
        candidate_evidence_ids=frozenset({"E01"}),
    )
    decision = build_decision_input(
        raw_case=case,
        candidate=candidate,
        objective_receipt=build_objective_receipt(
            raw_case=case,
            evidence_receipt=evidence,
            candidate_objective="restore_payments",
            validator=lambda _case, _evidence: "restore_payments",
        ),
        evidence_receipt=evidence,
        constraint_receipt=build_constraint_validation_receipt(
            raw_case=case,
            candidate=candidate,
            validators={"bounded_processor_b_traffic": lambda _case, _candidate: ()},
        ),
        state_fingerprint=STATE_FINGERPRINT,
        consequence_assessed=True,
        reversibility_confirmed=True,
        rehearsal_receipt=build_rehearsal_receipt(
            candidate=candidate,
            state_fingerprint=STATE_FINGERPRINT,
            passed=True,
        ),
        requested_approver_role="incident_commander",
        verification_receipt=build_verification_receipt(
            candidate=candidate,
            state_fingerprint=STATE_FINGERPRINT,
            possible=True,
        ),
    )
    return evaluate_decision(decision)


def valid_grant(**changes: object) -> ApprovalGrant:
    values = {
        "candidate_fingerprint": candidate_fingerprint(bounded_candidate()),
        "case_fingerprint": CASE_FINGERPRINT,
        "evidence_fingerprint": EVIDENCE_FINGERPRINT,
        "state_fingerprint": STATE_FINGERPRINT,
        "decision_fingerprint": DECISION_FINGERPRINT,
        "approver": "Jordan Operator",
        "authority": "incident_commander",
        "consequence_class": "C2",
        "issued_at": ISSUED_AT,
        "expires_at": EXPIRES_AT,
        "nonce": "approval-nonce-0001",
        "secret_key": SECRET,
    }
    values.update(changes)
    return create_approval(**values)


def validation_kwargs(**changes: object) -> dict[str, object]:
    values: dict[str, object] = {
        "expected_candidate_fingerprint": candidate_fingerprint(bounded_candidate()),
        "expected_case_fingerprint": CASE_FINGERPRINT,
        "expected_evidence_fingerprint": EVIDENCE_FINGERPRINT,
        "expected_state_fingerprint": STATE_FINGERPRINT,
        "expected_decision_fingerprint": DECISION_FINGERPRINT,
        "expected_authority": "incident_commander",
        "expected_consequence_class": "C2",
        "now": ISSUED_AT + timedelta(minutes=1),
        "secret_key": SECRET,
    }
    values.update(changes)
    return values


def test_exact_approval_is_valid() -> None:
    validation = validate_approval(valid_grant(), **validation_kwargs())

    assert validation.valid is True
    assert validation.status is ApprovalStatus.VALID
    assert validation.reason_code is None


def test_approval_creation_is_deterministic_with_injected_time_and_nonce() -> None:
    assert valid_grant() == valid_grant()


def test_approval_is_created_directly_from_evaluated_decision_envelope() -> None:
    decision = evaluated_payment_decision()

    grant = create_approval_for_decision(
        decision,
        approver="Jordan Operator",
        issued_at=ISSUED_AT,
        expires_at=EXPIRES_AT,
        secret_key=SECRET,
        nonce="approval-nonce-from-decision",
    )

    assert grant.decision_fingerprint == decision.decision_fingerprint
    assert grant.candidate_fingerprint == decision.candidate_fingerprint
    assert grant.evidence_fingerprint == decision.evidence_fingerprint
    assert grant.state_fingerprint == decision.state_fingerprint
    assert grant.authority == decision.required_authority


def test_approval_cannot_be_created_from_unvalidated_or_nonwaiting_decision() -> None:
    with pytest.raises(ApprovalValidationError, match="evaluate_decision"):
        create_approval_for_decision(
            EvaluatedDecision(),
            approver="Jordan Operator",
            issued_at=ISSUED_AT,
            expires_at=EXPIRES_AT,
            secret_key=SECRET,
        )
    with pytest.raises(ApprovalValidationError, match="not waiting"):
        create_approval_for_decision(
            evaluated_payment_decision(consequence="C1"),
            approver="Jordan Operator",
            issued_at=ISSUED_AT,
            expires_at=EXPIRES_AT,
            secret_key=SECRET,
        )
    malformed = object.__new__(EvaluatedDecision)
    object.__setattr__(malformed, "_validated", True)
    object.__setattr__(malformed, "result", evaluated_payment_decision().result)
    object.__setattr__(malformed, "required_authority", None)
    object.__setattr__(malformed, "consequence_class", "C2")
    with pytest.raises(ApprovalValidationError, match="authority and consequence"):
        create_approval_for_decision(
            malformed,
            approver="Jordan Operator",
            issued_at=ISSUED_AT,
            expires_at=EXPIRES_AT,
            secret_key=SECRET,
        )


def test_default_nonce_is_securely_generated() -> None:
    grant = valid_grant(nonce=None)

    assert isinstance(grant.nonce, str)
    assert len(grant.nonce) >= 24


def test_approval_binds_exact_candidate_case_evidence_state_authority_and_consequence() -> (
    None
):
    grant = valid_grant()

    assert grant.candidate_fingerprint == candidate_fingerprint(bounded_candidate())
    assert grant.case_fingerprint == CASE_FINGERPRINT
    assert grant.evidence_fingerprint == EVIDENCE_FINGERPRINT
    assert grant.state_fingerprint == STATE_FINGERPRINT
    assert grant.decision_fingerprint == DECISION_FINGERPRINT
    assert grant.authority == "incident_commander"
    assert grant.consequence_class == "C2"
    assert grant.used is False
    assert len(grant.integrity) == 64


def test_approval_rejects_a_different_evaluated_decision_context() -> None:
    validation = validate_approval(
        valid_grant(),
        **validation_kwargs(expected_decision_fingerprint="e" * 64),
    )

    assert validation.status is ApprovalStatus.DECISION_MISMATCH


def test_us_to_global_mutation_invalidates_old_approval() -> None:
    mutated = bounded_candidate()
    mutated["parameters"]["region"] = "GLOBAL"

    validation = validate_approval(
        valid_grant(),
        **validation_kwargs(
            expected_candidate_fingerprint=candidate_fingerprint(mutated)
        ),
    )

    assert validation.status is ApprovalStatus.CANDIDATE_MISMATCH
    assert validation.valid is False


@pytest.mark.parametrize(
    ("changed_expectation", "expected_status"),
    [
        (
            {"expected_case_fingerprint": "c" * 64},
            ApprovalStatus.CASE_MISMATCH,
        ),
        (
            {"expected_evidence_fingerprint": "d" * 64},
            ApprovalStatus.EVIDENCE_MISMATCH,
        ),
        (
            {"expected_state_fingerprint": "d" * 64},
            ApprovalStatus.STATE_MISMATCH,
        ),
        (
            {"expected_authority": "automated_agent"},
            ApprovalStatus.AUTHORITY_MISMATCH,
        ),
        (
            {"expected_consequence_class": "C3"},
            ApprovalStatus.CONSEQUENCE_MISMATCH,
        ),
    ],
)
def test_bound_context_mismatch_invalidates_approval(
    changed_expectation: dict[str, object], expected_status: ApprovalStatus
) -> None:
    validation = validate_approval(
        valid_grant(), **validation_kwargs(**changed_expectation)
    )

    assert validation.status is expected_status
    assert validation.valid is False


def test_approval_expires_at_the_exact_expiry_boundary() -> None:
    validation = validate_approval(valid_grant(), **validation_kwargs(now=EXPIRES_AT))

    assert validation.status is ApprovalStatus.EXPIRED
    assert validation.valid is False


def test_approval_is_not_valid_before_its_issue_time() -> None:
    validation = validate_approval(
        valid_grant(),
        **validation_kwargs(now=ISSUED_AT - timedelta(microseconds=1)),
    )

    assert validation.status is ApprovalStatus.NOT_YET_VALID
    assert validation.valid is False


def test_approval_is_valid_at_its_exact_issue_time() -> None:
    validation = validate_approval(valid_grant(), **validation_kwargs(now=ISSUED_AT))

    assert validation.status is ApprovalStatus.VALID


def test_approval_is_valid_immediately_before_expiry() -> None:
    validation = validate_approval(
        valid_grant(),
        **validation_kwargs(now=EXPIRES_AT - timedelta(microseconds=1)),
    )

    assert validation.status is ApprovalStatus.VALID


def test_consumption_marks_approval_used_without_mutating_original() -> None:
    original = valid_grant()
    consumed = consume_approval(original, **validation_kwargs())

    assert original.used is False
    assert consumed.used is True
    assert consumed.integrity != original.integrity


def test_consumed_one_time_approval_cannot_be_reused() -> None:
    consumed = consume_approval(valid_grant(), **validation_kwargs())

    validation = validate_approval(consumed, **validation_kwargs())

    assert validation.status is ApprovalStatus.ALREADY_USED
    with pytest.raises(ApprovalValidationError, match="ALREADY_USED"):
        consume_approval(consumed, **validation_kwargs())


@pytest.mark.parametrize(
    ("field", "tampered_value"),
    [
        ("candidate_fingerprint", "c" * 64),
        ("case_fingerprint", "d" * 64),
        ("evidence_fingerprint", "e" * 64),
        ("state_fingerprint", "f" * 64),
        ("approver", "Mallory"),
        ("authority", "automated_agent"),
        ("consequence_class", "C3"),
        ("expires_at", EXPIRES_AT + timedelta(hours=1)),
        ("nonce", "attacker-controlled-nonce"),
        ("used", True),
    ],
)
def test_tampering_with_signed_fields_is_detected(
    field: str, tampered_value: object
) -> None:
    tampered = replace(valid_grant(), **{field: tampered_value})

    validation = validate_approval(tampered, **validation_kwargs())

    assert validation.status is ApprovalStatus.INTEGRITY_INVALID
    assert validation.valid is False


def test_wrong_hmac_key_is_rejected() -> None:
    validation = validate_approval(
        valid_grant(), **validation_kwargs(secret_key=OTHER_SECRET)
    )

    assert validation.status is ApprovalStatus.INTEGRITY_INVALID


def test_approval_serializes_to_integration_shape() -> None:
    serialized = valid_grant().to_dict()

    assert serialized == {
        "candidate_fingerprint": candidate_fingerprint(bounded_candidate()),
        "case_fingerprint": CASE_FINGERPRINT,
        "evidence_fingerprint": EVIDENCE_FINGERPRINT,
        "state_fingerprint": STATE_FINGERPRINT,
        "decision_fingerprint": DECISION_FINGERPRINT,
        "approver": "Jordan Operator",
        "authority": "incident_commander",
        "consequence_class": "C2",
        "issued_at": "2026-08-22T13:38:00Z",
        "expires_at": "2026-08-22T13:48:00Z",
        "nonce": "approval-nonce-0001",
        "used": False,
        "integrity": valid_grant().integrity,
    }


def test_approval_round_trips_through_a_strict_persistence_boundary() -> None:
    restored = approval_from_dict(valid_grant().to_dict())

    assert restored == valid_grant()
    assert validate_approval(restored, **validation_kwargs()).valid is True


@pytest.mark.parametrize(
    "mutation",
    [
        lambda record: record.pop("nonce"),
        lambda record: record.update({"unexpected": "field"}),
        lambda record: record.update({1: "field"}),
        lambda record: record.update({"used": "false"}),
        lambda record: record.update({"issued_at": 0}),
        lambda record: record.update({"issued_at": "not-a-timestamp"}),
        lambda record: record.update({"issued_at": "2" * 129}),
        lambda record: record.update({"integrity": "invalid"}),
    ],
)
def test_malformed_persisted_approval_fails_closed(mutation) -> None:
    record = valid_grant().to_dict()
    mutation(record)

    with pytest.raises(ApprovalValidationError):
        approval_from_dict(record)


def test_non_mapping_persisted_approval_fails_closed() -> None:
    with pytest.raises(ApprovalValidationError, match="must be a mapping"):
        approval_from_dict([])


@pytest.mark.parametrize(
    "changes",
    [
        {"consequence_class": "INVALID"},
        {"expires_at": ISSUED_AT},
    ],
)
def test_malformed_direct_grant_fails_stable_validation(
    changes: dict[str, object],
) -> None:
    malformed = replace(valid_grant(), **changes)

    with pytest.raises(ApprovalValidationError):
        validate_approval(malformed, **validation_kwargs())


def test_approval_fingerprint_is_stable_and_materially_sensitive() -> None:
    grant = valid_grant()
    changed = replace(grant, approver="Different Operator")

    assert approval_fingerprint(grant) == approval_fingerprint(valid_grant())
    assert approval_fingerprint(grant) != approval_fingerprint(changed)


@pytest.mark.parametrize(
    "changes",
    [
        {"candidate_fingerprint": "invalid"},
        {"case_fingerprint": "invalid"},
        {"evidence_fingerprint": "invalid"},
        {"state_fingerprint": "invalid"},
        {"decision_fingerprint": "invalid"},
        {"approver": ""},
        {"approver": "x" * 4_097},
        {"authority": " "},
        {"consequence_class": "CRITICAL"},
        {"issued_at": datetime(2026, 8, 22, 13, 38)},  # noqa: DTZ001
        {"expires_at": ISSUED_AT},
        {"nonce": ""},
        {"secret_key": b"too-short"},
        {"secret_key": b"x" * 4_097},
    ],
)
def test_invalid_approval_creation_fails_closed(changes: dict[str, object]) -> None:
    with pytest.raises(ApprovalValidationError):
        valid_grant(**changes)


def test_validation_rejects_naive_now_and_weak_key() -> None:
    with pytest.raises(ApprovalValidationError, match="timezone-aware"):
        validate_approval(
            valid_grant(),
            **validation_kwargs(
                now=datetime(2026, 8, 22, 13, 39)  # noqa: DTZ001
            ),
        )
    with pytest.raises(ApprovalValidationError, match="at least 32 bytes"):
        validate_approval(valid_grant(), **validation_kwargs(secret_key=b"short"))


def test_validation_rejects_invalid_grant_and_expected_consequence() -> None:
    with pytest.raises(ApprovalValidationError, match="ApprovalGrant"):
        validate_approval({}, **validation_kwargs())
    with pytest.raises(ApprovalValidationError, match="consequence class"):
        validate_approval(
            valid_grant(),
            **validation_kwargs(expected_consequence_class="CRITICAL"),
        )


def test_approval_fingerprint_rejects_non_grant() -> None:
    with pytest.raises(ApprovalValidationError, match="ApprovalGrant"):
        approval_fingerprint({})


def test_approval_grant_is_immutable() -> None:
    grant = valid_grant()

    with pytest.raises((AttributeError, TypeError)):
        grant.used = True


def test_hmac_validation_uses_constant_time_comparison() -> None:
    source = inspect.getsource(approval_module)

    assert "compare_digest" in source
    assert "resolve:approval:v1" in source


def test_approval_has_no_mongodb_imports() -> None:
    tree = ast.parse(inspect.getsource(approval_module))
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module)

    assert not any(
        "pymongo" in name or "mongo_store" in name for name in imported_modules
    )
