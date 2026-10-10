#!/usr/bin/env python3
"""Regression tests for H1 download validation and source-overlap safeguards."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
LIVE_PATH = ROOT / "research" / "h1" / "scripts" / "download_h1_live.py"
DATA_PATH = ROOT / "scripts" / "download_h1_research_data.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LIVE = load_module("download_h1_live_test", LIVE_PATH)
DATA = load_module("download_h1_research_data_test", DATA_PATH)


class H1OverlapTests(unittest.TestCase):
    def test_weekend_freshness_accepts_last_completed_friday_candle(self):
        now = pd.Timestamp("2026-10-10T00:00:00Z")  # Saturday UTC
        latest = pd.Timestamp("2026-10-09T20:00:00Z")
        LIVE.validate_freshness(latest, now=now)

    def test_weekend_freshness_rejects_data_older_than_session_close(self):
        now = pd.Timestamp("2026-10-10T00:00:00Z")
        latest = pd.Timestamp("2026-10-09T18:00:00Z")
        with self.assertRaisesRegex(RuntimeError, "stale during market closure"):
            LIVE.validate_freshness(latest, now=now)

    def test_open_market_freshness_still_rejects_stale_data(self):
        now = pd.Timestamp("2026-10-08T12:30:00Z")  # Thursday UTC
        latest = pd.Timestamp("2026-10-08T09:00:00Z")
        with self.assertRaisesRegex(RuntimeError, "stale during open market"):
            LIVE.validate_freshness(latest, now=now)

    def test_monitor_weekend_freshness_accepts_friday_close(self):
        monitor = load_module("monitor_h1_live_test", ROOT / "research" / "h1" / "scripts" / "monitor_h1_live.py")
        monitor.validate_h1_freshness(pd.Timestamp("2026-10-09T20:00:00Z"), pd.Timestamp("2026-10-10T00:00:00Z"))

    def test_monitor_open_market_still_rejects_stale_data(self):
        monitor = load_module("monitor_h1_live_test_open", ROOT / "research" / "h1" / "scripts" / "monitor_h1_live.py")
        with self.assertRaisesRegex(RuntimeError, "stale H1 data during open market"):
            monitor.validate_h1_freshness(pd.Timestamp("2026-10-08T09:00:00Z"), pd.Timestamp("2026-10-08T12:30:00Z"))

    def test_no_overlap_fails_closed(self):
        now_ms = int(pd.Timestamp.now(tz="UTC").timestamp() * 1000)
        old = pd.DataFrame({"timestamp": [now_ms - 30 * 24 * 3600 * 1000], "close": [1.0]})
        fresh = pd.DataFrame({"timestamp": [now_ms], "close": [1.0]})
        with self.assertRaisesRegex(RuntimeError, "no timestamp overlap"):
            LIVE.validate_overlap("eurjpy", old, fresh)

    def test_seven_day_overlap_accepts_sufficient_bars(self):
        now_ms = int(pd.Timestamp.now(tz="UTC").timestamp() * 1000)
        times = [now_ms - k * 3600 * 1000 for k in range(40, 0, -1)]
        old = pd.DataFrame({"timestamp": times, "close": [1.0] * len(times)})
        fresh = old.copy()
        with patch.object(LIVE, "OVERLAP_HOURS", 168):
            LIVE.validate_overlap("eurjpy", old, fresh)


class H1DownloadIntegrityTests(unittest.TestCase):
    def test_empty_csv_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "empty.csv"
            path.write_text("", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "empty download file"):
                DATA.read_valid_csv(path)

    def test_malformed_schema_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad.csv"
            path.write_text("timestamp,open,close\n1,1.0,1.1\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "missing columns"):
                DATA.read_valid_csv(path)

    def test_invalid_download_does_not_replace_existing_cache(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            DATA.OUT = root / "out"
            DATA.OUT.mkdir()
            final = DATA.OUT / "usdjpy.csv"
            final.write_text(
                "timestamp,open,high,low,close,volume\n1,1.0,1.2,0.9,1.1,0\n",
                encoding="utf-8",
            )
            bad = root / "empty.csv"
            bad.write_text("", encoding="utf-8")
            before = final.read_text(encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "no valid download CSVs"):
                DATA.merge("usdjpy", [bad])
            self.assertEqual(final.read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
