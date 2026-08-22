"""Contract-boundary tests for case and candidate identity.

These tests intentionally describe the public interface before ``resolve.case``
exists.  The payment scenario supplies useful examples, but the identity rules
must remain domain-independent so the same permission kernel can load another
case without code changes.
"""

from __future__ import annotations

import ast
import inspect
from copy import deepcopy
from dataclasses import asdict

import pytest

import resolve.contract as contract_module
from resolve.case import (
    CaseValidationError,
    candidate_fingerprint,
    case_fingerprint,
    normalize_case,
)
from resolve.contract import (
    ConstraintValidationReceipt,
    DecisionInput,
    DecisionValidationError,
    Disposition,
    EvidenceReceipt,
    GateValue,
    ObjectiveReceipt,
    RehearsalReceipt,
    VerificationReceipt,
    build_constraint_validation_receipt,
    build_decision_input,
    build_evidence_receipt,
    build_objective_receipt,
    build_rehearsal_receipt,
    build_verification_receipt,
    decision_fingerprint,
    evaluate_contract,
    evaluate_decision,
)

STATE_FINGERPRINT = "c" * 64


def payment_case() -> dict:
    """Return the locked payment case shape used by the core tests."""

    return {
        "name": "payment_outage",
        "objective": {
            "primary": (
                "restore payment authorization while preserving regional "
                "processor compliance"
            ),
            "protected_outcomes": [
                "payment_success",
                "regional_processor_compliance",
            ],
            "anti_objectives": ["global_unsafe_failover"],
        },
        "evidence_roots": ["evidence/incident.json", "evidence/policy.json"],
        "constraints": ["processor_b_only_for_eligible_bounded_traffic"],
        "actions": [
            {
                "id": "payments.failover",
                "consequence": "C2",
                "reversible": True,
                "authority": "incident_commander",
                "allowed_targets": ["processor_b"],
                "allowed_parameters": {
                    "region": ["US"],
                    "traffic_pct": {"minimum": 1, "maximum": 40},
                },
            }
        ],
        "verification": {
            "success_conditions": [
                "actual_simulator_state_matches_approved_candidate",
                "policy_violations_equal_zero",
            ]
        },
        "watch": {"reopen_conditions": ["payment_success_drops"]},
    }


def bounded_candidate() -> dict:
    """Return the candidate that may advance to exact human approval."""

    return {
        "action_type": "payments.failover",
        "target": "processor_b",
        "parameters": {"region": "US", "traffic_pct": 40},
    }


def passing_constraint_validators(raw_case: dict) -> dict:
    """Return trusted local validators that report no domain violations."""

    return {
        constraint_id: lambda _case, _candidate: ()
        for constraint_id in raw_case["constraints"]
    }


def valid_decision_input(
    *, candidate: dict | None = None, raw_case: dict | None = None, **changes: object
) -> DecisionInput:
    """Return a valid input, with explicit overrides for kernel unit tests."""

    actual_case = raw_case if raw_case is not None else payment_case()
    actual_candidate = candidate if candidate is not None else bounded_candidate()
    evidence = build_evidence_receipt(
        evidence_registry={"E01": "1" * 64, "E05": "5" * 64, "E07": "7" * 64},
        required_evidence_ids=frozenset({"E01", "E05", "E07"}),
        candidate_evidence_ids=frozenset({"E01", "E05", "E07"}),
    )
    objective = build_objective_receipt(
        raw_case=actual_case,
        evidence_receipt=evidence,
        candidate_objective="restore_payments_with_regional_compliance",
        validator=lambda _case, _evidence: "restore_payments_with_regional_compliance",
    )
    if not isinstance(actual_case, dict) or not isinstance(actual_candidate, dict):
        return build_decision_input(
            raw_case=actual_case,
            candidate=actual_candidate,
            objective_receipt=objective,
            evidence_receipt=evidence,
            constraint_receipt=None,
            state_fingerprint=STATE_FINGERPRINT,
            consequence_assessed=True,
            reversibility_confirmed=True,
            rehearsal_receipt=None,
            requested_approver_role="incident_commander",
            verification_receipt=None,
        )
    constraints = build_constraint_validation_receipt(
        raw_case=actual_case,
        candidate=actual_candidate,
        validators=passing_constraint_validators(actual_case),
    )
    rehearsal = build_rehearsal_receipt(
        candidate=actual_candidate,
        state_fingerprint=STATE_FINGERPRINT,
        passed=True,
    )
    verification = build_verification_receipt(
        candidate=actual_candidate,
        state_fingerprint=STATE_FINGERPRINT,
        possible=True,
    )
    decision = build_decision_input(
        raw_case=actual_case,
        candidate=actual_candidate,
        objective_receipt=objective,
        evidence_receipt=evidence,
        constraint_receipt=constraints,
        state_fingerprint=STATE_FINGERPRINT,
        consequence_assessed=True,
        reversibility_confirmed=True,
        rehearsal_receipt=rehearsal,
        requested_approver_role="incident_commander",
        verification_receipt=verification,
    )
    for field, value in changes.items():
        object.__setattr__(decision, field, value)
    decision._validate()
    return decision


def test_valid_case_normalizes_to_canonical_mapping() -> None:
    normalized = normalize_case(payment_case())

    assert normalized["name"] == "payment_outage"
    assert normalized["actions"][0]["authority"] == "incident_commander"
    assert normalized["verification"]["success_conditions"]


@pytest.mark.parametrize(
    "missing_path",
    [
        ("name",),
        ("objective", "primary"),
        ("constraints",),
        ("actions",),
        ("actions", 0, "authority"),
        ("verification", "success_conditions"),
    ],
)
def test_missing_permission_material_fails_closed(missing_path: tuple) -> None:
    raw = payment_case()
    cursor = raw
    for key in missing_path[:-1]:
        cursor = cursor[key]
    del cursor[missing_path[-1]]

    with pytest.raises(CaseValidationError):
        normalize_case(raw)


@pytest.mark.parametrize(
    ("path", "invalid_value"),
    [
        (("objective", "protected_outcomes"), "payment_success"),
        (("evidence_roots",), "evidence/"),
        (("constraints",), "constraint"),
        (("actions", 0, "reversible"), "true"),
        (("actions", 0, "consequence"), "CRITICAL"),
        (("actions", 0, "allowed_parameters"), []),
        (("verification", "success_conditions"), "verified"),
    ],
)
def test_invalid_case_types_and_enums_are_rejected(
    path: tuple, invalid_value: object
) -> None:
    raw = payment_case()
    cursor = raw
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = invalid_value

    with pytest.raises(CaseValidationError):
        normalize_case(raw)


