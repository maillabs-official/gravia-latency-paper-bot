"""Strictly read-only dual-feed capture; no paper fills from raw spot ticks.

Usage: python monitor.py --token-id VERIFIED_CLOB_TOKEN_ID --seconds 60
Requires a verified BTC market token ID; never guesses markets or resolution.
"""
import argparse
import asyncio
import json
import signal
import time
from pathlib import Path

from binance_feed import monitor as binance_monitor
from polymarket_feed import monitor as polymarket_monitor
from recorder import JsonlRecorder

async def run(token_ids, seconds, output):
    recorder = JsonlRecorder(output)
    counts = {"binance": 0, "polymarket": 0}
    lock = asyncio.Lock()
    start = time.monotonic()

    async def capture(event):
        source = event.get("source")
        if source not in counts:
            return
        async with lock:
            await recorder.record(event)
            counts[source] += 1

    tasks = [asyncio.create_task(binance_monitor(capture), name="binance"),
             asyncio.create_task(polymarket_monitor(token_ids, capture), name="polymarket")]
    try:
        await asyncio.sleep(seconds)
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
    return {"duration_s": round(time.monotonic() - start, 3), "counts": counts, "file": str(output), "paper_only": True}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token-id", action="append", required=True, help="Verified CLOB token ID; repeatable")
    parser.add_argument("--seconds", type=int, default=60)
    parser.add_argument("--output", default="data/observations.jsonl")
    args = parser.parse_args()
    if args.seconds <= 0 or args.seconds > 86400:
        parser.error("--seconds must be between 1 and 86400")
    if not all(x.isdigit() for x in args.token_id):
        parser.error("token IDs must be decimal strings")
    print(json.dumps(asyncio.run(run(args.token_id, args.seconds, Path(args.output)))), flush=True)

if __name__ == "__main__":
    main()
