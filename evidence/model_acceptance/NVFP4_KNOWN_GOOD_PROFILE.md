MODEL=unsloth/Qwen3.8-27B-NVFP4
MODEL_PATH=/home/dell/Desktop/LAN_LORDS_HACKNYC/MODELS/NVFP4
MODEL_REVISION=7d6f8d4d72f56b92b3cdbf22f156b90e1bab0108
MODEL_SHA=c473512c70eace07e2256fe9fd76596ac03e3295bee7d54cfb72676416afcc05
MTP_SHA=1d8268aa85ace093a561e3e7b63b9d390dac1cd55a90cd55b5ec509c3c9da9fe
TOKENIZER_SHA=06b9509352d2af50381ab2247e083b80d32d5c0aba91c272ca9ff729b6a0e523
VLLM_VERSION=0.21.0+2325b6f0.dev
CONTAINER_IMAGE=nvcr.io/nvidia/vllm:26.05.post1-py3
CONTAINER_DIGEST=sha256:9204569b17ee4c0eff75194b8e6e458479c8aee18953b5ab9cf359fcdac659e2
DRIVER=580.159.03
CUDA=13.0 host; NVIDIA container CUDA forward-compatibility mode
ARCHITECTURE=linux/arm64; NVIDIA GB10 SM121
MAX_MODEL_LEN=32768
MAX_NUM_SEQS=1
ATTENTION_BACKEND=FLASHINFER; FLASH_ATTN for vision encoder
KV_CACHE_DTYPE=auto
REASONING_PARSER=qwen3
TOOL_CALL_PARSER=qwen3_coder
THINKING_CONFIGURATION=per-request chat_template_kwargs.enable_thinking
EXACT_DOCKER_LAUNCH_COMMAND=docker run --name resolve-vllm --pull=never --gpus all --ipc=host -p 127.0.0.1:8000:8000 -p 172.18.0.1:8000:8000 -e HF_HUB_OFFLINE=1 -e TRANSFORMERS_OFFLINE=1 -v /home/dell/Desktop/LAN_LORDS_HACKNYC/MODELS/NVFP4:/model:ro nvcr.io/nvidia/vllm@sha256:9204569b17ee4c0eff75194b8e6e458479c8aee18953b5ab9cf359fcdac659e2 vllm serve /model --served-model-name qwen3.8-resolve --host 0.0.0.0 --port 8000 --max-model-len 32768 --max-num-seqs 1 --tensor-parallel-size 1 --gpu-memory-utilization 0.50 --no-enable-prefix-caching --enforce-eager --reasoning-parser qwen3 --tool-call-parser qwen3_coder --enable-auto-tool-choice

A0=PASS
A1=PASS
A2=PASS
A2B=PASS
A3=PASS
A4=PASS
A5=PASS
A6=PASS
A7=PASS

MODEL_ENDPOINT=http://127.0.0.1:8000/v1
MODEL_ALIAS=qwen3.8-resolve
REPRODUCIBLE_LAUNCH_SCRIPT=runtime/run_vllm.sh

NOTE=--enforce-eager is required because the default Torch AOT path fails while serializing a Transformers launcher function. The second port publication is restricted to the private OpenShell Docker bridge for policy-proxied sandbox access. No runtime package was changed.
