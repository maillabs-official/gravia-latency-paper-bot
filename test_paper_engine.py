import json
import unittest
import tempfile
from pathlib import Path
from paper_engine import PaperEngine

CFG = json.loads(Path(__file__).with_name('config.json').read_text())

class PaperTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state_path = Path(self.tmp.name) / 'state.json'
        self.e = PaperEngine(CFG, self.state_path)
    def test_initial_cash(self): self.assertEqual(self.e.cash, 20)
    def test_latency(self): self.assertFalse(self.e.buy('btc','YES',.5,elapsed_ms=999)[0])
    def test_stale(self): self.assertFalse(self.e.buy('btc','YES',.5,data_age_ms=3001)[0])
    def test_two_positions(self):
        self.assertTrue(self.e.buy('a','YES',.5)[0])
        self.assertTrue(self.e.buy('b','NO',.5)[0])
        self.assertFalse(self.e.buy('c','YES',.5)[0])
    def test_round_trip(self):
        self.assertTrue(self.e.buy('a','YES',.5)[0])
        self.assertTrue(self.e.sell('a','YES',.6)[0])
        self.assertAlmostEqual(self.e.cash, 21)
    def test_restart_no_topup(self):
        self.assertTrue(self.e.buy('a','YES',.5)[0])
        e2 = PaperEngine(CFG, self.state_path)
        self.assertEqual(e2.cash, 15)
        self.assertEqual(len(e2.positions), 1)
    def test_loss_persists_without_topup(self):
        self.assertTrue(self.e.buy('a','YES',.5)[0])
        self.assertTrue(self.e.sell('a','YES',.4)[0])
        restarted = PaperEngine(CFG, self.state_path)
        self.assertAlmostEqual(restarted.cash, 19)
        self.assertAlmostEqual(restarted.realized_pnl, -1)
    def test_no_automatic_topup_when_cash_insufficient(self):
        for name in ('a', 'b'):
            self.assertTrue(self.e.buy(name, 'YES', .5)[0])
        self.assertAlmostEqual(self.e.cash, 10)
        self.e.config = dict(CFG, order_size_usd=11)
        self.assertEqual(self.e.buy('c', 'YES', .5)[1], 'position limit')
        self.assertAlmostEqual(PaperEngine(CFG, self.state_path).cash, 10)

    def test_daily_loss_limit_blocks_new_buys(self):
        for i in range(5):
            name = str(i)
            self.assertTrue(self.e.buy(name, 'YES', .5)[0])
            self.assertTrue(self.e.sell(name, 'YES', .4)[0])
        self.assertAlmostEqual(self.e.realized_pnl, -5)
        self.assertFalse(self.e.buy('next', 'YES', .5)[0])
        self.assertFalse(PaperEngine(CFG, self.state_path).buy('next', 'YES', .5)[0])

    def test_no_real(self):
        bad=dict(CFG, real_trading_enabled=True)
        with self.assertRaises(ValueError): PaperEngine(bad)
    def test_depth(self): self.assertFalse(self.e.buy('a','YES',.5,available_shares=1)[0])

if __name__ == '__main__': unittest.main()
