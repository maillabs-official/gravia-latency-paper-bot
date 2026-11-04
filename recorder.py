"""Append-only JSONL recorder for market-data observations (no trading)."""
import json
from pathlib import Path

class JsonlRecorder:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    async def record(self, event):
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, separators=(",", ":"), ensure_ascii=False) + chr(10))
