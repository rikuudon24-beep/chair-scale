#!/usr/bin/env python3
"""Regression tests for guarded H1 research cache fallback."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

import pandas as pd

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "download_h1_research_data.py"
SPEC = importlib.util.spec_from_file_location("download_h1_research_data_cache_test", SCRIPT)
DATA = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DATA)


class H1CacheFallbackTests(unittest.TestCase):
    def write_cache(self, root, latest):
        DATA.OUT = root
        root.mkdir(exist_ok=True)
        times = [(latest - pd.Timedelta(hours=i)).timestamp() * 1000 for i in range(1000)]
        pd.DataFrame({
            "timestamp": times, "open": [1.0] * 1000, "high": [1.2] * 1000,
            "low": [0.9] * 1000, "close": [1.1] * 1000, "volume": [0] * 1000,
        }).to_csv(root / "usdjpy.csv", index=False)

    def test_recent_valid_cache_is_usable(self):
        with tempfile.TemporaryDirectory() as td:
            now = pd.Timestamp.now(tz="UTC").floor("h")
            self.write_cache(Path(td), now)
            usable, reason = DATA.cached_data_is_usable("usdjpy", now=now)
            self.assertTrue(usable, reason)

    def test_stale_cache_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            now = pd.Timestamp.now(tz="UTC")
            self.write_cache(Path(td), now - pd.Timedelta(days=20))
            usable, reason = DATA.cached_data_is_usable("usdjpy", now=now)
            self.assertFalse(usable)
            self.assertIn("exceeds", reason)


if __name__ == "__main__":
    unittest.main(verbosity=2)
