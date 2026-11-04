import json
import unittest
from pathlib import Path
from paper_engine import PaperEngine

CFG = json.loads(Path(__file__).with_name('config.json').read_text())

class PaperTests(unittest.TestCase):
    def setUp(self): self.e = PaperEngine(CFG)
    def test_initial_cash(self): self.assertEqual(self.e.cash, 50)
    def test_latency(self): self.assertFalse(self.e.buy('btc','YES',.5,elapsed_ms=999)[0])
    def test_stale(self): self.assertFalse(self.e.buy('btc','YES',.5,data_age_ms=3001)[0])
    def test_two_positions(self):
        self.assertTrue(self.e.buy('a','YES',.5)[0])
        self.assertTrue(self.e.buy('b','NO',.5)[0])
        self.assertFalse(self.e.buy('c','YES',.5)[0])
    def test_round_trip(self):
        self.assertTrue(self.e.buy('a','YES',.5)[0])
        self.assertTrue(self.e.sell('a','YES',.6)[0])
        self.assertAlmostEqual(self.e.cash, 51)
    def test_no_real(self):
        bad=dict(CFG, real_trading_enabled=True)
        with self.assertRaises(ValueError): PaperEngine(bad)
    def test_depth(self): self.assertFalse(self.e.buy('a','YES',.5,available_shares=1)[0])

if __name__ == '__main__': unittest.main()
