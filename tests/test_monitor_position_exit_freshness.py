#!/usr/bin/env python3
"""Regression tests for completed-H4 exit-monitor freshness and weekend handling."""
import importlib.util
from pathlib import Path
from unittest.mock import patch
import unittest
import pandas as pd

SPEC=importlib.util.spec_from_file_location("monitor_position_exit",Path("scripts/monitor_position_exit.py"))
MONITOR=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MONITOR)

class ExitFreshnessTests(unittest.TestCase):
    def market(self, timestamps):
        return pd.DataFrame({
            "timestamp": pd.to_datetime(timestamps,utc=True),
            "open":[1.0]*len(timestamps),"high":[1.1]*len(timestamps),
            "low":[0.9]*len(timestamps),"close":[1.0]*len(timestamps),
        })

    def test_weekend_does_not_allow_week_old_market_data(self):
        now=pd.Timestamp("2026-10-10T12:00:00Z")  # Saturday
        stale=self.market(["2026-10-02T16:00:00Z"])
        with patch.object(MONITOR.d,"load_market",return_value=stale):
            with self.assertRaisesRegex(RuntimeError,"stale"):
                MONITOR.completed_market("usdcad",now=now)

    def test_weekend_uses_friday_last_completed_h4_and_excludes_20utc_partial(self):
        now=pd.Timestamp("2026-10-10T12:00:00Z")
        data=self.market(["2026-10-09T16:00:00Z","2026-10-09T20:00:00Z"])
        with patch.object(MONITOR.d,"load_market",return_value=data):
            closed=MONITOR.completed_market("usdcad",now=now)
        self.assertEqual(len(closed),1)
        self.assertEqual(pd.Timestamp(closed.timestamp.iloc[-1]),pd.Timestamp("2026-10-09T16:00:00Z"))

    def test_open_market_stale_data_returns_unknown_not_hold(self):
        now=pd.Timestamp("2026-10-12T12:00:00Z")  # Monday
        stale=self.market(["2026-10-09T16:00:00Z"])
        with patch.object(MONITOR.d,"load_market",return_value=stale):
            with self.assertRaisesRegex(RuntimeError,"stale"):
                MONITOR.completed_market("usdcad",now=now)

if __name__=="__main__":
    unittest.main(verbosity=2)
