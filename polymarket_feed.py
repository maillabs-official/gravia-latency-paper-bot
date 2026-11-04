"""Read-only Polymarket CLOB market data. No orders, signing or credentials.

Token IDs must be taken from verified market metadata and resolution rules.
Do not compare BTC spot prices directly with YES/NO probabilities.
"""
import asyncio
import json
import time

WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"

async def monitor(token_ids, on_event, *, reconnect_seconds=3):
    if not token_ids or not all(isinstance(x, str) and x.isdigit() for x in token_ids):
        raise ValueError("Supply validated Polymarket CLOB token IDs")
    import websockets
    while True:
        try:
            async with websockets.connect(WS_URL, ping_interval=None, max_queue=1000) as ws:
                await ws.send(json.dumps({"assets_ids": token_ids, "type": "market"}))
                async def heartbeat():
                    while True:
                        await asyncio.sleep(10)
                        await ws.send("PING")
                task = asyncio.create_task(heartbeat())
                try:
                    async for raw in ws:
                        if raw in ("PONG", "PING"):
                            continue
                        recv_ms = time.time_ns() // 1_000_000
                        try:
                            payload = json.loads(raw)
                        except json.JSONDecodeError:
                            continue
                        for item in payload if isinstance(payload, list) else [payload]:
                            if isinstance(item, dict):
                                await on_event({"source": "polymarket", "received_ms": recv_ms, "event": item})
                finally:
                    task.cancel()
        except (OSError, ConnectionError, TimeoutError, ValueError) as exc:
            print("Polymarket feed interrupted:", type(exc).__name__, flush=True)
        await asyncio.sleep(reconnect_seconds)

async def print_event(event):
    print(json.dumps(event), flush=True)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("token_ids", nargs="+", help="Verified CLOB token IDs")
    args = parser.parse_args()
    asyncio.run(monitor(args.token_ids, print_event))
