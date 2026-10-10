#!/usr/bin/env python3
"""Regression tests for live H1-to-H4/D1 UTC candle aggregation."""
import importlib.util
import unittest
import warnings
from pathlib import Path

import pandas as pd

SCRIPT = Path(__file__).resolve().parents[1] / "research" / "h1" / "scripts" / "download_htf_live.py"
SPEC = importlib.util.spec_from_file_location("download_htf_live_test", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class LiveHTFResampleTests(unittest.TestCase):
    def setUp(self):
        idx = pd.date_range("2026-10-01T00:00:00Z", periods=72, freq="h")
        self.h1 = pd.DataFrame({
            "open": [1.0 + i * 0.001 for i in range(len(idx))],
            "high": [1.1 + i * 0.001 for i in range(len(idx))],
            "low": [0.9 + i * 0.001 for i in range(len(idx))],
            "close": [1.05 + i * 0.001 for i in range(len(idx))],
            "volume": [10.0] * len(idx),
        }, index=idx)


    def test_weekend_h1_source_accepts_friday_close(self):
        now = pd.Timestamp("2026-10-10T04:00:00Z")
        latest = pd.Timestamp("2026-10-09T20:00:00Z")
        MODULE.validate_h1_source_freshness("audnzd", latest, now)

    def test_weekend_h1_source_rejects_data_too_old_for_friday_close(self):
        now = pd.Timestamp("2026-10-10T04:00:00Z")
        latest = pd.Timestamp("2026-10-09T18:00:00Z")
        with self.assertRaisesRegex(RuntimeError, "stale during weekly closure"):
            MODULE.validate_h1_source_freshness("audnzd", latest, now)

    def test_open_market_h1_source_still_rejects_stale_data(self):
        now = pd.Timestamp("2026-10-08T12:30:00Z")
        latest = pd.Timestamp("2026-10-08T09:00:00Z")
        with self.assertRaisesRegex(RuntimeError, "stale before HTF aggregation"):
            MODULE.validate_h1_source_freshness("audnzd", latest, now)

    def test_weekend_h4_accepts_fridays_last_completed_candle(self):
        now = pd.Timestamp("2026-10-10T04:00:00Z")
        latest = pd.Timestamp("2026-10-09T16:00:00Z")
        MODULE.validate_htf_freshness("audnzd", "h4", latest, now)

    def test_weekend_h4_rejects_candle_older_than_fridays_last_complete(self):
        now = pd.Timestamp("2026-10-10T04:00:00Z")
        latest = pd.Timestamp("2026-10-09T12:00:00Z")
        with self.assertRaisesRegex(RuntimeError, "predates weekly close"):
            MODULE.validate_htf_freshness("audnzd", "h4", latest, now)

    def test_open_market_h4_still_rejects_stale_data(self):
        now = pd.Timestamp("2026-10-12T12:00:00Z")
        latest = pd.Timestamp("2026-10-09T16:00:00Z")
        with self.assertRaisesRegex(RuntimeError, "latest fully closed candle is stale"):
            MODULE.validate_htf_freshness("audnzd", "h4", latest, now)

    def test_daily_resampling_has_no_ineffective_offset_warnings(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            out = MODULE.aggregate(self.h1, "d1")
        self.assertFalse(
            [str(w.message) for w in caught if "offset" in str(w.message).lower() or "origin" in str(w.message).lower()],
            "D1 resampling should not emit ineffective origin/offset warnings",
        )
        stamps = pd.to_datetime(out.timestamp, unit="ms", utc=True)
        self.assertTrue(all(ts.hour == 0 for ts in stamps))
        self.assertGreaterEqual(len(out), 3)

    def test_h4_resampling_is_aligned_to_utc_four_hour_boundaries(self):
        out = MODULE.aggregate(self.h1, "h4")
        stamps = pd.to_datetime(out.timestamp, unit="ms", utc=True)
        self.assertTrue(all(ts.hour in {0, 4, 8, 12, 16, 20} for ts in stamps))
        self.assertGreaterEqual(len(out), 18)


if __name__ == "__main__":
    unittest.main(verbosity=2)
