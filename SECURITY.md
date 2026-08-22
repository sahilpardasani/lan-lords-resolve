# Security

Resolve is a local execution-assurance demo. It is not a hosted SaaS.

## Report

Open a private GitHub security advisory on [`YashM1503/lan-lords-resolve`](https://github.com/YashM1503/lan-lords-resolve), or contact the LAN LORDS maintainers. Do not file public issues that include secrets, model-weight paths with credentials, or live Mongo dumps.

## Scope

In scope: leakage of `.env` credentials, accidental commit of model weights, Mongo exposed beyond loopback, OpenShell policy regressions that allow public egress.

Out of scope: the synthetic payment dataset, judge-demo UX, and third-party model/container licenses (see `THIRD_PARTY_NOTICES.md`).

## Hard rules

- No cloud LLM keys in the Resolve runtime.
- Mongo and vLLM bind to loopback unless an operator explicitly documents otherwise.
- Do not pre-load a live approval into Mongo before a trial.