def test_duplicate_action_ids_are_rejected() -> None:
    raw = payment_case()
    raw["actions"].append(deepcopy(raw["actions"][0]))

    with pytest.raises(CaseValidationError, match="duplicate"):
        normalize_case(raw)


def test_empty_required_string_is_rejected() -> None:
    raw = payment_case()
    raw["actions"][0]["authority"] = "   "

    with pytest.raises(CaseValidationError, match="non-empty string"):
        normalize_case(raw)


def test_actions_must_be_a_nonempty_list() -> None:
    wrong_type = payment_case()
    wrong_type["actions"] = "payments.failover"
    empty = payment_case()
    empty["actions"] = []

    with pytest.raises(CaseValidationError, match="must be a list"):
        normalize_case(wrong_type)
    with pytest.raises(CaseValidationError, match="must not be empty"):
        normalize_case(empty)


def test_verification_success_conditions_must_not_be_empty() -> None:
    raw = payment_case()
    raw["verification"]["success_conditions"] = []

    with pytest.raises(CaseValidationError, match="must not be empty"):
        normalize_case(raw)


def test_normalization_does_not_mutate_business_owned_input() -> None:
    raw = payment_case()
    original = deepcopy(raw)

    normalize_case(raw)

    assert raw == original


def test_case_fingerprint_is_stable_across_mapping_key_order() -> None:
    original = payment_case()
    reordered = {
        "watch": original["watch"],
        "verification": original["verification"],
        "actions": original["actions"],
        "constraints": original["constraints"],
        "evidence_roots": original["evidence_roots"],
        "objective": original["objective"],
        "name": original["name"],
    }

    assert case_fingerprint(original) == case_fingerprint(reordered)


def test_watch_section_is_optional_for_closed_cases() -> None:
    raw = payment_case()
    del raw["watch"]

    assert len(case_fingerprint(raw)) == 64


@pytest.mark.parametrize(
    ("path", "material_change"),
    [
        (("objective", "primary"), "maximize payment volume at any cost"),
        (("constraints", 0), "processor_b_allows_global_traffic"),
        (("actions", 0, "authority"), "automated_agent"),
        (("actions", 0, "allowed_parameters", "region"), ["GLOBAL"]),
        (
            ("verification", "success_conditions", 0),
            "trust_the_model_report",
        ),
    ],
)
def test_material_case_changes_create_new_fingerprint(
    path: tuple, material_change: object
) -> None:
    original = payment_case()
    changed = deepcopy(original)
    cursor = changed
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = material_change

    assert case_fingerprint(original) != case_fingerprint(changed)


def test_case_fingerprint_preserves_exact_allowed_parameter_whitespace() -> None:
    original = payment_case()
    changed = deepcopy(original)
    changed["actions"][0]["allowed_parameters"]["region"] = [" US "]

    assert case_fingerprint(original) != case_fingerprint(changed)


def test_candidate_fingerprint_is_stable_across_parameter_key_order() -> None:
    original = bounded_candidate()
    reordered = {
        "target": "processor_b",
        "parameters": {"traffic_pct": 40, "region": "US"},
        "action_type": "payments.failover",
    }

    assert candidate_fingerprint(original) == candidate_fingerprint(reordered)


@pytest.mark.parametrize(
    ("field", "material_change"),
    [
        ("region", "GLOBAL"),
        ("traffic_pct", 50),
    ],
)
def test_material_parameter_mutation_changes_candidate_fingerprint(
    field: str, material_change: object
) -> None:
    original = bounded_candidate()
    changed = deepcopy(original)
    changed["parameters"][field] = material_change

    assert candidate_fingerprint(original) != candidate_fingerprint(changed)


def test_candidate_fingerprint_preserves_material_parameter_whitespace() -> None:
    original = bounded_candidate()
    original["parameters"]["routing_token"] = "abc"
    changed = deepcopy(original)
    changed["parameters"]["routing_token"] = " abc "

    assert candidate_fingerprint(original) != candidate_fingerprint(changed)


def test_cyclic_candidate_fails_with_stable_validation_error() -> None:
    candidate = bounded_candidate()
    candidate["parameters"]["cycle"] = candidate["parameters"]

    with pytest.raises(CaseValidationError, match="cyclic"):
        candidate_fingerprint(candidate)


def test_reused_noncyclic_candidate_subtree_is_allowed() -> None:
    shared = {"value": 1}
    candidate = bounded_candidate()
    candidate["parameters"].update({"left": shared, "right": shared})

    assert len(candidate_fingerprint(candidate)) == 64


def test_excessively_deep_candidate_fails_closed() -> None:
    candidate = bounded_candidate()
    nested: dict = {}
    candidate["parameters"]["nested"] = nested
    for _ in range(40):
        child: dict = {}
        nested["child"] = child
        nested = child

    with pytest.raises(CaseValidationError, match="nesting depth"):
        candidate_fingerprint(candidate)


def test_oversized_candidate_string_fails_closed() -> None:
    candidate = bounded_candidate()
    candidate["parameters"]["payload"] = "x" * 65_537

    with pytest.raises(CaseValidationError, match="65,536 bytes"):
        candidate_fingerprint(candidate)


def test_candidate_member_and_total_node_counts_are_bounded() -> None:
    too_many_parameters = bounded_candidate()
    too_many_parameters["parameters"] = {
        f"key-{index}": index for index in range(10_001)
    }
    too_many_nodes = bounded_candidate()
    too_many_nodes["parameters"]["items"] = [None] * 10_000

    with pytest.raises(CaseValidationError, match="member count"):
        candidate_fingerprint(too_many_parameters)
    with pytest.raises(CaseValidationError, match="node count"):
        candidate_fingerprint(too_many_nodes)


def test_candidate_rejects_oversized_keys_and_integers() -> None:
    oversized_key = bounded_candidate()
    oversized_key["parameters"] = {"x" * 65_537: 1}
    oversized_integer = bounded_candidate()
    oversized_integer["parameters"]["value"] = 1 << 4_096

    with pytest.raises(CaseValidationError, match="mapping key"):
        candidate_fingerprint(oversized_key)
    with pytest.raises(CaseValidationError, match="integer exceeds"):
        candidate_fingerprint(oversized_integer)


def test_candidate_total_string_budget_is_bounded() -> None:
    candidate = bounded_candidate()
    candidate["parameters"] = {f"field-{index}": "x" * 60_000 for index in range(20)}

    with pytest.raises(CaseValidationError, match="total string budget"):
        candidate_fingerprint(candidate)

    candidate["parameters"] = {
        (f"{index:02d}" + "k" * 59_998): index for index in range(20)
    }
    with pytest.raises(CaseValidationError, match="total string budget"):
        candidate_fingerprint(candidate)


