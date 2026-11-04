"""Read-only Binance BTC/USDT trade feed. No trading API or wallet."""
import asyncio
import json
import time
from datetime import datetime, timezone

URL = "wss://stream.binance.com:9443/ws/btcusdt@trade"

async def monitor(on_trade, *, reconnect_seconds=3):
    import websockets
    while True:
        try:
            async with websockets.connect(URL, ping_interval=20, ping_timeout=20, max_queue=1000) as ws:
                async for raw in ws:
                    recv_ns = time.time_ns()
                    event = json.loads(raw)
                    if event.get("e") != "trade":
                        continue
                    record = {
                        "source": "binance",
                        "symbol": "BTCUSDT",
                        "price": float(event["p"]),
                        "quantity": float(event["q"]),
                        "exchange_event_ms": int(event["E"]),
                        "received_ms": recv_ns // 1_000_000,
                        "received_utc": datetime.fromtimestamp(recv_ns / 1e9, timezone.utc).isoformat(),
                    }
                    await on_trade(record)
        except (OSError, ConnectionError, TimeoutError, ValueError) as exc:
            print("Binance connection interrupted:", type(exc).__name__, flush=True)
        await asyncio.sleep(reconnect_seconds)

async def print_trade(record):
    print(json.dumps(record), flush=True)

if __name__ == "__main__":
    asyncio.run(monitor(print_trade))
