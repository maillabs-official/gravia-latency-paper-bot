# Gravia Latency Paper Bot

**PAPER ONLY / REAL OFF.** Initial simulator only; not yet a deployed live 24-hour monitor.

- Virtual balance: $50
- Virtual order: $5
- Execution delay: 1000 ms
- Maximum open positions: 2
- No wallet, private key, or real order endpoint.

Run `python -m unittest -v` and `python paper_engine.py`. GitHub Actions also runs these checks on push.

Next milestones: Binance public WebSocket reader; Polymarket public market data and contract metadata; event timestamps and latency measurements; delayed order book replay; realistic fees and partial fills; SQLite recovery; 24-hour server monitoring; Telegram alerts.

BTC spot price is not directly comparable to a YES/NO contract price. Virtual results are not realized profits.