def test_case_list_sizes_are_bounded_before_normalization() -> None:
    case = payment_case()
    case["evidence_roots"] = [f"E-{index}" for index in range(10_001)]

    with pytest.raises(CaseValidationError, match="member count"):
        normalize_case(case)


def test_case_action_count_and_structural_string_sizes_are_bounded() -> None:
    too_many_actions = payment_case()
    too_many_actions["actions"] = [too_many_actions["actions"][0]] * 10_001
    oversized_name = payment_case()
    oversized_name["name"] = "x" * 65_537

    with pytest.raises(CaseValidationError, match="member count"):
        normalize_case(too_many_actions)
    with pytest.raises(CaseValidationError, match="65,536 bytes"):
        normalize_case(oversized_name)


def test_target_mutation_changes_candidate_fingerprint() -> None:
    original = bounded_candidate()
    changed = deepcopy(original)
    changed["target"] = "processor_c"

    assert candidate_fingerprint(original) != candidate_fingerprint(changed)


def test_candidate_missing_exact_action_fields_is_rejected() -> None:
    incomplete = bounded_candidate()
    del incomplete["parameters"]

    with pytest.raises(CaseValidationError):
        candidate_fingerprint(incomplete)


def test_non_string_mapping_keys_are_rejected_before_hashing() -> None:
    candidate = bounded_candidate()
    candidate["parameters"] = {"region": "US", 40: "traffic_pct"}

    with pytest.raises(CaseValidationError, match="keys must be strings"):
        candidate_fingerprint(candidate)


@pytest.mark.parametrize("invalid_number", [float("nan"), float("inf")])
def test_non_finite_numbers_are_rejected(invalid_number: float) -> None:
    candidate = bounded_candidate()
    candidate["parameters"]["traffic_pct"] = invalid_number

    with pytest.raises(CaseValidationError, match="finite number"):
        candidate_fingerprint(candidate)


def test_unsupported_runtime_objects_are_rejected() -> None:
    candidate = bounded_candidate()
    candidate["parameters"]["region"] = {"US"}

    with pytest.raises(CaseValidationError, match="unsupported value type"):
        candidate_fingerprint(candidate)


def test_case_identity_is_not_payment_specific() -> None:
    loss_leader_case = {
        "name": "hypothetical_loss_leader",
        "objective": {
            "primary": "follow the currently authorized category strategy",
            "protected_outcomes": ["authorized_strategy"],
            "anti_objectives": ["unauthorized_objective_substitution"],
        },
        "evidence_roots": ["variants/"],
        "constraints": ["candidate_must_align_with_authorized_strategy"],
        "actions": [
            {
                "id": "double_sku_price",
                "consequence": "C2",
                "reversible": True,
                "authority": "pricing_director",
                "allowed_targets": ["loss-leader-sku"],
                "allowed_parameters": {"price_multiplier": [2.0]},
            }
        ],
        "verification": {"success_conditions": ["authorized_strategy_not_violated"]},
        "watch": {"reopen_conditions": ["strategy_changes"]},
    }

    fingerprint = case_fingerprint(loss_leader_case)

    assert len(fingerprint) == 64
    assert fingerprint != case_fingerprint(payment_case())


# ---------------------------------------------------------------------------
# Resolve Contract permission tests
# ---------------------------------------------------------------------------


def test_gate_values_are_the_frozen_machine_vocabulary() -> None:
    assert {value.value for value in GateValue} == {"PASS", "FAIL", "UNKNOWN"}


def test_dispositions_are_the_frozen_permission_vocabulary() -> None:
    assert {value.value for value in Disposition} == {
        "BLOCKED",
        "MORE_EVIDENCE_REQUIRED",
        "WAITING_HUMAN",
        "ADMISSIBLE",
    }


def test_all_eight_gates_are_always_returned() -> None:
    result = evaluate_contract(valid_decision_input())

    assert set(result.gates) == {
        "intent",
        "evidence",
        "constraints",
        "consequence",
        "reversibility",
        "rehearsal",
        "authority",
        "verification",
    }
    assert all(value is GateValue.PASS for value in result.gates.values())


def test_all_pass_with_human_required_waits_for_human() -> None:
    result = evaluate_contract(valid_decision_input())

    assert result.disposition is Disposition.WAITING_HUMAN
    assert result.reason_codes == ()


def test_all_pass_without_human_requirement_is_admissible() -> None:
    decision = valid_decision_input(human_approval_required=False)

    assert evaluate_contract(decision).disposition is Disposition.ADMISSIBLE


def test_any_gate_failure_blocks() -> None:
    decision = valid_decision_input(
        hard_constraint_violations=("PROCESSOR_B_GLOBAL_NOT_AUTHORIZED",)
    )
    result = evaluate_contract(decision)

    assert result.gates["constraints"] is GateValue.FAIL
    assert result.disposition is Disposition.BLOCKED
    assert "HARD_CONSTRAINT_VIOLATION" in result.reason_codes


def test_material_unknown_requests_more_evidence() -> None:
    partial_evidence = frozenset({"E01", "E05"})
    decision = valid_decision_input(
        available_evidence_ids=partial_evidence,
        candidate_evidence_ids=partial_evidence,
    )
    result = evaluate_contract(decision)

    assert result.gates["evidence"] is GateValue.UNKNOWN
    assert result.disposition is Disposition.MORE_EVIDENCE_REQUIRED
    assert "MISSING_REQUIRED_EVIDENCE" in result.reason_codes


def test_failure_takes_precedence_over_unknown() -> None:
    decision = valid_decision_input(
        available_evidence_ids=frozenset({"E01"}),
        candidate_evidence_ids=frozenset({"E01"}),
        hard_constraint_violations=("GLOBAL_FAILOVER_NOT_AUTHORIZED",),
    )
    result = evaluate_contract(decision)

    assert result.gates["evidence"] is GateValue.UNKNOWN
    assert result.gates["constraints"] is GateValue.FAIL
    assert result.disposition is Disposition.BLOCKED


