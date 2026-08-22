"""
resolve/context.py  --  case + evidence loader (Coder 3)

Loads the primary payment case and its STAGED evidence. Mirrors Business 1's
frozen facts. Evidence is staged per the spec: initial evidence proves the
global failover breaks a hard rule; later evidence reveals the traffic
breakdown needed to choose the bounded 40% candidate.

Real version reads cases/primary/case.yaml + evidence/**; this holds the
same facts inline so the run works before Business 1's files land.
"""

import hashlib
import json


def _fingerprint(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def load_case() -> dict:
    case = {
        "case_id": "case_primary_payments",
        "what_happened": "Payment success dropped from baseline.",
        "objective": "restore_payment_success",
        "protected_outcomes": ["do_not_exceed_processor_b_authorization"],
        "baseline_success": 98.6,
        "current_success": 79.0,
        "hard_constraint": "processor_b_authorized_only_for_eligible_bounded_traffic",
        "approver_authority": "payments_ops_lead",
        "success_condition": "success_rate_recovers_toward_baseline",
        "verification_rule": "read_actual_simulator_state",
    }
    case["case_fingerprint"] = _fingerprint(case)
    return case


def initial_evidence() -> dict:
    """First pass: enough to show GLOBAL/100% violates the hard rule,
    but NOT yet the traffic breakdown (forces MORE_EVIDENCE_REQUIRED first)."""
    return {
        "success_rate_now": 79.0,
        "processor_b_authorization": "eligible_bounded_only",
        # traffic_breakdown intentionally absent on first pass
    }


def revealed_evidence() -> dict:
    """Second pass: reveals eligible traffic so the bounded 40% candidate
    can be chosen and pass the constraint gate."""
    ev = initial_evidence()
    ev["traffic_breakdown"] = {
        "us_eligible_pct": 40,      # Business 1: good candidate is US 40%
        "networks": ["visa", "mastercard"],
    }
    return ev
