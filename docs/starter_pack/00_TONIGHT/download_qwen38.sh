#!/usr/bin/env bash
set -euo pipefail

# Safe single-GGUF downloader. No quant or remote SHA is silently assumed.
# Example:
#   GGUF_FILE="Qwen3.8-27B-UD-Q4_K_M.gguf" ./download_qwen38.sh /Volumes/<WD>/LAN_LORDS_HACKNYC/MODELS/GGUF
# Optional:
#   GGUF_REVISION=<commit_sha> EXPECTED_SHA256=<sha256> ...

DEST="${1:-$PWD/MODELS/GGUF}"
REPO="unsloth/Qwen3.8-27B-GGUF"
: "${GGUF_FILE:?Set GGUF_FILE to the exact quant filename after inspecting the current repository/model card}"

mkdir -p "$DEST"
if ! command -v hf >/dev/null 2>&1; then
  echo "hf CLI not found. Install huggingface_hub in your user environment, then rerun." >&2
  exit 3
fi

args=(download "$REPO" "$GGUF_FILE" --local-dir "$DEST")
if [[ -n "${GGUF_REVISION:-}" ]]; then
  args+=(--revision "$GGUF_REVISION")
fi
hf "${args[@]}"

# Small text/config assets are useful if present; failure is non-fatal.
ref_args=(download "$REPO" README.md --local-dir "$DEST")
if [[ -n "${GGUF_REVISION:-}" ]]; then
  ref_args+=(--revision "$GGUF_REVISION")
fi
hf "${ref_args[@]}" || true

if command -v sha256sum >/dev/null 2>&1; then
  ACTUAL="$(sha256sum "$DEST/$GGUF_FILE" | awk '{print $1}')"
else
  ACTUAL="$(shasum -a 256 "$DEST/$GGUF_FILE" | awk '{print $1}')"
fi
printf '%s  %s\n' "$ACTUAL" "$GGUF_FILE" > "$DEST/SHA256SUMS"

if [[ -n "${EXPECTED_SHA256:-}" ]]; then
  echo "Expected: $EXPECTED_SHA256"
  echo "Actual:   $ACTUAL"
  test "$ACTUAL" = "$EXPECTED_SHA256"
fi

echo "Downloaded: $DEST/$GGUF_FILE"
echo "Local SHA256: $ACTUAL"
echo "Record the repository revision used before the event."
