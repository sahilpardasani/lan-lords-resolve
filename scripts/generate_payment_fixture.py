#!/usr/bin/env python3
"""Generate the deterministic, causally coherent Resolve payment fixture."""

from __future__ import annotations

import hashlib
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
DATASET_ID = "resolve_payments_canonical_500_v1"
CASE_ID = "payment_failover_001"
SEED = 20260822
TOTAL = 500
WEIGHTED_VALUE_USD = 25_000
BASE_TIME = datetime(2026, 8, 22, 13, 0, tzinfo=timezone.utc)


def iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_ndjson(path: Path, values: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n" for value in values)
    path.write_text(text, encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def make_transactions() -> list[dict]:
    randomizer = random.Random(SEED)
    countries = ("US", "CA", "GB", "DE")
    networks = ("visa", "mastercard", "amex")
    transactions = []
    for number in range(1, TOTAL + 1):
        affected = 396 <= number <= 482
        if affected:
            country = "US"
            network = "visa" if number % 2 else "mastercard"
            amount = round(randomizer.uniform(20, 4_999), 2)
        elif number > 482:
            # The 18 remaining incident failures are deliberately outside the
            # Processor B network allowlist, so the admitted cohort is exactly
            # the 87 affected and policy-eligible rows rather than an arbitrary
            # subset of a larger eligible failure population.
            country = "US"
            network = "amex"
            amount = round(randomizer.uniform(20, 4_999), 2)
        else:
            country = countries[randomizer.randrange(len(countries))]
            network = networks[randomizer.randrange(len(networks))]
            amount = round(randomizer.uniform(20, 9_000), 2)

        eligible = country == "US" and network in {"visa", "mastercard"} and amount <= 5_000
        baseline_success = number <= 493
        incident_success = number <= 395
        recovery_success = number <= 482
        recovery_processor = "processor_b" if affected else "processor_a"
        started = BASE_TIME + timedelta(seconds=number - 1)

        transactions.append(
            {
                "document_type": "payment_transaction",
                "dataset_id": DATASET_ID,
                "case_id": CASE_ID,
                "cohort_transaction_id": f"PAY-{number:04d}",
                "baseline_observed_at": iso(started),
                "incident_observed_at": iso(started + timedelta(minutes=20)),
                "recovery_observed_at": iso(started + timedelta(minutes=30)),
                "country": country,
                "network": network,
                "currency": "USD",
                "amount_usd": amount,
                "weighted_payment_value_usd": WEIGHTED_VALUE_USD,
                "eligible_for_processor_b": eligible,
                "affected_cohort": affected,
                "baseline_result": "success" if baseline_success else "processing_error",
                "incident_result": "success" if incident_success else "processor_a_degradation",
                "recovery_processor": recovery_processor,
                "recovery_result": "success" if recovery_success else "processor_a_degradation",
                "routed_under_approved_action": affected,
                "policy_status": "OK",
                "classification": "synthetic_demo_data",
                "contains_actual_customer_data": False,
            }
        )
    return transactions


def main() -> None:
    canonical = ROOT / "data" / "canonical"
    mongo_import = ROOT / "data" / "mongodb" / "import"
    reference = ROOT / "data" / "mongodb" / "reference_expected_trace"
    source_dir = ROOT / "docs" / "source_material" / "original"

    transactions = make_transactions()
    write_ndjson(canonical / "payment_transactions_500.ndjson", transactions)
    write_ndjson(mongo_import / "payment_events.ndjson", transactions)

    routing_policy = {
        "document_type": "routing_policy",
        "case_id": CASE_ID,
        "policy_id": "processor_b_bounded_failover_v1",
        "processor_b": {
            "allowed_countries": ["US"],
            "allowed_networks": ["visa", "mastercard"],
            "maximum_transaction_value_usd": 5_000,
            "maximum_total_traffic_share": 0.20,
        },
        "classification": "synthetic_company_policy",
        "contains_actual_customer_data": False,
    }
    write_json(canonical / "routing_policy.json", routing_policy)

    expected_metrics = {
        "dataset_id": DATASET_ID,
        "case_id": CASE_ID,
        "total": 500,
        "baseline_success": 493,
        "baseline_success_rate": 0.986,
        "incident_success": 395,
        "incident_success_rate": 0.790,
        "incident_failures": 105,
        "processor_b_routed": 87,
        "processor_b_route_share_of_total": 0.174,
        "recovery_success": 482,
        "recovery_success_rate": 0.964,
        "remaining_recovery_failures": 18,
        "unauthorized_processor_b_routes": 0,
        "policy_violations": 0,
        "weighted_value_per_record_usd": WEIGHTED_VALUE_USD,
        "weighted_cohort_value_usd": 12_500_000,
        "affected_flow_share": 0.00005,
        "affected_value_per_minute_usd": 416_666.6666666667,
        "modeled_minutes_without_resolve": 30,
        "modeled_minutes_with_resolve": 10,
        "modeled_minutes_saved": 20,
        "modeled_payment_flow_returning_sooner_usd": 8_333_333.333333334,
        "business_value_limitation": "Payment throughput, not revenue, profit, guaranteed savings, or guaranteed avoided loss.",
        "classification": "synthetic_demo_data",
        "contains_actual_customer_data": False,
    }
    write_json(canonical / "expected_metrics.json", expected_metrics)

    source_files = []
    for name in (
        "Resolve_Payments_Real_Business_Data.xlsx",
        "resolve_mongodb_demo.ndjson",
        "Hackathon 082226.docx",
    ):
        path = source_dir / name
        source_files.append({"path": str(path.relative_to(ROOT)), "sha256": sha256(path)})
    manifest = {
        "document_type": "dataset_manifest",
        "dataset_id": DATASET_ID,
        "case_id": CASE_ID,
        "record_count": TOTAL,
        "deterministic_seed": SEED,
        "transaction_identity_rule": "PAY-0001 through PAY-0500 represent one cohort observed at baseline, incident, and recovery.",
        "weighted_value_rule": "Count each transaction identity once; alternate state observations do not multiply weighted value.",
        "source_files": source_files,
        "missing_optional_visual_reference": "resolve_enterprise_payment_live_demo.html",
        "classification": "synthetic_demo_data",
        "contains_actual_customer_data": False,
    }
    write_json(canonical / "dataset_manifest.json", manifest)

    case = yaml.safe_load((ROOT / "cases" / "primary" / "case.yaml").read_text(encoding="utf-8"))
    case_import = {
        "document_type": "case_fixture",
        "case_id": CASE_ID,
        "case": case,
        "classification": "synthetic_demo_data",
        "contains_actual_customer_data": False,
    }
    write_ndjson(mongo_import / "cases.ndjson", [case_import])

    evidence = []
    for stage in ("stage_1", "stage_2"):
        for path in sorted((ROOT / "cases" / "primary" / "evidence" / stage).glob("*.json")):
            document = json.loads(path.read_text(encoding="utf-8"))
            document["document_type"] = "evidence_fixture"
            document["case_id"] = CASE_ID
            document["stage"] = stage
            evidence.append(document)
    write_ndjson(mongo_import / "evidence.ndjson", evidence)

    expected_trace = [
        {
            "sequence": 1,
            "event": "unsafe_candidate_evaluated",
            "candidate": {"country": "GLOBAL", "traffic_share": 1.0},
            "disposition": "BLOCKED",
            "reason_codes": ["COUNTRY_NOT_ALLOWED", "TRAFFIC_CAP_EXCEEDED"],
        },
        {
            "sequence": 2,
            "event": "bounded_candidate_stage_1_evaluated",
            "candidate": {"country": "US", "networks": ["visa", "mastercard"], "maximum_transaction_value_usd": 5000, "traffic_share": 0.174},
            "disposition": "MORE_EVIDENCE_REQUIRED",
            "reason_codes": ["PROCESSOR_B_CAPACITY_STALE"],
        },
        {
            "sequence": 3,
            "event": "bounded_candidate_stage_2_evaluated",
            "disposition": "WAITING_HUMAN",
            "reason_codes": [],
        },
        {"sequence": 4, "event": "approval_expected_live", "disposition": "GENERATE_AT_RUNTIME"},
        {"sequence": 5, "event": "commit_expected_live", "disposition": "GENERATE_AT_RUNTIME"},
        {"sequence": 6, "event": "verification_expected_live", "disposition": "GENERATE_AT_RUNTIME"},
    ]
    reference_records = [
        {
            "document_type": "reference_expected_trace_step",
            "reference_only": True,
            "case_id": CASE_ID,
            "classification": "synthetic_expected_result",
            "contains_actual_customer_data": False,
            **step,
        }
        for step in expected_trace
    ]
    write_ndjson(reference / "expected_trace.ndjson", reference_records)


if __name__ == "__main__":
    main()
