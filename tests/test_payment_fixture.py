"""Repository-level conformance test for the canonical payment fixture."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_canonical_payment_fixture_passes_validator() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/validate_payment_fixture.py"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "STATUS: PASS" in result.stdout
    assert "CAUSAL_B_ROUTE_CHECK: PASS" in result.stdout
    assert "LIVE_APPROVAL_PRELOADED: NO" in result.stdout