@pytest.mark.parametrize(
    ("authorized", "candidate", "expected", "reason"),
    [
        (None, "maximize_sku_margin", GateValue.UNKNOWN, "OBJECTIVE_MISSING"),
        (
            "preserve_loss_leader_strategy",
            "maximize_sku_margin",
            GateValue.FAIL,
            "OBJECTIVE_CONFLICT",
        ),
        (
            "direct_profitability",
            "direct_profitability",
            GateValue.PASS,
            None,
        ),
    ],
)
def test_intent_gate_supports_loss_leader_conformance(
    authorized: str | None,
    candidate: str,
    expected: GateValue,
    reason: str | None,
) -> None:
    decision = valid_decision_input(
        authorized_objective=authorized,
        candidate_objective=candidate,
    )
    result = evaluate_contract(decision)

    assert result.gates["intent"] is expected
    if reason is not None:
        assert reason in result.reason_codes


def test_missing_candidate_objective_makes_intent_unknown() -> None:
    result = evaluate_contract(valid_decision_input(candidate_objective=None))

    assert result.gates["intent"] is GateValue.UNKNOWN
    assert "OBJECTIVE_MISSING" in result.reason_codes


def test_unknown_evidence_reference_is_a_hard_failure() -> None:
    decision = valid_decision_input(
        candidate_evidence_ids=frozenset({"E01", "E05", "E99"})
    )
    result = evaluate_contract(decision)

    assert result.gates["evidence"] is GateValue.FAIL
    assert result.disposition is Disposition.BLOCKED
    assert "INVALID_EVIDENCE_REFERENCE" in result.reason_codes


def test_weaker_evidence_never_increases_autonomy() -> None:
    complete = evaluate_contract(valid_decision_input())
    weakened = evaluate_contract(
        valid_decision_input(
            available_evidence_ids=frozenset({"E01"}),
            candidate_evidence_ids=frozenset({"E01"}),
        )
    )

    assert complete.disposition is Disposition.WAITING_HUMAN
    assert weakened.disposition is Disposition.MORE_EVIDENCE_REQUIRED


def test_constraints_are_unknown_until_checked() -> None:
    result = evaluate_contract(valid_decision_input(constraints_checked=False))

    assert result.gates["constraints"] is GateValue.UNKNOWN
    assert "CONSTRAINTS_NOT_CHECKED" in result.reason_codes


@pytest.mark.parametrize(
    ("consequence_class", "assessed", "expected_reason"),
    [
        (None, False, "CONSEQUENCE_UNKNOWN"),
        ("C2", False, "CONSEQUENCE_NOT_ASSESSED"),
    ],
)
def test_consequence_requires_classification_and_assessment(
    consequence_class: str | None,
    assessed: bool,
    expected_reason: str,
) -> None:
    decision = valid_decision_input(
        consequence_class=consequence_class,
        consequence_assessed=assessed,
    )
    result = evaluate_contract(decision)

    assert result.gates["consequence"] is GateValue.UNKNOWN
    assert expected_reason in result.reason_codes


@pytest.mark.parametrize(
    ("required", "confirmed", "expected", "reason"),
    [
        (False, None, GateValue.PASS, None),
        (True, None, GateValue.UNKNOWN, "REVERSIBILITY_UNKNOWN"),
        (True, False, GateValue.FAIL, "REVERSIBILITY_REQUIRED"),
        (True, True, GateValue.PASS, None),
    ],
)
def test_reversibility_gate(
    required: bool,
    confirmed: bool | None,
    expected: GateValue,
    reason: str | None,
) -> None:
    decision = valid_decision_input(
        reversibility_required=required,
        reversibility_confirmed=confirmed,
    )
    result = evaluate_contract(decision)

    assert result.gates["reversibility"] is expected
    if reason is not None:
        assert reason in result.reason_codes


@pytest.mark.parametrize(
    ("required", "passed", "expected", "reason"),
    [
        (False, None, GateValue.PASS, None),
        (True, None, GateValue.UNKNOWN, "REHEARSAL_MISSING"),
        (True, False, GateValue.FAIL, "REHEARSAL_FAILED"),
        (True, True, GateValue.PASS, None),
    ],
)
def test_rehearsal_gate(
    required: bool,
    passed: bool | None,
    expected: GateValue,
    reason: str | None,
) -> None:
    decision = valid_decision_input(
        rehearsal_required=required,
        rehearsal_passed=passed,
    )
    result = evaluate_contract(decision)

    assert result.gates["rehearsal"] is expected
    if reason is not None:
        assert reason in result.reason_codes


@pytest.mark.parametrize(
    ("required_authority", "requested_role", "expected", "reason"),
    [
        (None, None, GateValue.UNKNOWN, "AUTHORITY_UNKNOWN"),
        (
            "incident_commander",
            None,
            GateValue.UNKNOWN,
            "AUTHORITY_UNKNOWN",
        ),
        (
            "incident_commander",
            "automated_agent",
            GateValue.FAIL,
            "AUTHORITY_MISMATCH",
        ),
        (
            "incident_commander",
            "incident_commander",
            GateValue.PASS,
            None,
        ),
    ],
)
def test_authority_gate_identifies_the_correct_approval_route(
    required_authority: str | None,
    requested_role: str | None,
    expected: GateValue,
    reason: str | None,
) -> None:
    decision = valid_decision_input(
        required_authority=required_authority,
        requested_approver_role=requested_role,
    )
    result = evaluate_contract(decision)

    assert result.gates["authority"] is expected
    if reason is not None:
        assert reason in result.reason_codes


@pytest.mark.parametrize(
    ("possible", "expected", "reason"),
    [
        (None, GateValue.UNKNOWN, "VERIFICATION_UNKNOWN"),
        (False, GateValue.FAIL, "VERIFICATION_IMPOSSIBLE"),
        (True, GateValue.PASS, None),
    ],
)
def test_verification_gate_requires_observable_post_action_state(
    possible: bool | None,
    expected: GateValue,
    reason: str | None,
) -> None:
    result = evaluate_contract(valid_decision_input(verification_possible=possible))

    assert result.gates["verification"] is expected
    if reason is not None:
        assert reason in result.reason_codes


def test_evaluation_is_deterministic_and_does_not_mutate_input() -> None:
    decision = valid_decision_input()
    before = asdict(decision)

    first = evaluate_contract(decision)
    second = evaluate_contract(decision)

    assert first == second
    assert asdict(decision) == before


def test_contract_result_serializes_to_the_shared_interface() -> None:
    result = evaluate_contract(valid_decision_input())

    assert result.to_dict() == {
        "gates": {
            "intent": "PASS",
            "evidence": "PASS",
            "constraints": "PASS",
            "consequence": "PASS",
            "reversibility": "PASS",
            "rehearsal": "PASS",
            "authority": "PASS",
            "verification": "PASS",
        },
        "disposition": "WAITING_HUMAN",
        "reason_codes": [],
    }


