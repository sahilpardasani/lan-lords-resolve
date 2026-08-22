# Third-party notices

The root Apache License 2.0 applies only to source and documentation authored by LAN LORDS in this repository. It does not grant rights to third-party models, containers, binaries, or packages.

Model weights and Docker images are not included or redistributed in this Git repository. Operators must obtain them separately and comply with their respective terms.

| Component | Source/project | Pinned identity | License status | Redistribution status / notes |
|---|---|---|---|---|
| Qwen3.8-27B-NVFP4 | `unsloth/Qwen3.8-27B-NVFP4`, based on Qwen | revision `7d6f8d4d72f56b92b3cdbf22f156b90e1bab0108` | Model card declares Apache-2.0; standalone license/NOTICE absent locally, so complete obligations need verification | Weights are external, mounted read-only, and not redistributed here. Preserve model-card and upstream attribution. |
| vLLM | vLLM in NVIDIA NGC container | `0.21.0+2325b6f0.dev`; digest `sha256:9204569b17ee4c0eff75194b8e6e458479c8aee18953b5ab9cf359fcdac659e2` | Python distribution reports Apache-2.0; complete NVIDIA container EULA and bundled component notices need verification | Image is referenced by digest, not redistributed. NGC usage/redistribution terms govern the image. |
| NVIDIA container/runtime content | NVIDIA NGC vLLM image and host NVIDIA Container Toolkit | image digest above; toolkit `1.19.1` | Toolkit package copyright records Apache-2.0; CUDA/NGC image terms need verification | Not redistributed here. Digest pinning identifies content but is not a license grant. |
| MongoDB | Official `mongo` container / MongoDB Server | image digest `sha256:d7c8d78b890e2d87ff11b30656a6c991addcc260723c9be723123041763d00a8`; server `8.0.29` | `LICENSE_STATUS=NEEDS_VERIFICATION` from authoritative Server and official-image notices | Used as a local service; image is not redistributed here. |
| OpenShell CLI | NVIDIA OpenShell | `/usr/bin/openshell` `0.0.91`; SHA-256 `791487086ea80a536b9f8099de6014553a848b72f31bd0e39ac51f3b7701a205` | `LICENSE_STATUS=NEEDS_VERIFICATION` | Preinstalled host binary; not redistributed here. |
| OpenShell community sandbox | NVIDIA OpenShell Community Ollama sandbox | digest `sha256:ddc74aa75ac47793754510b4d75ff6f739ec4dbe4d6fba48e48879826106a585`; revision label `fffb6b2248ff6ba585f50517f3711b08122089f2` | OCI label declares Apache-2.0; full bundled notices need verification | Image is not redistributed here. |
| Python standard library | Python Software Foundation | host Python `3.12.3` | Python license applies | No third-party Python packages are vendored by this repository. Runtime packages remain inside the pinned container. |

No npm dependencies or vendored application dependencies are present on this branch.
