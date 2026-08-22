#!/usr/bin/env bash
set -u
OUT="${1:-evidence/preflight.txt}"
mkdir -p "$(dirname "$OUT")"
{
  echo "=== HACK NYC GB10 PREFLIGHT ==="
  date
  echo
  echo "--- GPU ---"
  nvidia-smi || true
  echo
  echo "--- TOOL VERSIONS ---"
  python3 --version || true
  node --version || true
  npm --version || true
  nemoclaw --version || true
  openshell --version || true
  openclaw --version || true
  llama-server --version || true
  echo
  echo "--- NEMOCLAW READINESS ---"
  nemoclaw host probe --json || true
  nemoclaw resources --json || true
  nemoclaw agents list || true
  echo
  echo "--- DISK/MEMORY ---"
  df -h || true
  free -h || true
} 2>&1 | tee "$OUT"
echo "Saved: $OUT"
