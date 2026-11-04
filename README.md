# GRAVIA LATENCY PAPER BOT

**PAPER ONLY • REAL OFF • No wallet or real orders**

Configuration: $20 virtual capital, $5 virtual order, 1,000 ms simulated latency, maximum 2 positions, $5 daily realized loss stop. See `config.json`.

## Included
- `binance_feed.py`: public BTCUSDT trade WebSocket reader
- `polymarket_feed.py`: public CLOB market WebSocket reader; requires verified token IDs
- `discover_markets.py`: public Gamma BTC candidate discovery, **not** oracle verification
- `monitor.py`: dual-feed capture to JSONL (no trades)
- `recorder.py`: append-only observation recorder
- `execution_model.py`: delayed quote selection from observed book snapshots
- `paper_engine.py`: bounded virtual balance and positions
- `test_*.py`: unit tests; GitHub Actions tests on push

## Local setup
```sh
python -m pip install -r requirements.txt
python -m unittest -v
python paper_engine.py
python discover_markets.py --limit 100
python monitor.py --token-id VERIFIED_CLOB_TOKEN_ID --seconds 60
```

**Important limitations:** These modules are building blocks, not a proven latency-arbitrage trading system. BTC spot ticks are not interchangeable with Polymarket YES/NO contract probabilities. Before a valid paper-trade signal, verify each contract's resolution oracle, strike, expiry, and market structure, then implement a tested probability/edge model and live order-book parser. No real 24-hour deployment, verified profitability, or live end-to-end integration is claimed. GitHub Actions is not a persistent 24-hour WebSocket server. Use a suitable always-on host only after validation. Never provide wallet credentials.
