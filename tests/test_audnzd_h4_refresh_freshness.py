#!/usr/bin/env python3
"""Regression tests for AUDNZD H4 freshness across the weekly FX closure."""
import importlib.util
from datetime import datetime, timezone
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "refresh_audnzd_h4_exit", ROOT / "scripts" / "refresh_audnzd_h4_exit.py"
)
REFRESH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REFRESH)


class AudnzdH4FreshnessTests(unittest.TestCase):
    def test_weekend_accepts_fridays_last_complete_h4_candle(self):
        now = datetime(2026, 10, 10, 3, 35, tzinfo=timezone.utc)
        latest = datetime(2026, 10, 9, 16, 0, tzinfo=timezone.utc)
        REFRESH.validate_freshness(latest, now)

    def test_weekend_rejects_data_older_than_fridays_last_complete_h4_candle(self):
        now = datetime(2026, 10, 10, 3, 35, tzinfo=timezone.utc)
        latest = datetime(2026, 10, 9, 12, 0, tzinfo=timezone.utc)
        with self.assertRaisesRegex(RuntimeError, "predates weekly close"):
            REFRESH.validate_freshness(latest, now)

    def test_open_market_still_rejects_stale_h4_data(self):
        now = datetime(2026, 10, 12, 12, 0, tzinfo=timezone.utc)
        latest = datetime(2026, 10, 9, 16, 0, tzinfo=timezone.utc)
        with self.assertRaisesRegex(RuntimeError, "too old during open market"):
            REFRESH.validate_freshness(latest, now)


if __name__ == "__main__":
    unittest.main(verbosity=2)
