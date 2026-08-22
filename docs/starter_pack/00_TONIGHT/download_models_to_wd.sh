#!/usr/bin/env bash
set -euo pipefail

# Guarded pre-event artifact downloader. It NEVER auto-selects a disk.
# Usage:
#   WD_VOLUME="My Passport" DOWNLOAD_NVFP4=1 ./download_models_to_wd.sh
# Optional: DOWNLOAD_FP8=1

: "${WD_VOLUME:?Set WD_VOLUME to the exact confirmed mounted WD volume name under /Volumes}"
WD_MOUNT="/Volumes/${WD_VOLUME}"
[[ -d "$WD_MOUNT" ]] || { echo "Missing volume: $WD_MOUNT" >&2; exit 2; }

ROOT="$WD_MOUNT/LAN_LORDS_HACKNYC"
mkdir -p "$ROOT"/{MODELS/GGUF,MODELS/NVFP4,MODELS/FP8_FALLBACK,STACK/source_archives,STACK/docker_images,STACK/linux_arm64_wheels,STACK/offline_docs,PRE_EVENT_ALLOWED_MATERIALS,CHECKSUMS,MANIFESTS}

echo "Target: $ROOT"
df -h "$WD_MOUNT"

HF=""
if command -v hf >/dev/null 2>&1; then HF="hf"; elif command -v huggingface-cli >/dev/null 2>&1; then HF="huggingface-cli"; else
  echo "Hugging Face CLI not found. Install it in your user environment, then rerun." >&2
  exit 3
fi

# Exact GGUF filename is intentionally not hard-coded: inspect repo first and approve the quant.
echo "Inspect the current GGUF repository/model card and select the exact quant deliberately; do not assume a quant:"
echo "  https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/tree/main"
echo "Then use one of these patterns, depending on installed CLI:"
echo "  hf download unsloth/Qwen3.8-27B-GGUF <EXACT_GGUF_FILENAME> --local-dir \"$ROOT/MODELS/GGUF\""
echo "  huggingface-cli download unsloth/Qwen3.8-27B-GGUF <EXACT_GGUF_FILENAME> --local-dir \"$ROOT/MODELS/GGUF\""

if [[ "${DOWNLOAD_NVFP4:-0}" == "1" ]]; then
  echo "Downloading NVFP4 repository..."
  "$HF" download unsloth/Qwen3.8-27B-NVFP4 --local-dir "$ROOT/MODELS/NVFP4"
fi

if [[ "${DOWNLOAD_FP8:-0}" == "1" ]]; then
  echo "Downloading optional FP8 fallback..."
  "$HF" download Qwen/Qwen3.8-27B-FP8 --local-dir "$ROOT/MODELS/FP8_FALLBACK"
fi

find "$ROOT/MODELS" -type f -size 0 -print | tee "$ROOT/MANIFESTS/ZERO_LENGTH_FILES.txt"
find "$ROOT/MODELS" -type f -print0 | xargs -0 shasum -a 256 > "$ROOT/CHECKSUMS/MODEL_SHA256SUMS.txt"

python3 - "$ROOT" <<'PY2'
from pathlib import Path
import csv, os, sys, datetime
root=Path(sys.argv[1])
rows=[]
for f in sorted((root/'MODELS').rglob('*')):
    if f.is_file():
        rows.append([f.relative_to(root).as_posix(), f.stat().st_size, datetime.datetime.now().astimezone().isoformat()])
with (root/'MANIFESTS'/'MODEL_FILES.csv').open('w', newline='') as h:
    w=csv.writer(h); w.writerow(['path','bytes','observed_at']); w.writerows(rows)
print(f"Recorded {len(rows)} model files")
PY2

echo "Checksums: $ROOT/CHECKSUMS/MODEL_SHA256SUMS.txt"
df -h "$WD_MOUNT"
