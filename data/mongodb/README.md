# MongoDB fixture import

Canonical fixture context: [../../README.md](../../README.md) and [../../cases/primary/EXPECTED.md](../../cases/primary/EXPECTED.md). Reconciliation: [../../docs/SOURCE_RECONCILIATION.md](../../docs/SOURCE_RECONCILIATION.md).

Only source fixtures are pre-loadable: the synthetic case, staged evidence, and the canonical 500-transaction cohort. The import does not create approvals, executions, verifications, journal events, or replay state.

Validate without MongoDB:

```bash
python3 scripts/import_mongo_fixture.py --dry-run
```

Import to the local demo database:

```bash
python3 scripts/import_mongo_fixture.py --database resolve_demo
```

The importer uses keyed upserts scoped to `case_id`, `evidence_id`, `dataset_id`, and `cohort_transaction_id`. It never drops a database or collection and does not delete unrelated documents.

`reference_expected_trace/expected_trace.ndjson` is a reference-only benchmark. It must not be imported as evidence that a live run occurred.
