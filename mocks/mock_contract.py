"""
mocks/mock_contract.py  --  stand-in for Coder 2's resolve/contract.py

PURE permission logic. MUST NOT import/query MongoDB. Same DecisionInput ->
same verdict, whether Mongo is up or down. Returns the frozen result shape.

Gates: INTENT EVIDENCE CONSTRAINTS CONSEQUENCE REVERSIBILITY REHEARSAL
       AUTHORITY VERIFICATION  each PASS / FAIL / UNKNOWN
Dispositions: MORE_EVIDENCE_REQUIRED | BLOCKED | WAITING_HUMAN | PASS
"""

GATES = ["intent", "evidence", "constraints", "consequence",
         "reversibility", "rehearsal", "authority", "verification"]


def _all(v):
    return {g: v for g in GATES}


def evaluate(candidate: dict, case: dict, evidence: dict) -> dict:
    params = candidate.get("parameters", {})
    region = params.get("region")
    traffic = params.get("traffic_pct", 0)

    # hard constraint FIRST: Processor B only for eligible bounded traffic.
    # GLOBAL violates it no matter the evidence -> BLOCKED (spec: hard constraint)
    if region == "GLOBAL":
        g = _all("PASS"); g["constraints"] = "FAIL"
        return {"gates": g, "disposition": "BLOCKED",
                "reason_codes": ["CONSTRAINT_PROCESSOR_B_BOUNDED_ONLY"]}

    # missing material evidence -> MORE_EVIDENCE_REQUIRED
    if not evidence.get("traffic_breakdown"):
        g = _all("PASS"); g["evidence"] = "UNKNOWN"
        return {"gates": g, "disposition": "MORE_EVIDENCE_REQUIRED",
                "reason_codes": ["MISSING_TRAFFIC_EVIDENCE"]}

    # bounded action exceeding eligible traffic -> BLOCKED
    eligible = evidence["traffic_breakdown"].get("us_eligible_pct", 0)
    if traffic > eligible:
        g = _all("PASS"); g["constraints"] = "FAIL"
        return {"gates": g, "disposition": "BLOCKED",
                "reason_codes": ["CONSTRAINT_EXCEEDS_ELIGIBLE_TRAFFIC"]}

    # eligible bounded candidate -> all gates pass, needs human authority
    return {"gates": _all("PASS"), "disposition": "WAITING_HUMAN",
            "reason_codes": []}
