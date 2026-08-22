CODER_1_STATUS=YELLOW; runtime green, C3 endpoint and third-party license verification pending

GITHUB=YashM1503/lan-lords-resolve-hacknyc; remote identified, shell unauthenticated
BRANCH=feat/c1-hardening-readiness
REMOTE=https://github.com/YashM1503/lan-lords-resolve-hacknyc.git

GB10=PASS
CUDA=13.0 host
DRIVER=580.159.03
DOCKER=29.2.1

MODEL=unsloth/Qwen3.8-27B-NVFP4
MODEL_REVISION=7d6f8d4d72f56b92b3cdbf22f156b90e1bab0108
VLLM=0.21.0+2325b6f0.dev
VLLM_IMAGE=nvcr.io/nvidia/vllm:26.05.post1-py3
VLLM_DIGEST=sha256:9204569b17ee4c0eff75194b8e6e458479c8aee18953b5ab9cf359fcdac659e2

NVFP4=PASS
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

MONGODB=PASS; official MongoDB 8.0.29 ARM64; persistence verified
MONGODB_ENDPOINT=mongodb://127.0.0.1:27017

OPENSHELL=PASS; /usr/bin/openshell 0.0.91; deny-by-default sandbox ready
ZERO_EGRESS_PUBLIC_BLOCK=PASS
ZERO_EGRESS_LOCAL_MODEL_PASS=PASS
ZERO_EGRESS_LOCAL_RESOLVE_PASS=PENDING_AWAITING_CODER_3_ENDPOINT

BLOCKER=GitHub shell authentication unavailable; local Resolve endpoint not yet supplied by Coder 3
NEXT=Coder 3 consume the model and MongoDB endpoints, then add/prove the local Resolve route in OpenShell
