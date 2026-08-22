# Coder 1 red-team report

Scope: malicious local user, careless developer, demo judge, and future-maintainer attacks against the Coder 1 local runtime only.

| ID | Severity | Finding | Evidence | Impact | Fix | Status |
|---|---|---|---|---|---|---|
| RT-001 | HIGH for production; MEDIUM for this single-user demo | MongoDB has no authentication and is reachable to peers on Docker's default bridge despite loopback-only host publication. | Container has no auth flags; `127.0.0.1:27017` host mapping; default bridge container IP exists. | Another local container/user may read or change audit data. | Before production, enable auth with external secrets and isolate it on a dedicated internal network. Do not store production data now. | OPEN / FROZEN-RUNTIME CHANGE REQUIRES REVIEW |
| RT-002 | HIGH for production; MEDIUM for this single-user demo | vLLM API has no authentication and requires a private bridge host bind for OpenShell. | Bindings are `127.0.0.1:8000` and `172.18.0.1:8000`; no wildcard bind/API key; model mount is RO. | Local bridge peers may invoke inference. | Add an authenticated loopback proxy or dedicated internal network after accepted-profile compatibility testing. | ACCEPTED DEMO RISK |
| RT-003 | MEDIUM | OpenShell supervisor container requires powerful capabilities and an unconfined vendor profile. | Runtime inspect shows vendor sandbox capabilities; it is not Docker privileged and has no Docker socket mount. | A supervisor compromise has a broad host-kernel attack surface. | Use only the pinned sponsor image; evaluate a vendor-supported reduced-capability profile post-hackathon. | OPEN / VENDOR BOUNDARY |
| RT-004 | MEDIUM | Landlock compatibility is `best_effort`, and the allowed private CIDRs are broader than one bridge address. | `runtime/openshell-zero-egress.yaml`; effective policy hash recorded. Explicit public HTTP is blocked. | Filesystem enforcement can degrade on unsupported kernels; future private endpoints could be broader than intended. | Validate fail-closed support and narrow to a dedicated subnet after sponsor compatibility review. | OPEN / POLICY HARDENING |
| RT-005 | MEDIUM | Local model artifact permissions are world-readable and unnecessarily executable. | External artifact files are mode 0755; container mount itself is read-only. | Other local accounts can copy weights. | Use a dedicated runtime group and 0640/0750 after confirming container UID requirements. | OPEN / EXTERNAL ARTIFACT; NOT MODIFIED |
| RT-006 | MEDIUM | Existing A7 receipt ended with `finish_reason=length`. | `challenger_result.json`; material boundaries appear in reasoning, but visible answer is truncated. | A reviewer could overestimate output quality. | Harness now requires `finish_reason=stop`; rerun in a future full gate. | FIXED FOR FUTURE RUNS / OLD RECEIPT DISCLOSED |
| RT-007 | LOW | Scripts use fixed names and the vLLM path is machine-specific. | `runtime/run_vllm.sh` and `runtime/run_mongodb.sh`. | Recreate attempts fail unclearly; portability is limited. | Doctor/preflight and operations guide clarify recovery; parameterize after the event. | MITIGATED |
| RT-008 | LOW | Tracked evidence exposes local paths, topology, prompts, and container identifiers. | Evidence files are intentionally committed for auditability. No credentials were detected. | Information disclosure if repository is public. | Keep evidence minimal in future immutable bundles; review repository visibility. | ACCEPTED AUDIT TRADEOFF |

## Positive controls

- No public wildcard binding for ports 8000 or 27017.
- OpenShell gateway binds to loopback and a private Docker bridge, not `0.0.0.0`.
- Neither vLLM nor MongoDB is Docker privileged; neither mounts `docker.sock`.
- The model bind is read-only and both offline-model environment flags are active.
- Runtime tests reject wrong model names, unavailable endpoints, wrong digests/versions, missing artifacts, writable mounts, stale Mac paths, tracked weights, tracked env/key files, and wildcard port publication.
- Public OpenShell HTTP denial is an explicit policy 403, not DNS failure.

No CRITICAL finding was identified. No frozen runtime hardening change was made without compatibility review.
