# Resolve Architecture Update — Applied Delta

This pack preserves the previous Hack NYC event rules, compliance boundary, synthetic case references, source materials, and empty repo scaffold while applying the Resolve architecture-lock delta.

## Changed
- Product thesis: troubleshooting **and permission** loop.
- Five roles: `main`, `scout`, `investigator`, `planner`, `challenger`.
- Removed LLM final Judge; `contract.py` is deterministic permission judge.
- Added 8-gate contract: INTENT, EVIDENCE, CONSTRAINTS, CONSEQUENCE, REVERSIBILITY, REHEARSAL, AUTHORITY, VERIFICATION.
- `case.yaml` is the generalization boundary; no per-domain skill trees/adapters in P0.
- Model policy: carry GGUF + NVFP4; acceptance suite chooses serving path.
- Added long-context/tool/sponsor-stack/zero-egress model acceptance suite.
- Added `doctor.py` diagnostic specification.
- Added behavior calibration/property checks.
- Added hypothetical loss-leader objective benchmark.
- Updated phase gates and hard feature freezes.
- Updated demo around approval binding/mutation + counterfactual evidence.
- Updated Cursor/Codex division of labor and single-writer critical files.

## Preserved
- Build-after-kickoff originality boundary.
- Local GB10 inference requirement.
- OpenClaw/NemoClaw/OpenShell sponsor path.
- Existing five synthetic business/domain cases.
- Rubric map, provenance, source materials, manifests, replay/recording strategy.

## External verification correction
The older pack's hard-coded GGUF SHA became stale as the upstream repository changed. The updated downloader requires explicit quant/revision selection and records the downloaded artifact's local SHA instead of silently trusting the old hash.
