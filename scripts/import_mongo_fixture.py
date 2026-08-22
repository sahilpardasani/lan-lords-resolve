#!/usr/bin/env python3
"""Safely upsert the canonical pre-loadable fixture into MongoDB."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_payment_fixture import load_ndjson, main as validate_fixture


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uri", default=os.environ.get("MONGODB_URI", "mongodb://127.0.0.1:27017"))
    parser.add_argument("--database", default="resolve_demo")
    parser.add_argument("--dry-run", action="store_true", help="validate and print import counts without connecting")
    return parser.parse_args()


def main():
    args = arguments()
    validate_fixture()
    import_dir = ROOT / "data" / "mongodb" / "import"
    cases = load_ndjson(import_dir / "cases.ndjson")
    evidence = load_ndjson(import_dir / "evidence.ndjson")
    payment_events = load_ndjson(import_dir / "payment_events.ndjson")

    if args.dry_run:
        print(f"MONGO_IMPORT_DRY_RUN: PASS database={args.database} cases={len(cases)} evidence={len(evidence)} payment_events={len(payment_events)}")
        return

    try:
        from pymongo import ASCENDING, MongoClient, ReplaceOne
    except ImportError as exc:
        raise SystemExit("pymongo is required for a live import; use --dry-run for validation only") from exc

    client = MongoClient(args.uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    database = client[args.database]
    database.cases.create_index([("case_id", ASCENDING)], unique=True)
    database.evidence.create_index([("case_id", ASCENDING), ("evidence_id", ASCENDING)], unique=True)
    database.payment_events.create_index([("dataset_id", ASCENDING), ("cohort_transaction_id", ASCENDING)], unique=True)

    database.cases.bulk_write(
        [ReplaceOne({"case_id": document["case_id"]}, document, upsert=True) for document in cases],
        ordered=True,
    )
    database.evidence.bulk_write(
        [ReplaceOne({"case_id": document["case_id"], "evidence_id": document["evidence_id"]}, document, upsert=True) for document in evidence],
        ordered=True,
    )
    database.payment_events.bulk_write(
        [ReplaceOne({"dataset_id": document["dataset_id"], "cohort_transaction_id": document["cohort_transaction_id"]}, document, upsert=True) for document in payment_events],
        ordered=True,
    )
    print(
        "MONGO_IMPORT: PASS "
        f"database={args.database} "
        f"cases={len(cases)} "
        f"evidence={len(evidence)} "
        f"payment_events={len(payment_events)}"
    )


if __name__ == "__main__":
    main()