def test_decision_input_is_immutable() -> None:
    decision = valid_decision_input()

    with pytest.raises((AttributeError, TypeError)):
        decision.constraints_checked = False


def test_model_cannot_supply_a_permission_disposition() -> None:
    values = asdict(valid_decision_input())
    values["model_disposition"] = "ADMISSIBLE"

    with pytest.raises(TypeError):
        DecisionInput(**values)


def test_model_cannot_supply_permission_producing_policy_facts() -> None:
    with pytest.raises(TypeError):
        build_decision_input(
            raw_case=payment_case(),
            candidate={
                "action_type": "payments.failover",
                "target": "processor_b",
                "parameters": {"region": "GLOBAL", "traffic_pct": 100},
            },
            authorized_objective="restore_payments_with_regional_compliance",
            candidate_objective="restore_payments_with_regional_compliance",
            required_evidence_ids=frozenset({"E01"}),
            available_evidence_ids=frozenset({"E01"}),
            candidate_evidence_ids=frozenset({"E01"}),
            consequence_assessed=True,
            reversibility_confirmed=True,
            rehearsal_passed=True,
            requested_approver_role="incident_commander",
            verification_possible=True,
            constraints_checked=True,
            hard_constraint_violations=(),
            human_approval_required=False,
        )


@pytest.mark.parametrize(
    "changes",
    [
        {"case_fingerprint": "not-a-sha256"},
        {"candidate_fingerprint": ""},
        {"authorized_objective": "   "},
        {"authorized_objective": "x" * 4_097},
        {"required_evidence_ids": frozenset({""})},
        {"required_evidence_ids": frozenset({"x" * 4_097})},
        {"required_evidence_ids": frozenset(f"E-{index}" for index in range(10_001))},
        {
            "required_evidence_ids": frozenset(
                f"{index:04d}" + "x" * 3_996 for index in range(300)
            )
        },
        {"available_evidence_ids": {"E01"}},
        {"consequence_class": "CRITICAL"},
        {"constraints_checked": "yes"},
        {"hard_constraint_violations": ["VIOLATION"]},
        {"hard_constraint_violations": ("",)},
        {"hard_constraint_violations": ("x" * 4_097,)},
        {
            "hard_constraint_violations": tuple(
                f"{index:04d}" + "x" * 3_996 for index in range(300)
            )
        },
        {"reversibility_confirmed": "yes"},
        {"human_approval_required": 1},
    ],
)
def test_invalid_decision_input_is_rejected(changes: dict[str, object]) -> None:
    with pytest.raises(DecisionValidationError):
        valid_decision_input(**changes)


def test_contract_rejects_non_decision_input() -> None:
    with pytest.raises(DecisionValidationError, match="DecisionInput"):
        evaluate_contract({})


def test_contract_has_no_mongodb_or_persistence_imports() -> None:
    source = inspect.getsource(contract_module)
    tree = ast.parse(source)
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module)

    assert not any(
        name == "pymongo" or name.startswith("pymongo.") or "mongo_store" in name
        for name in imported_modules
    )


def test_candidate_mutation_changes_identity_before_contract_re_evaluation() -> None:
    approved = bounded_candidate()
    mutated = deepcopy(approved)
    mutated["parameters"]["region"] = "GLOBAL"
    mutated["parameters"]["traffic_pct"] = 100

    original_input = valid_decision_input()
    mutated_input = valid_decision_input(candidate=mutated)

    assert original_input.candidate_fingerprint != mutated_input.candidate_fingerprint
    assert mutated_input.hard_constraint_violations == (
        "PARAMETER_NOT_AUTHORIZED:region",
        "PARAMETER_NOT_AUTHORIZED:traffic_pct",
    )
    assert evaluate_contract(mutated_input).disposition is Disposition.BLOCKED


def test_action_missing_from_case_is_blocked() -> None:
    candidate = bounded_candidate()
    candidate["action_type"] = "payments.unapproved_action"

    decision = valid_decision_input(candidate=candidate)

    assert decision.hard_constraint_violations == ("ACTION_NOT_AUTHORIZED",)
    assert evaluate_contract(decision).disposition is Disposition.BLOCKED


@pytest.mark.parametrize(
    "unauthorized_target",
    [
        "processor_c",
        "PROCESSOR_B",
        "processor_b ",
        "processor_\N{CYRILLIC SMALL LETTER A}",
    ],
)
def test_candidate_target_must_be_explicitly_authorized(
    unauthorized_target: str,
) -> None:
    candidate = bounded_candidate()
    candidate["target"] = unauthorized_target

    decision = valid_decision_input(candidate=candidate)

    assert "TARGET_NOT_AUTHORIZED" in decision.hard_constraint_violations
    assert evaluate_contract(decision).disposition is Disposition.BLOCKED


def test_missing_target_policy_fails_closed_to_unknown() -> None:
    case = payment_case()
    del case["actions"][0]["allowed_targets"]

    decision = valid_decision_input(raw_case=case)

    assert decision.constraints_checked is False
    assert evaluate_contract(decision).disposition is Disposition.MORE_EVIDENCE_REQUIRED


@pytest.mark.parametrize(
    "path",
    [
        ("constraints",),
        ("actions", 0, "allowed_targets"),
    ],
)
def test_policy_identifier_lists_reject_duplicates(path: tuple) -> None:
    case = payment_case()
    cursor = case
    for key in path:
        cursor = cursor[key]
    cursor.append(cursor[0])

    with pytest.raises(CaseValidationError, match="duplicate"):
        normalize_case(case)


def test_additional_candidate_context_remains_bound_to_identity() -> None:
    candidate = bounded_candidate()
    original_fingerprint = candidate_fingerprint(candidate)
    candidate["force"] = True

    assert candidate_fingerprint(candidate) != original_fingerprint


def test_candidate_parameter_set_must_exactly_match_case_policy() -> None:
    candidate = bounded_candidate()
    del candidate["parameters"]["traffic_pct"]

    decision = valid_decision_input(candidate=candidate)

    assert "PARAMETER_SET_NOT_AUTHORIZED" in decision.hard_constraint_violations
    assert evaluate_contract(decision).disposition is Disposition.BLOCKED


@pytest.mark.parametrize("traffic_pct", ["40", 0])
def test_candidate_parameter_range_rejects_wrong_type_or_low_value(
    traffic_pct: object,
) -> None:
    candidate = bounded_candidate()
    candidate["parameters"]["traffic_pct"] = traffic_pct

    decision = valid_decision_input(candidate=candidate)

    assert "PARAMETER_NOT_AUTHORIZED:traffic_pct" in (
        decision.hard_constraint_violations
    )


