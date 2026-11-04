"""Conservative no-wallet paper position simulator."""
from dataclasses import dataclass
import json
from pathlib import Path

@dataclass
class Position:
    market: str
    side: str
    shares: float
    entry: float
    cost: float

class PaperEngine:
    def __init__(self, config):
        if config.get('mode') != 'PAPER_ONLY' or config.get('real_trading_enabled') is not False:
            raise ValueError('PAPER_ONLY and REAL OFF required')
        self.config = config
        self.cash = float(config['starting_balance_usd'])
        self.positions = []
        self.realized_pnl = 0.0
        self.day_start_pnl = 0.0

    def buy(self, market, side, ask_price, *, data_age_ms=0, elapsed_ms=1000, available_shares=float('inf'), fee_usd=0.0):
        if data_age_ms > self.config['max_data_age_ms']:
            return False, 'stale data'
        if elapsed_ms < self.config['execution_delay_ms']:
            return False, 'latency not elapsed'
        if len(self.positions) >= self.config['max_open_positions']:
            return False, 'position limit'
        if self.realized_pnl - self.day_start_pnl <= -self.config['daily_loss_limit_usd']:
            return False, 'daily loss limit'
        if not (0 < ask_price < 1):
            return False, 'invalid contract price'
        cost = float(self.config['order_size_usd'])
        if cost + fee_usd > self.cash:
            return False, 'insufficient virtual cash'
        shares = cost / ask_price
        if shares > available_shares:
            return False, 'insufficient order book depth'
        self.cash -= cost + fee_usd
        self.positions.append(Position(market, side, shares, ask_price, cost + fee_usd))
        return True, 'paper fill'

    def sell(self, market, side, bid_price, *, available_shares=float('inf'), fee_usd=0.0):
        pos = next((p for p in self.positions if p.market == market and p.side == side), None)
        if pos is None:
            return False, 'position missing'
        if not (0 <= bid_price <= 1) or available_shares < pos.shares:
            return False, 'invalid price or insufficient depth'
        proceeds = pos.shares * bid_price - fee_usd
        self.cash += proceeds
        self.realized_pnl += proceeds - pos.cost
        self.positions.remove(pos)
        return True, 'paper close'

if __name__ == '__main__':
    cfg = json.loads(Path(__file__).with_name('config.json').read_text())
    engine = PaperEngine(cfg)
    print({'mode': cfg['mode'], 'cash_usd': engine.cash, 'open_positions': len(engine.positions), 'real_trading': False})
