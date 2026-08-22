# Case 02 — Payment Authorization Outage

Payment success fell from **98.6% to 79.0%** shortly after a deployment. The easy answer is “fail all traffic to processor B,” but a segment-level check shows that processor B is unsafe for one regulated region.

Resolve should isolate the affected segment, distinguish deployment/configuration from upstream processor failure, and recommend a bounded failover rather than a global switch.