def test_scalar_allowed_parameter_rule_is_supported() -> None:
    case = payment_case()
    case["actions"][0]["allowed_parameters"]["region"] = "US"

    decision = valid_decision_input(raw_case=case)

    assert decision.hard_constraint_violations == ()


@pytest.mark.parametrize(
    ("traffic_pct", "allowed"),
    [(40, False), (100, True), (101, False), (True, False)],
)
def test_two_number_list_is_an_exact_enum(traffic_pct: object, allowed: bool) -> None:
    case = payment_case()
    case["actions"][0]["allowed_parameters"]["traffic_pct"] = [0, 100]
    candidate = bounded_candidate()
    candidate["parameters"]["traffic_pct"] = traffic_pct

    decision = valid_decision_input(raw_case=case, candidate=candidate)

    assert (not decision.hard_constraint_violations) is allowed


@pytest.mark.parametrize(
    ("region", "allowed"),
    [
        ("US", True),
        ("us", False),
        ("US\n", False),
        ("ＵＳ", False),
        ("US\x00", False),
    ],
)
def test_parameter_enums_reject_case_whitespace_and_unicode_confusables(
    region: str, allowed: bool
) -> None:
    candidate = bounded_candidate()
    candidate["parameters"]["region"] = region

    decision = valid_decision_input(candidate=candidate)

    assert (not decision.hard_constraint_violations) is allowed


@pytest.mark.parametrize(
    ("rule", "value", "allowed"),
    [
        ([True], True, True),
        ([True], 1, False),
        (2.0, 2.0, True),
        (2.0, 2, False),
    ],
)
def test_enum_and_scalar_rules_do_not_collapse_boolean_or_numeric_types(
    rule: object, value: object, allowed: bool
) -> None:
    case = payment_case()
    case["actions"][0]["allowed_parameters"]["region"] = rule
    candidate = bounded_candidate()
    candidate["parameters"]["region"] = value

    decision = valid_decision_input(raw_case=case, candidate=candidate)

    assert (not decision.hard_constraint_violations) is allowed


@pytest.mark.parametrize("unknown_rule", [{}, {"pattern": "US"}])
def test_unknown_parameter_rule_fails_to_more_evidence(unknown_rule: dict) -> None:
    case = payment_case()
    case["actions"][0]["allowed_parameters"]["region"] = unknown_rule

    decision = valid_decision_input(raw_case=case)
    result = evaluate_contract(decision)

    assert decision.constraints_checked is False
    assert result.disposition is Disposition.MORE_EVIDENCE_REQUIRED


def test_invalid_case_policy_flags_fail_closed() -> None:
    case = payment_case()
    case["actions"][0]["human_approval_required"] = "no"

    with pytest.raises(DecisionValidationError, match="must be booleans"):
        valid_decision_input(raw_case=case)


def test_consequence_policy_cannot_disable_required_human_approval() -> None:
    low_case = payment_case()
    low_case["actions"][0]["consequence"] = "C1"
    high_case = payment_case()
    high_case["actions"][0]["consequence"] = "C3"
    high_case["actions"][0]["human_approval_required"] = False

    low = valid_decision_input(raw_case=low_case)
    high = valid_decision_input(raw_case=high_case)

    assert low.human_approval_required is False
    assert high.human_approval_required is True
    assert evaluate_contract(high).disposition is Disposition.WAITING_HUMAN


def test_evidence_receipt_fingerprints_validated_content_not_only_ids() -> None:
    first = build_evidence_receipt(
        evidence_registry={"E01": "1" * 64},
        required_evidence_ids=frozenset({"E01"}),
        candidate_evidence_ids=frozenset({"E01"}),
    )
    changed = build_evidence_receipt(
        evidence_registry={"E01": "2" * 64},
        required_evidence_ids=frozenset({"E01"}),
        candidate_evidence_ids=frozenset({"E01"}),
    )

    assert first.evidence_fingerprint != changed.evidence_fingerprint
    assert first.available_evidence_ids == frozenset({"E01"})


def test_objective_receipt_derives_authorized_objective_from_trusted_validator() -> (
    None
):
    evidence = build_evidence_receipt(
        evidence_registry={"E-STRATEGY": "e" * 64},
        required_evidence_ids=frozenset({"E-STRATEGY"}),
        candidate_evidence_ids=frozenset({"E-STRATEGY"}),
    )
    receipt = build_objective_receipt(
        raw_case=payment_case(),
        evidence_receipt=evidence,
        candidate_objective="restore_payments_with_regional_compliance",
        validator=lambda _case, _evidence: "restore_payments_with_regional_compliance",
    )

    assert receipt.authorized_objective == "restore_payments_with_regional_compliance"
    assert receipt.evidence_fingerprint == evidence.evidence_fingerprint


def test_objective_receipt_is_bound_to_evidence_snapshot() -> None:
    decision_args = receipt_builder_kwargs()
    evidence = build_evidence_receipt(
        evidence_registry={"E01": "9" * 64},
        required_evidence_ids=frozenset({"E01"}),
        candidate_evidence_ids=frozenset({"E01"}),
    )

    with pytest.raises(DecisionValidationError, match="objective receipt"):
        build_decision_input(**{**decision_args, "evidence_receipt": evidence})


def test_model_shaped_objective_receipt_is_rejected() -> None:
    with pytest.raises(DecisionValidationError, match="ObjectiveReceipt"):
        build_decision_input(
            **receipt_builder_kwargs(objective_receipt=ObjectiveReceipt())
        )


def test_objective_receipt_rejects_untrusted_validator_boundaries() -> None:
    evidence = receipt_builder_kwargs()["evidence_receipt"]
    with pytest.raises(DecisionValidationError, match="raw_case"):
        build_objective_receipt(
            raw_case=[],
            evidence_receipt=evidence,
            candidate_objective="candidate",
            validator=lambda _case, _evidence: "authorized",
        )
    with pytest.raises(DecisionValidationError, match="EvidenceReceipt"):
        build_objective_receipt(
            raw_case=payment_case(),
            evidence_receipt=EvidenceReceipt(),
            candidate_objective="candidate",
            validator=lambda _case, _evidence: "authorized",
        )
    with pytest.raises(DecisionValidationError, match="callable"):
        build_objective_receipt(
            raw_case=payment_case(),
            evidence_receipt=evidence,
            candidate_objective="candidate",
            validator=True,
        )


