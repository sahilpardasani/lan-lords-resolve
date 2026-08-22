#!/usr/bin/env python3
"""Validate the canonical Resolve payment fixture and emit an audit receipt."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "data" / "canonical"
MONGO_IMPORT = ROOT / "data" / "mongodb" / "import"
REFERENCE_TRACE = ROOT / "data" / "mongodb" / "reference_expected_trace" / "expected_trace.ndjson"
RECEIPT = ROOT / "evidence" / "data_integrity" / "DATA_FIXTURE_RECEIPT.txt"
CASE_PATH = ROOT / "cases" / "primary" / "case.yaml"


class ValidationFailure(Exception):
    pass


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_ndjson(path):
    records = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValidationFailure(f"{path}:{line_number}: invalid JSON: {exc}") from exc
    return records


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_timestamp(value, label):
    if not isinstance(value, str):
        raise ValidationFailure(f"{label}: timestamp must be a string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationFailure(f"{label}: invalid ISO-8601 timestamp {value!r}") from exc
    if parsed.tzinfo is None:
        raise ValidationFailure(f"{label}: timestamp must include a timezone")
    return parsed


def validate_timestamps(value, label="document"):
    if isinstance(value, dict):
        for key, child in value.items():
            child_label = f"{label}.{key}"
            if key.endswith("_at") or key == "timestamp":
                parse_timestamp(child, child_label)
            else:
                validate_timestamps(child, child_label)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            validate_timestamps(child, f"{label}[{index}]")


def require(condition, message):
    if not condition:
        raise ValidationFailure(message)


def validate_case():
    raw_case = yaml.safe_load(CASE_PATH.read_text(encoding="utf-8"))
    require(isinstance(raw_case, dict), "case.yaml must parse to a mapping")
    require(raw_case.get("case_id") == "payment_failover_001", "case_id mismatch")
    require(raw_case.get("classification") == "synthetic_demo_data", "case classification missing")
    require(raw_case.get("contains_actual_customer_data") is False, "case must deny actual customer data")
    policy = raw_case["policy"]["processor_b"]
    require(policy["allowed_countries"] == ["US"], "case country policy mismatch")
    require(policy["allowed_networks"] == ["visa", "mastercard"], "case network policy mismatch")
    require(policy["maximum_transaction_value_usd"] == 5000, "case amount cap mismatch")
    require(math.isclose(policy["maximum_total_traffic_share"], 0.20), "case total traffic cap mismatch")
    require(raw_case["authority"]["human_required"] is True, "human authority rule missing")
    require(raw_case["rehearsal"]["required"] is True, "rehearsal rule missing")
    require(raw_case["verification"]["required"] is True, "verification rule missing")
    require(raw_case["retry"]["automatic_post_commit_retry"] is False, "post-commit retry must be disabled")

    sys.path.insert(0, str(ROOT))
    from resolve.case import normalize_case

    normalize_case(raw_case)
    return raw_case


def validate_evidence():
    documents = []
    for stage in ("stage_1", "stage_2"):
        directory = ROOT / "cases" / "primary" / "evidence" / stage
        for path in sorted(directory.glob("*.json")):
            document = load_json(path)
            validate_timestamps(document, str(path.relative_to(ROOT)))
            require(document.get("evidence_id"), f"{path}: evidence_id missing")
            require(document.get("source_classification"), f"{path}: source classification missing")
            require(document.get("contains_actual_customer_data") is False, f"{path}: actual customer data flag must be false")
            documents.append(document)
    evidence_ids = [document["evidence_id"] for document in documents]
    require(len(documents) == 8, "expected exactly eight staged evidence documents")
    require(len(evidence_ids) == len(set(evidence_ids)), "evidence IDs must be unique")

    stale = load_json(ROOT / "cases" / "primary" / "evidence" / "stage_1" / "processor_b_capacity_stale.json")
    require(stale["status"] == "stale" and stale["sufficient_for_admission"] is False, "stage-1 capacity evidence must be insufficient")
    require(parse_timestamp(stale["expires_at"], "stale.expires_at") < parse_timestamp(stale["retrieved_at"], "stale.retrieved_at"), "stage-1 capacity evidence must be materially stale")

    current = load_json(ROOT / "cases" / "primary" / "evidence" / "stage_2" / "processor_b_capacity_current.json")
    require(current["status"] == "current" and current["sufficient_for_admission"] is True, "stage-2 capacity evidence must be current")
    require(parse_timestamp(current["measured_at"], "current.measured_at") < parse_timestamp(current["expires_at"], "current.expires_at"), "stage-2 capacity window is invalid")

    affected = load_json(ROOT / "cases" / "primary" / "evidence" / "stage_2" / "affected_cohort.json")
    require(affected["affected_and_policy_eligible_transactions"] == 87, "affected cohort evidence count mismatch")
    require(math.isclose(affected["affected_total_traffic_share"], 0.174), "affected cohort evidence share mismatch")
    rehearsal = load_json(ROOT / "cases" / "primary" / "evidence" / "stage_2" / "rehearsal_receipt.json")
    require(rehearsal["status"] == "PASS", "rehearsal receipt must pass")
    return documents


def validate_transactions():
    path = CANONICAL / "payment_transactions_500.ndjson"
    records = load_ndjson(path)
    require(len(records) == 500, "canonical fixture must contain 500 records")
    transaction_ids = [record.get("cohort_transaction_id") for record in records]
    require(all(transaction_ids), "every transaction requires an identity")
    require(len(transaction_ids) == len(set(transaction_ids)), "transaction IDs must be unique")

    for index, record in enumerate(records, 1):
        validate_timestamps(record, f"transaction[{index}]")
        require(record.get("classification") == "synthetic_demo_data", f"transaction {index}: source classification missing")
        require(record.get("contains_actual_customer_data") is False, f"transaction {index}: actual customer data flag must be false")

    baseline = sum(record["baseline_result"] == "success" for record in records)
    incident = sum(record["incident_result"] == "success" for record in records)
    recovery = sum(record["recovery_result"] == "success" for record in records)
    incident_failures = [record for record in records if record["incident_result"] != "success"]
    eligible_incident_failures = [record for record in incident_failures if record["eligible_for_processor_b"] is True]
    affected = [record for record in records if record["affected_cohort"] is True]
    b_routed = [record for record in records if record["recovery_processor"] == "processor_b"]
    require(baseline == 493, f"baseline successes: expected 493, got {baseline}")
    require(incident == 395, f"incident successes: expected 395, got {incident}")
    require(len(incident_failures) == 105, f"incident failures: expected 105, got {len(incident_failures)}")
    require(recovery == 482, f"recovery successes: expected 482, got {recovery}")
    require(len(eligible_incident_failures) == 87, "policy-eligible incident-failure cohort must contain exactly 87 records")
    require(len(affected) == 87, "affected cohort must contain exactly 87 records")
    require(len(b_routed) == 87, f"Processor B routes: expected 87, got {len(b_routed)}")
    require({record["cohort_transaction_id"] for record in affected} == {record["cohort_transaction_id"] for record in b_routed}, "affected cohort and Processor B routes must be identical")
    require(math.isclose(len(b_routed) / len(records), 0.174), "Processor B route share must be 17.4% of total traffic")
    require(len(b_routed) / len(records) <= 0.20, "Processor B route share exceeds the 20% total cap")

    unauthorized = []
    for record in b_routed:
        allowed = (
            record["affected_cohort"] is True
            and record["incident_result"] != "success"
            and record["eligible_for_processor_b"] is True
            and record["country"] == "US"
            and record["network"] in {"visa", "mastercard"}
            and record["amount_usd"] <= 5000
            and record["recovery_result"] == "success"
            and record["routed_under_approved_action"] is True
        )
        if not allowed:
            unauthorized.append(record["cohort_transaction_id"])
    require(not unauthorized, f"unauthorized Processor B routes: {unauthorized[:8]}")

    for record in records:
        if record["recovery_processor"] != "processor_b":
            require(record["recovery_processor"] == "processor_a", "unexpected recovery processor")
            require(record["routed_under_approved_action"] is False, "non-B route marked as approved reroute")
            if record["incident_result"] != "success":
                require(record["recovery_result"] != "success", "unexplained Processor A recovery found")

    violations = [record for record in records if record["policy_status"] != "OK"]
    require(not violations, "policy violations must equal zero")
    require(sum(record["weighted_payment_value_usd"] for record in records) == 12_500_000, "weighted cohort value must equal $12.5M")
    return records, baseline, incident, recovery, len(b_routed)


def validate_business_math():
    metrics = load_json(CANONICAL / "expected_metrics.json")
    affected_per_minute = 12_000_000_000_000 * 0.00005 / 1440
    returning_sooner = affected_per_minute * 20
    require(metrics["modeled_minutes_saved"] == 20, "modeled minutes saved must equal 20")
    require(math.isclose(metrics["affected_value_per_minute_usd"], affected_per_minute, rel_tol=0, abs_tol=0.01), "affected value per minute mismatch")
    require(math.isclose(metrics["modeled_payment_flow_returning_sooner_usd"], returning_sooner, rel_tol=0, abs_tol=0.01), "recovered-window throughput mismatch")
    limitation = metrics.get("business_value_limitation", "").lower()
    require("not revenue" in limitation and "guaranteed" in limitation, "business-value limitation is incomplete")
    return metrics


def validate_manifest():
    manifest = load_json(CANONICAL / "dataset_manifest.json")
    require(manifest["record_count"] == 500, "manifest record count mismatch")
    require(manifest["classification"] == "synthetic_demo_data", "manifest classification missing")
    require(manifest["contains_actual_customer_data"] is False, "manifest actual customer data flag must be false")
    for source in manifest["source_files"]:
        path = ROOT / source["path"]
        require(path.is_file(), f"source file missing: {source['path']}")
        require(sha256(path) == source["sha256"], f"source hash mismatch: {source['path']}")
    return manifest


def validate_mongo_imports(records, evidence):
    imports = {}
    all_documents = []
    for path in sorted(MONGO_IMPORT.glob("*.ndjson")):
        documents = load_ndjson(path)
        imports[path.name] = documents
        all_documents.extend(documents)
        for index, document in enumerate(documents, 1):
            validate_timestamps(document, f"{path.name}[{index}]")
    require(set(imports) == {"cases.ndjson", "evidence.ndjson", "payment_events.ndjson"}, "unexpected Mongo import file set")
    require(len(imports["cases.ndjson"]) == 1, "Mongo case import count mismatch")
    require(len(imports["evidence.ndjson"]) == len(evidence), "Mongo evidence import count mismatch")
    require(imports["payment_events.ndjson"] == records, "Mongo payment import must exactly match canonical records")
    forbidden_types = {"approval", "approval_validation", "execution", "verification", "journal_event"}
    preloaded = [document.get("document_type") for document in all_documents if document.get("document_type") in forbidden_types]
    require(not preloaded, f"live-state documents must not be preloaded: {preloaded}")

    reference = load_ndjson(REFERENCE_TRACE)
    require(reference and all(document.get("reference_only") is True for document in reference), "expected trace must be reference-only")
    require(all(document.get("document_type") == "reference_expected_trace_step" for document in reference), "expected trace uses a live document type")


def build_receipt(manifest, metrics, baseline, incident, recovery, b_routed):
    source_lines = [
        f"SOURCE_SHA256 {source['path']}: {source['sha256']}"
        for source in manifest["source_files"]
    ]
    lines = [
        "RESOLVE CANONICAL PAYMENT DATA FIXTURE RECEIPT",
        "STATUS: PASS",
        f"DATASET_ID: {manifest['dataset_id']}",
        "CASE_ID: payment_failover_001",
        "TOTAL: 500",
        f"BASELINE_SUCCESS: {baseline} (98.6%)",
        f"INCIDENT_SUCCESS: {incident} (79.0%)",
        f"RECOVERY_SUCCESS: {recovery} (96.4%)",
        f"PROCESSOR_B_ROUTED: {b_routed} (17.4% of total)",
        "CAUSAL_B_ROUTE_CHECK: PASS",
        "UNAUTHORIZED_PROCESSOR_B_ROUTES: 0",
        "POLICY_VIOLATIONS: 0",
        "MAXIMUM_TOTAL_TRAFFIC_SHARE: 20.0%",
        "WEIGHTED_COHORT_VALUE_USD: 12500000",
        f"MODELED_MINUTES_SAVED: {metrics['modeled_minutes_saved']}",
        "MODELED_PAYMENT_FLOW_RETURNING_SOONER_USD: 8333333.33",
        "BUSINESS_VALUE_CLASSIFICATION: payment throughput; not revenue, profit, guaranteed savings, or guaranteed avoided loss",
        "CASE_NORMALIZATION: PASS",
        "UNKNOWN_EVIDENCE_STAGING: PASS",
        "MONGO_IMPORT_JSON: PASS",
        "LIVE_APPROVAL_PRELOADED: NO",
        "LIVE_EXECUTION_PRELOADED: NO",
        "LIVE_VERIFICATION_PRELOADED: NO",
        f"CANONICAL_NDJSON_SHA256: {sha256(CANONICAL / 'payment_transactions_500.ndjson')}",
        *source_lines,
        "OPTIONAL_HTML_VISUAL_REFERENCE: NOT PROVIDED; excluded from data validation",
    ]
    return "\n".join(lines) + "\n"


def main():
    validate_case()
    evidence = validate_evidence()
    records, baseline, incident, recovery, b_routed = validate_transactions()
    metrics = validate_business_math()
    manifest = validate_manifest()
    validate_mongo_imports(records, evidence)
    receipt = build_receipt(manifest, metrics, baseline, incident, recovery, b_routed)
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(receipt, encoding="utf-8")
    print(receipt, end="")


if __name__ == "__main__":
    try:
        main()
    except (KeyError, TypeError, ValueError, OSError, ValidationFailure, yaml.YAMLError) as exc:
        print(f"STATUS: FAIL\nERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
