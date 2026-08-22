# Model Repository Volatility Note — checked 2026-08-22

This is an **external verification note**, not part of the uploaded architecture source.

The earlier starter pack pinned `Qwen3.8-27B-UD-Q4_K_XL.gguf` to an older observed SHA/size. The upstream `unsloth/Qwen3.8-27B-GGUF` repository has changed since then: the current main view observed on August 22, 2026 shows a different XL artifact revision/size/hash, and the current model-card examples use `UD-Q4_K_M` rather than assuming XL.

Therefore:
- do not trust a stale hard-coded remote SHA from an older pack;
- inspect the repository immediately before download;
- deliberately select the exact quant you want;
- record repository revision + filename + size;
- generate the SHA-256 of the downloaded local artifact;
- if you intentionally pin an upstream revision, record it in `SOURCE_MANIFEST.csv`;
- acceptance on the GB10, not quant naming, chooses the competition runtime.

Current reference pages:
- https://huggingface.co/unsloth/Qwen3.8-27B-GGUF
- https://huggingface.co/unsloth/Qwen3.8-27B-NVFP4
