"""Tests for strict read-only monitoring and JSONL capture."""
import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from recorder import JsonlRecorder
from monitor import run

class MonitorTests(unittest.TestCase):
    def test_recorder_writes_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            recorder = JsonlRecorder(path)
            asyncio.run(recorder.record({"source": "binance", "price": 1}))
            asyncio.run(recorder.record({"source": "polymarket", "event": {}}))
            rows = [json.loads(x) for x in path.read_text().splitlines()]
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[1]["source"], "polymarket")

    def test_monitor_is_paper_only(self):
        import inspect
        src = inspect.getsource(run)
        self.assertNotIn("place_order", src)
        self.assertNotIn("private_key", src)

if __name__ == "__main__":
    unittest.main()
