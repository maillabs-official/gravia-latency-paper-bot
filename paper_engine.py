"""PAPER ONLY virtual engine. Atomic local state; never top up on restart."""
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import os
import tempfile
from datetime import datetime, timezone

@dataclass
class Position:
    market: str
    side: str
    shares: float
    entry: float
    cost: float

class PaperEngine:
    def __init__(self, config, state_path="paper_state.json"):
        if config.get("mode") != "PAPER_ONLY" or config.get("real_trading_enabled") is not False:
            raise ValueError("PAPER_ONLY and REAL OFF required")
        if float(config["starting_balance_usd"]) != 20:
            raise ValueError("Fixed initial virtual capital must be $20")
        self.config = config
        self.path = Path(state_path)
        if self.path.exists():
            data = json.loads(self.path.read_text())
            if data.get("initial_capital") != 20 or data.get("mode") != "PAPER_ONLY":
                raise ValueError("Invalid persistent state")
            self.cash = float(data["cash"])
            self.positions = [Position(**p) for p in data["positions"]]
            self.realized_pnl = float(data["realized_pnl"])
            self.day = data["day"]
            self.day_start_pnl = float(data["day_start_pnl"])
        else:
            self.cash = 20.0
            self.positions = []
            self.realized_pnl = 0.0
            self.day = datetime.now(timezone.utc).date().isoformat()
            self.day_start_pnl = 0.0
            self._save()

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        state = dict(mode="PAPER_ONLY", initial_capital=20, cash=self.cash,
                     positions=[asdict(p) for p in self.positions],
                     realized_pnl=self.realized_pnl, day=self.day,
                     day_start_pnl=self.day_start_pnl)
        fd, tmp = tempfile.mkstemp(dir=str(self.path.parent), prefix=".paper-")
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(state, f)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    def _refresh_day(self):
        today = datetime.now(timezone.utc).date().isoformat()
        if self.day != today:
            self.day = today
            self.day_start_pnl = self.realized_pnl
            self._save()

    def buy(self, market, side, ask_price, *, data_age_ms=0, elapsed_ms=1000,
            available_shares=float("inf"), fee_usd=0.0):
        self._refresh_day()
        if data_age_ms > self.config["max_data_age_ms"]:
            return False, "stale data"
        if elapsed_ms < self.config["execution_delay_ms"]:
            return False, "latency not elapsed"
        if len(self.positions) >= self.config["max_open_positions"]:
            return False, "position limit"
        if self.realized_pnl - self.day_start_pnl <= -self.config["daily_loss_limit_usd"]:
            return False, "daily loss limit"
        if not (0 < ask_price < 1) or fee_usd < 0:
            return False, "invalid price or fee"
        cost = float(self.config["order_size_usd"])
        if cost + fee_usd > self.cash:
            return False, "insufficient virtual cash"
        shares = cost / ask_price
        if shares > available_shares:
            return False, "insufficient order book depth"
        self.cash -= cost + fee_usd
        self.positions.append(Position(market, side, shares, ask_price, cost + fee_usd))
        self._save()
        return True, "paper fill"

    def sell(self, market, side, bid_price, *, available_shares=float("inf"), fee_usd=0.0):
        pos = next((p for p in self.positions if p.market == market and p.side == side), None)
        if pos is None:
            return False, "position missing"
        if not (0 <= bid_price <= 1) or fee_usd < 0 or available_shares < pos.shares:
            return False, "invalid price, fee or depth"
        proceeds = pos.shares * bid_price - fee_usd
        if proceeds < 0:
            return False, "fee exceeds proceeds"
        self.cash += proceeds
        self.realized_pnl += proceeds - pos.cost
        self.positions.remove(pos)
        self._save()
        return True, "paper close"

if __name__ == "__main__":
    cfg = json.loads(Path(__file__).with_name("config.json").read_text())
    engine = PaperEngine(cfg)
    print({"mode": "PAPER_ONLY", "cash_usd": engine.cash,
           "open_positions": len(engine.positions), "real_trading": False})
