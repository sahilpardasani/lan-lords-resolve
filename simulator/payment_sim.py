"""
simulator/payment_sim.py  --  local payment state (Coder 3, mockable)

Holds the live payment success rate. A committed action mutates it; the
verifier reads the REAL state back (spec: "verification reads actual
simulator state"). No randomness at commit time so the demo is deterministic.
"""


class PaymentSimulator:
    def __init__(self):
        # Business 1 frozen facts
        self.baseline = 98.6
        self.current = 79.0
        self._committed = None

    def state(self) -> dict:
        return {"baseline_success": self.baseline,
                "current_success": round(self.current, 1),
                "committed_action": self._committed}

    def apply_failover(self, region: str, traffic_pct: int) -> dict:
        """Commit a bounded failover. Recovery scales with how much eligible
        traffic was actually moved. Bounded US 40% recovers most of the gap."""
        gap = self.baseline - self.current
        # only US-eligible traffic can recover; global is not authorized anyway
        recovered = gap * (traffic_pct / 100.0) if region == "US" else 0.0
        self.current = min(self.baseline, self.current + recovered)
        self._committed = {"region": region, "traffic_pct": traffic_pct}
        return self.state()
