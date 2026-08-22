#!/usr/bin/env bash
# Public-release QA sweep. Does not generate Codex canonical fixtures
# and does not start vLLM/Mongo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail=0
note() { printf '%s\n' "$*"; }
bad() { printf 'FAIL %s\n' "$*" >&2; fail=1; }
ok() { printf 'PASS %s\n' "$*"; }

note "==== public sweep $(date -u +%Y-%m-%dT%H:%M:%SZ) sha=$(git rev-parse --short HEAD 2>/dev/null || echo unknown) ===="

# Required public files
for f in LICENSE NOTICE README.md DEPLOY.md CONTRIBUTING.md SECURITY.md requirements.txt .env.example THIRD_PARTY_NOTICES.md docs/REPO_PREP.md docs/LICENSING.md; do
  [[ -f "$f" ]] && ok "present $f" || bad "missing $f"
done

grep -q 'Apache License' LICENSE && ok "LICENSE Apache-2.0" || bad "LICENSE is not Apache-2.0"

# Secrets / weights must not be tracked
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if git ls-files | grep -E '(^|/)\.env$|\.pem$|\.key$|credentials/|hf_cache/|\.gguf$|\.safetensors$' >/dev/null; then
    bad "tracked secret or weight-like path"
  else
    ok "no tracked env/key/weight paths"
  fi
fi

# Codex lane is reserved; absence is YELLOW, not FAIL
for p in cases/primary/case.yaml data/canonical docs/SOURCE_RECONCILIATION.md scripts/validate_payment_fixture.py; do
  if [[ -e "$p" ]]; then ok "codex artifact present $p"; else note "YELLOW reserved for Codex, not yet present: $p"; fi
done

# Tests
if command -v python3 >/dev/null; then
  python3 -m pytest -q tests/test_mongo_store.py && ok "mongo tests" || bad "mongo tests"
fi
if [[ -x /opt/anaconda3/bin/python3.13 ]]; then
  /opt/anaconda3/bin/python3.13 -m pytest -q \
    tests/test_contract.py tests/test_approval.py tests/test_journal.py tests/test_objective.py \
    && ok "core tests" || bad "core tests"
fi

# Port documentation
if grep -n -- '--port 8000' app.py >/dev/null; then
  note "YELLOW app.py still documents uvicorn port 8000; operators must use 8080 (see DEPLOY.md)"
fi

if [[ "$fail" -ne 0 ]]; then
  note "SWEEP: FAIL"
  exit 1
fi
note "SWEEP: PASS"
exit 0
