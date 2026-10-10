#!/usr/bin/env python3
"""Regression tests for AUD/NZD H4 exit-monitor freshness around weekly closure."""
import importlib.util
import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SPEC = importlib.util.spec_from_file_location(
    "monitor_audnzd_h4_exit", ROOT / "scripts" / "monitor_audnzd_h4_exit.py"
)
MONITOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MONITOR)


class AudnzdH4MonitorFreshnessTests(unittest.TestCase):
    def test_weekend_accepts_fridays_last_completed_h4_candle_after_eight_hours(self):
        now = pd.Timestamp("2026-10-10T08:30:00Z")
        latest = pd.Timestamp("2026-10-09T16:00:00Z")
        MONITOR.validate_h4_freshness(latest, now)

    def test_weekend_rejects_h4_data_older_than_fridays_last_complete_candle(self):
        now = pd.Timestamp("2026-10-10T08:30:00Z")
        latest = pd.Timestamp("2026-10-09T12:00:00Z")
        with self.assertRaisesRegex(RuntimeError, "predates weekly close"):
            MONITOR.validate_h4_freshness(latest, now)

    def test_open_market_still_rejects_stale_h4_data(self):
        now = pd.Timestamp("2026-10-12T12:30:00Z")
        latest = pd.Timestamp("2026-10-09T16:00:00Z")
        with self.assertRaisesRegex(RuntimeError, "data stale"):
            MONITOR.validate_h4_freshness(latest, now)

    def test_open_market_accepts_recent_completed_h4_candle(self):
        now = pd.Timestamp("2026-10-12T12:30:00Z")
        latest = pd.Timestamp("2026-10-12T04:00:00Z")
        MONITOR.validate_h4_freshness(latest, now)


if __name__ == "__main__":
    unittest.main(verbosity=2)
