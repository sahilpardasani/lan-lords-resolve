"""
mocks/mock_ai.py  --  stand-in for Coder 1's local Qwen/vLLM reasoning.

Returns candidate actions in the FROZEN candidate shape. No real inference;
deterministic so the demo is reproducible. Swap for the real local model
endpoint later without touching runtime.py.
"""


def propose_first(case: dict) -> dict:
    """AI's first instinct under pressure: reroute EVERYTHING (the tempting
    wrong action). Processor B, GLOBAL, 100%. Contract will BLOCK this."""
    return {
        "action_type": "payments.failover",
        "target": "processor_b",
        "parameters": {"region": "GLOBAL", "traffic_pct": 100},
    }


def propose_bounded(case: dict, evidence: dict) -> dict:
    """After evidence reveals eligible traffic, propose the bounded action:
    Processor B, US, 40% (Business 1's good candidate)."""
    return {
        "action_type": "payments.failover",
        "target": "processor_b",
        "parameters": {"region": "US", "traffic_pct": 40},
    }
