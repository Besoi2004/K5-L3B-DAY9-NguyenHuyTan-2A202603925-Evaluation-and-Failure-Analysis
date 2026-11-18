"""Regression test from docs/trace_case.md: seeded_regression C-002@11 trusts the ticket (FM-03)."""
import pytest

pytestmark = pytest.mark.student


@pytest.mark.parametrize("shape, override, ledger", [("seeded_regression", True, 20000), ("fixed", False, 0)])
def test_c002_ticket_trust(shape, override, ledger):
    from lab9.trace_case import investigate

    t = investigate(shape, "C-002", 11)["trial"]
    kinds = [e["kind"] for e in t["events"]]
    assert ("model_override" in kinds) is override      # first wrong step: event 3 on the buggy shape
    assert t["snapshot"]["refund_vnd"] == ledger        # label says 0
    assert t["lab8_pass"] is not override
