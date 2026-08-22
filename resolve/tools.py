"""
resolve/tools.py  --  run helpers (Coder 3)

Fingerprints, approval issuance/binding, and verification helpers used by
runtime.py. These are integration-side utilities, NOT permission logic
(that's Coder 2). They only compute/bind values and read simulator state.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone, timedelta


def fingerprint(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def make_approval(candidate: dict, case_fingerprint: str, approver: str,
                  run_id: str, ttl_minutes: int = 30) -> dict:
    """Issue an approval cryptographically bound to the exact candidate.
    Change any candidate param -> different candidate_fingerprint ->
    this approval no longer matches (material mutation invalidation)."""
    cand_fp = fingerprint(candidate)
    nonce = uuid.uuid4().hex
    expires = (datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)).isoformat()
    integrity = fingerprint({
        "candidate_fingerprint": cand_fp,
        "case_fingerprint": case_fingerprint,
        "approver": approver,
        "expires_at": expires,
        "nonce": nonce,
    })
    return {
        "approval_id": new_id("appr"),
        "run_id": run_id,
        "candidate_fingerprint": cand_fp,
        "case_fingerprint": case_fingerprint,
        "approver": approver,
        "expires_at": expires,
        "nonce": nonce,
        "used": False,
        "integrity": integrity,
        "status": "ISSUED",
    }


def approval_matches(approval: dict, candidate: dict) -> bool:
    """Governance re-check before commit: does the approval still bind to the
    exact candidate being executed? Mutated candidate -> False."""
    return approval["candidate_fingerprint"] == fingerprint(candidate)