def test_objective_validator_failure_or_invalid_result_fails_closed() -> None:
    evidence = receipt_builder_kwargs()["evidence_receipt"]

    def broken_validator(_case, _evidence):
        raise RuntimeError("strategy registry unavailable")

    with pytest.raises(DecisionValidationError, match="failed"):
        build_objective_receipt(
            raw_case=payment_case(),
            evidence_receipt=evidence,
            candidate_objective="candidate",
            validator=broken_validator,
        )
    with pytest.raises(DecisionValidationError, match="authorized_objective"):
        build_objective_receipt(
            raw_case=payment_case(),
            evidence_receipt=evidence,
            candidate_objective="candidate",
            validator=lambda _case, _evidence: " ",
        )


def receipt_builder_kwargs(**changes: object) -> dict[str, object]:
    """Return the fully bound trusted-receipt builder interface for edge tests."""

    case = payment_case()
    candidate = bounded_candidate()
    evidence = build_evidence_receipt(
        evidence_registry={"E01": "1" * 64},
        required_evidence_ids=frozenset({"E01"}),
        candidate_evidence_ids=frozenset({"E01"}),
    )
    values: dict[str, object] = {
        "raw_case": case,
        "candidate": candidate,
        "objective_receipt": build_objective_receipt(
            raw_case=case,
            evidence_receipt=evidence,
            candidate_objective="restore_payments_with_regional_compliance",
            validator=lambda _case, _evidence: (
                "restore_payments_with_regional_compliance"
            ),
        ),
        "evidence_receipt": evidence,
        "constraint_receipt": build_constraint_validation_receipt(
            raw_case=case,
            candidate=candidate,
            validators=passing_constraint_validators(case),
        ),
        "state_fingerprint": STATE_FINGERPRINT,
        "consequence_assessed": True,
        "reversibility_confirmed": True,
        "rehearsal_receipt": build_rehearsal_receipt(
            candidate=candidate,
            state_fingerprint=STATE_FINGERPRINT,
            passed=True,
        ),
        "requested_approver_role": "incident_commander",
        "verification_receipt": build_verification_receipt(
            candidate=candidate,
            state_fingerprint=STATE_FINGERPRINT,
            possible=True,
        ),
    }
    values.update(changes)
    return values


@pytest.mark.parametrize(
    "invalid_registry",
    [[], {1: "1" * 64}, {"E01": "invalid"}],
)
def test_evidence_receipt_rejects_malformed_registry(invalid_registry: object) -> None:
    with pytest.raises(DecisionValidationError):
        build_evidence_receipt(
            evidence_registry=invalid_registry,
            required_evidence_ids=frozenset({"E01"}),
            candidate_evidence_ids=frozenset({"E01"}),
        )


@pytest.mark.parametrize(
    "violations",
    [
        ["not-a-tuple"],
        ("",),
        tuple(f"V-{index}" for index in range(10_001)),
        ("x" * 4_097,),
    ],
)
def test_constraint_receipt_rejects_malformed_violation_codes(
    violations: object,
) -> None:
    with pytest.raises(DecisionValidationError):
        build_constraint_validation_receipt(
            raw_case=payment_case(),
            candidate=bounded_candidate(),
            validators={
                payment_case()["constraints"][0]: lambda _case, _candidate: violations
            },
        )


def test_constraint_receipt_rejects_unknown_constraint_id() -> None:
    with pytest.raises(DecisionValidationError, match="unknown constraint ID"):
        build_constraint_validation_receipt(
            raw_case=payment_case(),
            candidate=bounded_candidate(),
            validators={"not-in-the-case": lambda _case, _candidate: ()},
        )


@pytest.mark.parametrize(
    "validators",
    [
        [],
        {1: lambda _case, _candidate: ()},
        {"processor_b_only_for_eligible_bounded_traffic": True},
    ],
)
def test_constraint_receipt_requires_trusted_callable_registry(
    validators: object,
) -> None:
    with pytest.raises(DecisionValidationError, match="validator"):
        build_constraint_validation_receipt(
            raw_case=payment_case(),
            candidate=bounded_candidate(),
            validators=validators,
        )


def test_constraint_validator_failure_is_stable_and_fails_closed() -> None:
    def broken_validator(_case, _candidate):
        raise RuntimeError("validator dependency unavailable")

    with pytest.raises(DecisionValidationError, match="failed"):
        build_constraint_validation_receipt(
            raw_case=payment_case(),
            candidate=bounded_candidate(),
            validators={
                "processor_b_only_for_eligible_bounded_traffic": broken_validator
            },
        )


def test_constraint_validator_mutation_invalidates_its_own_receipt() -> None:
    candidate = bounded_candidate()
    original_fingerprint = candidate_fingerprint(candidate)

    def mutating_validator(_case, checked_candidate):
        checked_candidate["parameters"]["traffic_pct"] = 20
        return ()

    receipt = build_constraint_validation_receipt(
        raw_case=payment_case(),
        candidate=candidate,
        validators={
            "processor_b_only_for_eligible_bounded_traffic": mutating_validator
        },
    )

    assert receipt.candidate_fingerprint == original_fingerprint
    with pytest.raises(DecisionValidationError, match="constraint receipt"):
        build_decision_input(
            **receipt_builder_kwargs(
                candidate=candidate,
                constraint_receipt=receipt,
                rehearsal_receipt=None,
                verification_receipt=None,
            )
        )


def test_named_constraint_semantics_are_executed_not_only_declared() -> None:
    case = payment_case()
    case["constraints"] = ["traffic_pct_must_be_zero"]
    candidate = bounded_candidate()

    def traffic_must_be_zero(_case, checked_candidate):
        if checked_candidate["parameters"]["traffic_pct"] != 0:
            return ("TRAFFIC_MUST_BE_ZERO",)
        return ()

    receipt = build_constraint_validation_receipt(
        raw_case=case,
        candidate=candidate,
        validators={"traffic_pct_must_be_zero": traffic_must_be_zero},
    )
    decision_args = receipt_builder_kwargs(
        raw_case=case,
        candidate=candidate,
        constraint_receipt=receipt,
    )
    evidence = decision_args["evidence_receipt"]
    decision_args["objective_receipt"] = build_objective_receipt(
        raw_case=case,
        evidence_receipt=evidence,
        candidate_objective="restore_payments_with_regional_compliance",
        validator=lambda _case, _evidence: "restore_payments_with_regional_compliance",
    )
    decision = build_decision_input(**decision_args)

    assert decision.hard_constraint_violations == ("TRAFFIC_MUST_BE_ZERO",)
    assert evaluate_contract(decision).disposition is Disposition.BLOCKED


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"constraint_receipt": None}, None),
        ({"constraint_receipt": ConstraintValidationReceipt()}, "constraint_receipt"),
        ({"rehearsal_receipt": RehearsalReceipt()}, "rehearsal_receipt"),
        ({"verification_receipt": None}, None),
        ({"verification_receipt": VerificationReceipt()}, "verification_receipt"),
    ],
)
def test_missing_or_unvalidated_receipts_fail_closed(
    changes: dict[str, object], message: str | None
) -> None:
    if message is not None:
        with pytest.raises(DecisionValidationError, match=message):
            build_decision_input(**receipt_builder_kwargs(**changes))
        return

    decision = build_decision_input(**receipt_builder_kwargs(**changes))
    result = evaluate_contract(decision)
    assert result.disposition is Disposition.MORE_EVIDENCE_REQUIRED


