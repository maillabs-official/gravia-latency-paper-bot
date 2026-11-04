"""Read-only Polymarket Gamma discovery: candidates require manual resolution verification.

Never auto-select contracts for execution: title/metadata alone cannot prove
that Binance BTC/USDT is the settlement oracle or that timing aligns.
"""
import argparse
import json
import urllib.parse
import urllib.request

API = "https://gamma-api.polymarket.com/markets"

def discover(limit=100):
    if not 1 <= limit <= 500:
        raise ValueError("limit must be 1..500")
    url = API + "?" + urllib.parse.urlencode({"active": "true", "closed": "false", "limit": limit})
    req = urllib.request.Request(url, headers={"User-Agent": "GraviaPaperResearch/1.0"})
    with urllib.request.urlopen(req, timeout=15) as response:
        markets = json.load(response)
    if not isinstance(markets, list):
        raise ValueError("Unexpected Gamma response")
    candidates = []
    for market in markets:
        if not isinstance(market, dict):
            continue
        title = str(market.get("question", ""))
        text = title.lower()
        if not ("bitcoin" in text or "btc" in text):
            continue
        tokens = market.get("clobTokenIds", [])
        if isinstance(tokens, str):
            try:
                tokens = json.loads(tokens)
            except json.JSONDecodeError:
                tokens = []
        if not isinstance(tokens, list) or not tokens or not all(isinstance(t, str) and t.isdigit() for t in tokens):
            continue
        candidates.append({
            "question": title,
            "slug": market.get("slug"),
            "condition_id": market.get("conditionId"),
            "clob_token_ids": tokens,
            "end_date": market.get("endDate"),
            "resolution_source": market.get("resolutionSource"),
            "verified_for_trading": False,
        })
    return candidates

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=100)
    args = p.parse_args()
    print(json.dumps({"candidates": discover(args.limit), "warning": "Manual resolution/oracle verification required; never auto-trade."}, indent=2))
