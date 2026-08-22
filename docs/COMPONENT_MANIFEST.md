# Coder 1 component manifest

Verified locally on 2026-08-22. Digests identify exact content; they do not establish publisher authenticity or redistribution permission.

| Component | Exact version / identity |
|---|---|
| OS | Ubuntu 24.04.4 LTS |
| Architecture | Linux `arm64` / `aarch64` |
| Kernel | `6.17.0-1021-nvidia` |
| GPU | NVIDIA GB10, compute capability 12.1 |
| NVIDIA driver | `580.159.03` |
| Host CUDA | `13.0` |
| Docker | `29.2.1`, build `a5c7197` |
| NVIDIA Container Toolkit | `1.19.1-1` |
| Python | `3.12.3` |
| vLLM | `0.21.0+2325b6f0.dev` |
| NVIDIA vLLM image | `nvcr.io/nvidia/vllm@sha256:9204569b17ee4c0eff75194b8e6e458479c8aee18953b5ab9cf359fcdac659e2`; image ID `sha256:46591c6e4a018d8d197fa246b1e3d682c907654aab4e9402302abb3e6a7dd916`; linux/arm64 |
| Model | `unsloth/Qwen3.8-27B-NVFP4`; revision `7d6f8d4d72f56b92b3cdbf22f156b90e1bab0108` |
| Model SHA-256 | `c473512c70eace07e2256fe9fd76596ac03e3295bee7d54cfb72676416afcc05` |
| MTP artifact SHA-256 | `1d8268aa85ace093a561e3e7b63b9d390dac1cd55a90cd55b5ec509c3c9da9fe` (present but MTP disabled) |
| Tokenizer SHA-256 | `06b9509352d2af50381ab2247e083b80d32d5c0aba91c272ca9ff729b6a0e523` |
| MongoDB image | `mongo@sha256:d7c8d78b890e2d87ff11b30656a6c991addcc260723c9be723123041763d00a8`; image ID `sha256:43cfd95ac9101cf925da82777d63c7a7d0a7c17efc0e348f6e45b4d59ca5c123`; linux/arm64 |
| MongoDB Server | `8.0.29`, git version `559d67c651f7393e62757234a0b25cb7a8622148` |
| OpenShell | `/usr/bin/openshell` `0.0.91`; SHA-256 `791487086ea80a536b9f8099de6014553a848b72f31bd0e39ac51f3b7701a205` |
| OpenShell sandbox | `ghcr.io/nvidia/openshell-community/sandboxes/ollama@sha256:ddc74aa75ac47793754510b4d75ff6f739ec4dbe4d6fba48e48879826106a585` |

There is no project package manager manifest on this runtime-only branch. `runtime/model_acceptance.py`, `runtime/doctor.py`, and the test suite use only the Python standard library. Full container SBOMs and authoritative license bundles remain a post-hackathon supply-chain task.