def test_rehearsal_can_be_absent_only_as_an_unknown_gate() -> None:
    decision = build_decision_input(**receipt_builder_kwargs(rehearsal_receipt=None))

    assert evaluate_contract(decision).gates["rehearsal"] is GateValue.UNKNOWN


def test_receipt_builders_reject_invalid_state_and_boolean_types() -> None:
    with pytest.raises(DecisionValidationError, match="state_fingerprint"):
        build_rehearsal_receipt(
            candidate=bounded_candidate(), state_fingerprint="invalid", passed=True
        )
    with pytest.raises(DecisionValidationError, match="boolean"):
        build_verification_receipt(
            candidate=bounded_candidate(),
            state_fingerprint=STATE_FINGERPRINT,
            possible="yes",
        )


def test_receipt_dataclasses_cannot_be_constructed_from_model_mappings() -> None:
    for receipt_type in (
        EvidenceReceipt,
        ObjectiveReceipt,
        ConstraintValidationReceipt,
        RehearsalReceipt,
        VerificationReceipt,
    ):
        assert not hasattr(receipt_type(), "_validated")

    with pytest.raises(DecisionValidationError, match="EvidenceReceipt"):
        build_decision_input(
            **receipt_builder_kwargs(evidence_receipt=EvidenceReceipt())
        )


def test_constraint_receipt_is_bound_to_exact_case_and_candidate() -> None:
    original = bounded_candidate()
    receipt = build_constraint_validation_receipt(
        raw_case=payment_case(),
        candidate=original,
        validators=passing_constraint_validators(payment_case()),
    )
    mutated = bounded_candidate()
    mutated["parameters"]["region"] = "GLOBAL"

    with pytest.raises(DecisionValidationError, match="constraint receipt"):
        build_decision_input(
            **receipt_builder_kwargs(
                candidate=mutated,
                constraint_receipt=receipt,
                rehearsal_receipt=None,
                verification_receipt=None,
            )
        )


def test_missing_constraint_receipt_cannot_pass_constraints() -> None:
    decision = valid_decision_input()
    object.__setattr__(decision, "constraints_checked", False)

    result = evaluate_contract(decision)

    assert result.gates["constraints"] is GateValue.UNKNOWN
    assert result.disposition is Disposition.MORE_EVIDENCE_REQUIRED


@pytest.mark.parametrize("receipt_kind", ["rehearsal", "verification"])
def test_runtime_receipts_are_bound_to_candidate_and_state(receipt_kind: str) -> None:
    candidate = bounded_candidate()
    other_candidate = deepcopy(candidate)
    other_candidate["parameters"]["traffic_pct"] = 20
    if receipt_kind == "rehearsal":
        receipt = build_rehearsal_receipt(
            candidate=other_candidate,
            state_fingerprint=STATE_FINGERPRINT,
            passed=True,
        )
        changes = {"rehearsal_receipt": receipt, "verification_receipt": None}
    else:
        receipt = build_verification_receipt(
            candidate=other_candidate,
            state_fingerprint=STATE_FINGERPRINT,
            possible=True,
        )
        changes = {"rehearsal_receipt": None, "verification_receipt": receipt}

    with pytest.raises(DecisionValidationError, match=f"{receipt_kind} receipt"):
        build_decision_input(**receipt_builder_kwargs(candidate=candidate, **changes))


def test_decision_fingerprint_binds_evidence_state_and_all_permission_facts() -> None:
    original = valid_decision_input()
    changed_state = valid_decision_input()
    object.__setattr__(changed_state, "state_fingerprint", "d" * 64)
    changed_evidence = valid_decision_input()
    object.__setattr__(changed_evidence, "evidence_fingerprint", "e" * 64)
    changed_rehearsal = valid_decision_input()
    object.__setattr__(changed_rehearsal, "rehearsal_passed", False)

    fingerprints = {
        decision_fingerprint(original),
        decision_fingerprint(changed_state),
        decision_fingerprint(changed_evidence),
        decision_fingerprint(changed_rehearsal),
    }

    assert len(fingerprints) == 4


def test_decision_fingerprint_rejects_non_decision_input() -> None:
    with pytest.raises(DecisionValidationError, match="DecisionInput"):
        decision_fingerprint({})


def test_evaluated_decision_envelope_binds_result_to_context() -> None:
    decision = valid_decision_input()

    evaluated = evaluate_decision(decision)

    assert evaluated.decision_fingerprint == decision_fingerprint(decision)
    assert evaluated.case_fingerprint == decision.case_fingerprint
    assert evaluated.candidate_fingerprint == decision.candidate_fingerprint
    assert evaluated.evidence_fingerprint == decision.evidence_fingerprint
    assert evaluated.state_fingerprint == decision.state_fingerprint
    assert evaluated.required_authority == "incident_commander"
    assert evaluated.consequence_class == "C2"
    assert evaluated.human_approval_required is True
    assert evaluated.result.disposition is Disposition.WAITING_HUMAN
    assert evaluated.to_dict()["contract_result"]["disposition"] == "WAITING_HUMAN"


def test_high_consequence_nonreversible_action_is_blocked() -> None:
    case = payment_case()
    case["actions"][0]["reversible"] = False

    decision = valid_decision_input(raw_case=case)

    assert decision.reversibility_confirmed is False
    assert evaluate_contract(decision).disposition is Disposition.BLOCKED


def test_non_mapping_builder_inputs_fail_closed() -> None:
    with pytest.raises(DecisionValidationError, match="raw_case"):
        build_decision_input(**receipt_builder_kwargs(raw_case=[]))
    with pytest.raises(DecisionValidationError, match="candidate"):
        valid_decision_input(candidate=[])


def test_non_mapping_candidate_parameters_fail_closed() -> None:
    candidate = bounded_candidate()
    candidate["parameters"] = []

    with pytest.raises(CaseValidationError, match="candidate.parameters"):
        valid_decision_input(candidate=candidate)
