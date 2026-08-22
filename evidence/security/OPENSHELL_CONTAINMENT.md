# OpenShell containment evidence

Verified 2026-08-22 with `/usr/bin/openshell` version `0.0.91`; gateway healthy at the same version. Sandbox `resolve-containment` was Ready.

POLICY_LOCATION=`runtime/openshell-zero-egress.yaml`
EFFECTIVE_POLICY_VERSION=2
EFFECTIVE_POLICY_HASH=`c93a63667cbf7ee70adb3c3fce12cf19df52a3e0694a804ad7c958479ee60b69`
EFFECTIVE_POLICY_STATUS=Effective

## Public HTTP block

```bash
/usr/bin/openshell sandbox exec -n resolve-containment --no-tty -- \
  curl --fail --silent --show-error http://example.com/
```

Observed policy response: HTTP 403, `GET example.com:80/ not permitted by policy`; curl exit 22. This is an explicit policy denial, not a DNS failure.

ZERO_EGRESS_PUBLIC_BLOCK=PASS

## Local model allow

```bash
/usr/bin/openshell sandbox exec -n resolve-containment --no-tty -- \
  curl --fail --silent --show-error \
  http://host.openshell.internal:8000/v1/models
```

Observed model list contains `qwen3.8-resolve`.

ZERO_EGRESS_LOCAL_MODEL_PASS=PASS

## Local Resolve status

ZERO_EGRESS_LOCAL_RESOLVE_PASS=PENDING_EXTERNAL_DEPENDENCY
DEPENDENCY=Coder 3 must expose the actual Resolve application endpoint and provide its port and health/tool route.

Do not add a fake endpoint to turn this status green. Follow `docs/OPENSHELL_HANDOFF.md` once the real endpoint exists.
