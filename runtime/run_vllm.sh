#!/usr/bin/env bash
set -euo pipefail

readonly IMAGE='nvcr.io/nvidia/vllm@sha256:9204569b17ee4c0eff75194b8e6e458479c8aee18953b5ab9cf359fcdac659e2'
readonly MODEL_PATH='/home/dell/Desktop/LAN_LORDS_HACKNYC/MODELS/NVFP4'

exec docker run \
  --name resolve-vllm \
  --pull=never \
  --gpus all \
  --ipc=host \
  -p 127.0.0.1:8000:8000 \
  -p 172.18.0.1:8000:8000 \
  -e HF_HUB_OFFLINE=1 \
  -e TRANSFORMERS_OFFLINE=1 \
  -v "${MODEL_PATH}:/model:ro" \
  "${IMAGE}" \
  vllm serve /model \
  --served-model-name qwen3.8-resolve \
  --host 0.0.0.0 \
  --port 8000 \
  --max-model-len 32768 \
  --max-num-seqs 1 \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.50 \
  --no-enable-prefix-caching \
  --enforce-eager \
  --reasoning-parser qwen3 \
  --tool-call-parser qwen3_coder \
  --enable-auto-tool-choice
