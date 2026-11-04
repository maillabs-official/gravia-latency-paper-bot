import unittest
from execution_model import Quote, delayed_buy_quote

class ExecutionTests(unittest.TestCase):
    def test_delayed_quote_not_decision_quote(self):
        a = Quote("123", 1000, .40, 20, .39, 20)
        b = Quote("123", 2000, .55, 20, .54, 20)
        self.assertEqual(delayed_buy_quote(1000, [a,b], 1000).ask, .55)
    def test_no_future_data(self):
        q = Quote("123", 1999, .5, 20, .49, 20)
        self.assertIsNone(delayed_buy_quote(1000, [q], 1000))
    def test_stale_quote(self):
        q = Quote("123", 5100, .5, 20, .49, 20)
        self.assertIsNone(delayed_buy_quote(1000, [q], 1000, 3000))
    def test_crossed_book_rejected(self):
        q = Quote("123", 2000, .40, 20, .50, 20)
        self.assertIsNone(delayed_buy_quote(1000, [q], 1000))

if __name__ == "__main__": unittest.main()
