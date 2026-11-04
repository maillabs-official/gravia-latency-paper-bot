"""Validate delayed paper fills against observed order-book snapshots.

This is an evaluation gate, not a predictive edge or a trading system.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Quote:
    token_id: str
    received_ms: int
    ask: float
    ask_shares: float
    bid: float
    bid_shares: float

    def valid(self):
        return (self.token_id.isdigit() and 0 < self.bid <= self.ask < 1
                and self.ask_shares >= 0 and self.bid_shares >= 0)

def delayed_buy_quote(decision_ms, snapshots, delay_ms=1000, max_age_ms=3000):
    """Select first *observed* quote after latency, not decision-time quote.

    Reject gaps and stale observations. No look-ahead profit estimation.
    """
    if delay_ms < 0 or max_age_ms < 0:
        raise ValueError("Invalid timing")
    target = decision_ms + delay_ms
    for q in sorted(snapshots, key=lambda x: x.received_ms):
        if q.received_ms >= target:
            if q.received_ms - target > max_age_ms or not q.valid():
                return None
            return q
    return None
