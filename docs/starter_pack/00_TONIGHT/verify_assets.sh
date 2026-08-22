#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
export HACK_NYC_ROOT="$ROOT"
echo "HACK NYC asset verification"
echo "Root: $ROOT"

command -v python3 >/dev/null
python3 --version

for f in \
  "$ROOT/HACK_NYC_MASTER_PLAN.md" \
  "$ROOT/CODEX_START_HACK_NYC.md" \
  "$ROOT/CURSOR_START_HACK_NYC.md" \
  "$ROOT/01_KICKOFF/RUBRIC_MAP.md" \
  "$ROOT/03_QA/P0_TEST_PLAN.md"; do
  test -s "$f"
done

python3 - <<'PY'
from pathlib import Path
import json, os
root=Path(os.environ['HACK_NYC_ROOT'])
json_files=list(root.rglob('*.json'))
jsonl_files=list(root.rglob('*.jsonl'))
for p in json_files:
    json.loads(p.read_text())
for p in jsonl_files:
    for i,line in enumerate(p.read_text().splitlines(),1):
        if line.strip():
            json.loads(line)
print(f"PASS JSON: {len(json_files)} JSON, {len(jsonl_files)} JSONL")
PY

echo "PASS: starter pack structure."
