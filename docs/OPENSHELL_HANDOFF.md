# OpenShell handoff to Coder 3

- Binary: `/usr/bin/openshell`
- Required CLI/gateway version: `0.0.91`
- Sandbox: `resolve-containment`
- Base policy: `runtime/openshell-zero-egress.yaml`
- Accepted effective policy hash before Resolve integration: `c93a63667cbf7ee70adb3c3fce12cf19df52a3e0694a804ad7c958479ee60b69`

## Existing proofs

Public block:

```bash
/usr/bin/openshell sandbox exec -n resolve-containment --no-tty -- \
  curl --fail --silent --show-error http://example.com/
```

Expected: policy HTTP 403 and nonzero curl exit. DNS failure alone is not a pass.

Local Qwen allow:

```bash
/usr/bin/openshell sandbox exec -n resolve-containment --no-tty -- \
  curl --fail --silent --show-error \
  http://host.openshell.internal:8000/v1/models
```

Expected: JSON containing `qwen3.8-resolve`.

## Final local Resolve proof

Coder 3 must first bind the real Resolve service to loopback and the same private OpenShell bridge address used by the model. Replace `8080` and `/health` below only with the actual port and health route supplied by Coder 3.

```bash
RESOLVE_PORT=8080
RESOLVE_PATH=/health
/usr/bin/openshell policy update resolve-containment \
  --add-endpoint "host.openshell.internal:${RESOLVE_PORT}::rest:enforce:allowed-ip=172.16.0.0/12" \
  --binary /usr/bin/curl \
  --add-allow "host.openshell.internal:${RESOLVE_PORT}:GET:${RESOLVE_PATH}" \
  --wait
/usr/bin/openshell policy get resolve-containment
/usr/bin/openshell sandbox exec -n resolve-containment --no-tty -- \
  curl --fail --silent --show-error \
  "http://host.openshell.internal:${RESOLVE_PORT}${RESOLVE_PATH}"
```

Expected: policy status `Effective`, curl exit 0, and the application's documented healthy response. Then rerun the public block and local Qwen tests to prove the added rule did not broaden unrelated egress. Record the new policy hash and exact output in `evidence/security/OPENSHELL_CONTAINMENT.md` and change the status to PASS.

## Troubleshooting

- `connection refused`: verify the application is listening on the Docker bridge address as well as loopback; do not publish on `0.0.0.0`.
- HTTP 403 `not permitted by policy`: confirm host, port, method, and path exactly match the added endpoint/rule.
- DNS error: verify sandbox phase is Ready and use `host.openshell.internal`; DNS failure is not containment evidence.
- HTTP 502: verify the bridge-bound host service works from the host before changing policy.
- Policy not Effective: stop and collect `openshell gateway info`, `openshell sandbox list`, and `openshell policy get resolve-containment`; do not weaken enforcement.
