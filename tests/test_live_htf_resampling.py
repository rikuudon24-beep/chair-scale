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
