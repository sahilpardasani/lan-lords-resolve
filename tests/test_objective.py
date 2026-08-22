"""File-backed cross-domain INTENT conformance tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from resolve.contract import (
    DecisionInput,
    Disposition,
    GateValue,
    build_constraint_validation_receipt,
    build_decision_input,
    build_evidence_receipt,
    build_objective_receipt,
    build_rehearsal_receipt,
    build_verification_receipt,
    evaluate_contract,
)

STATE_FINGERPRINT = "c" * 64

FIXTURE_ROOT = Path(__file__).parents[1] / "cases" / "conformance"


def conformance_files() -> tuple[Path, ...]:
    return tuple(sorted(FIXTURE_ROOT.glob("OBJECTIVE-*.json")))


def load_fixture(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise TypeError(f"{path.name} must contain a JSON object")
    return value


def decision_for(fixture: dict[str, Any]) -> DecisionInput:
    case = {
        "name": "loss_leader_strategy",
        "objective": {
            "primary": "apply the authorized pricing strategy",
            "protected_outcomes": ["authorized_strategy"],
            "anti_objectives": ["unauthorized_margin_optimization"],
        },
        "evidence_roots": ["strategy"],
        "constraints": ["pricing_strategy_must_be_authorized"],
        "actions": [
            {
                "id": "pricing.change",
                "consequence": "C2",
                "reversible": True,
                "authority": "pricing_director",
                "allowed_targets": ["loss-leader-sku"],
                "allowed_parameters": {"sku": ["loss-leader-sku"]},
            }
        ],
        "verification": {"success_conditions": ["price_matches_approval"]},
    }
    candidate = {
        "action_type": "pricing.change",
        "target": "loss-leader-sku",
        "parameters": {"sku": "loss-leader-sku"},
    }
    evidence = build_evidence_receipt(
        evidence_registry={"E-STRATEGY": "e" * 64},
        required_evidence_ids=frozenset({"E-STRATEGY"}),
        candidate_evidence_ids=frozenset({"E-STRATEGY"}),
    )
    return build_decision_input(
        raw_case=case,
        candidate=candidate,
        objective_receipt=build_objective_receipt(
            raw_case=case,
            evidence_receipt=evidence,
            candidate_objective=fixture["candidate_objective"],
            validator=lambda _case, _evidence: fixture["authorized_objective"],
        ),
        evidence_receipt=evidence,
        constraint_receipt=build_constraint_validation_receipt(
            raw_case=case,
            candidate=candidate,
            validators={case["constraints"][0]: lambda _case, _candidate: ()},
        ),
        state_fingerprint=STATE_FINGERPRINT,
        consequence_assessed=True,
        reversibility_confirmed=True,
        rehearsal_receipt=build_rehearsal_receipt(
            candidate=candidate,
            state_fingerprint=STATE_FINGERPRINT,
            passed=True,
        ),
        requested_approver_role="pricing_director",
        verification_receipt=build_verification_receipt(
            candidate=candidate,
            state_fingerprint=STATE_FINGERPRINT,
            possible=True,
        ),
    )


def test_all_three_objective_fixtures_are_present() -> None:
    assert [path.stem for path in conformance_files()] == [
        "OBJECTIVE-01_strategy_missing",
        "OBJECTIVE-02_loss_leader_present",
        "OBJECTIVE-03_strategy_changed",
    ]


@pytest.mark.parametrize(
    "fixture_path", conformance_files(), ids=lambda path: path.stem
)
def test_loss_leader_intent_conformance(fixture_path: Path) -> None:
    fixture = load_fixture(fixture_path)
    result = evaluate_contract(decision_for(fixture))

    assert result.gates["intent"] is GateValue(fixture["expected_intent_gate"])
    assert result.disposition is Disposition(fixture["expected_disposition"])
    expected_reason = fixture["expected_reason_code"]
    if expected_reason is not None:
        assert expected_reason in result.reason_codes


def test_intent_pass_continues_to_authority_instead_of_auto_admitting() -> None:
    fixture = load_fixture(FIXTURE_ROOT / "OBJECTIVE-03_strategy_changed.json")
    result = evaluate_contract(decision_for(fixture))

    assert result.gates["intent"] is GateValue.PASS
    assert result.disposition is Disposition.WAITING_HUMAN
