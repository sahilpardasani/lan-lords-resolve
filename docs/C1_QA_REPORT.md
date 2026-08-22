# Coder 1 QA report

Scope: runtime/infrastructure files only. The frozen runtime configuration was not tuned or redesigned.

## P0_BLOCKER

None.

## P1_FIX_NOW

- QA-001: Mongo recreation could pull from the network when the pinned image was absent. Fixed by adding `--pull=never`; failure is now explicit and offline-safe.
- QA-002: Challenger acceptance accepted a length-truncated completion because it inspected reasoning without requiring normal completion. Fixed future harness behavior by requiring `finish_reason == "stop"`. Existing A7 material conclusion remains recorded, but the old receipt's truncation is disclosed.
- QA-003: No automated read-only readiness or negative-test suite. Fixed with `runtime/doctor.py` and `runtime/tests/test_runtime.py`.
- QA-004: No license, attribution boundary, operations guide, or component manifest. Fixed in this branch.

## P2_POST_HACKATHON

- Replace hard-coded model path with a validated operator-supplied path while preserving the accepted default.
- Produce full SPDX/CycloneDX SBOMs and authoritative license bundles for both pinned images.
- Make create/start/recover scripts fully idempotent with explicit existing-container preflight messages.
- Create immutable per-run evidence bundles instead of a cumulative server log.
- Revalidate challenger A7 with the stricter non-truncation assertion during a future full acceptance run.

## INFORMATIONAL

- Shell scripts use strict mode and pinned digests; vLLM additionally forbids pulling.
- Model mount is read-only; HF Hub and Transformers offline flags are present.
- No stale macOS volume or user-home absolute paths exist in tracked repository files.
- No tracked model weights, `.env`, private-key files, or obvious credentials were found.
- The private bridge publication on `172.18.0.1:8000` is intentional for OpenShell and is documented in the frozen profile; it is not a public wildcard bind.
- `runtime/__pycache__` was generated locally but is ignored and untracked.

## Validation performed

- `bash -n` on all shell scripts
- Python compile checks
- runtime unit/negative tests
- doctor read-only readiness
- `git diff --check`
- path, secret, weight, cache, permission, and large-file scans
- container image, mount, privilege, network, and port inspection
