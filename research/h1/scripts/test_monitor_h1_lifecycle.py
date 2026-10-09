#!/usr/bin/env python3
"""Deterministic lifecycle tests for the frozen H1 live monitor.

Uses temporary ledgers and synthetic completed H1 candles; never touches live data.
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

SCRIPT = Path(__file__).with_name("monitor_h1_live.py")
SPEC = importlib.util.spec_from_file_location("monitor_h1_live_under_test", SCRIPT)
MONITOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MONITOR)


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        MONITOR.ROOT = root
        MONITOR.STATE = root / "reports" / "h1_live_positions.csv"
        MONITOR.ALERTS = root / "reports" / "h1_live_alerts.csv"
        MONITOR.STATE.parent.mkdir(parents=True)
        pd.DataFrame(columns=MONITOR.POSCOL).to_csv(MONITOR.STATE, index=False)
        pd.DataFrame(columns=MONITOR.ALCOL).to_csv(MONITOR.ALERTS, index=False)
        self.times = pd.date_range("2026-10-09T00:00:00Z", periods=4, freq="h")
        self.bars = pd.DataFrame({
            "open": [100.0] * 4,
            "high": [100.5] * 4,
            "low": [99.5] * 4,
            "close": [100.1] * 4,
        }, index=self.times)
        self.bars.index.name = "timestamp"

    def fake_features(self, pair):
        return {
            "raw": self.bars.copy(), "h": self.bars.copy(), "ts": self.times[-1],
            "trend": False, "h4bull": False, "d1bull": False, "rsiup6": False,
        }

    def seed_open_trade(self, horizon=72):
        row = {
            "pair": "eurjpy", "direction": "long",
            "signal_time": self.times[0].isoformat(),
            "entry_time": self.times[0].isoformat(),
            "entry_price": 100.0, "tp": 101.0, "sl": 99.0,
            "horizon": horizon, "status": "OPEN",
            "last_checked": self.times[0].isoformat(),
        }
        pd.DataFrame([row], columns=MONITOR.POSCOL).to_csv(MONITOR.STATE, index=False)

    def run_monitor(self):
        with patch.object(MONITOR, "features", side_effect=self.fake_features), \
             patch.object(MONITOR, "signal", return_value=False):
            MONITOR.main()

    def test_htf_prior_uses_latest_candle_closed_by_signal_time(self):
        # H4 candle timestamps label OPEN. At 11:00, the 08:00 candle is
        # still forming, so the 04:00 candle is the latest completed one.
        h4_index = pd.to_datetime([
            "2026-10-09T00:00:00Z",
            "2026-10-09T04:00:00Z",
            "2026-10-09T08:00:00Z",
        ], utc=True)
        h4 = pd.DataFrame({"open": [1, 2, 3], "close": [2, 3, 4]}, index=h4_index)
        before_close = MONITOR.htf_prior(h4, pd.Timestamp("2026-10-09T11:00:00Z"), "h4")
        at_close = MONITOR.htf_prior(h4, pd.Timestamp("2026-10-09T12:00:00Z"), "h4")
        self.assertEqual(float(before_close["open"]), 2.0)
        self.assertEqual(float(at_close["open"]), 3.0)

    def test_d1_prior_does_not_depend_on_partial_daily_row_existing(self):
        # If aggregation omits the current partial D1 row, yesterday's fully
        # completed candle must still be selected rather than skipped.
        d1_index = pd.to_datetime([
            "2026-10-07T00:00:00Z",
            "2026-10-08T00:00:00Z",
        ], utc=True)
        d1 = pd.DataFrame({"open": [1, 2], "close": [2, 3]}, index=d1_index)
        prior = MONITOR.htf_prior(d1, pd.Timestamp("2026-10-09T08:00:00Z"), "d1")
        self.assertEqual(float(prior["open"]), 2.0)

    def test_same_bar_tp_sl_uses_sl_and_closed_trade_persists(self):
        self.seed_open_trade()
        self.bars.loc[self.times[1], "high"] = 101.2
        self.bars.loc[self.times[1], "low"] = 98.8
        self.run_monitor()
        positions = pd.read_csv(MONITOR.STATE)
        alerts = pd.read_csv(MONITOR.ALERTS)
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions.iloc[0]["status"], "CLOSED")
        self.assertEqual(alerts.iloc[0]["kind"], "EXIT_SL")
        self.run_monitor()
        positions_again = pd.read_csv(MONITOR.STATE)
        alerts_again = pd.read_csv(MONITOR.ALERTS)
        self.assertEqual(len(positions_again), 1, "closed trade must remain in state ledger")
        self.assertEqual(len(alerts_again), 1, "rerun must not duplicate exit alert")

    def test_catches_tp_on_intermediate_bar_after_missed_run(self):
        self.seed_open_trade()
        self.bars.loc[self.times[1], "high"] = 101.2
        # Latest evaluated candle is time[3], but TP happened at time[1].
        self.run_monitor()
        alerts = pd.read_csv(MONITOR.ALERTS)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts.iloc[0]["kind"], "EXIT_TP")
        self.assertEqual(float(alerts.iloc[0]["price"]), 101.0)

    def test_time_exit_occurs_at_horizon_bar_close(self):
        self.seed_open_trade(horizon=2)
        self.bars.loc[self.times[2], "close"] = 100.25
        self.run_monitor()
        alerts = pd.read_csv(MONITOR.ALERTS)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts.iloc[0]["kind"], "EXIT_TIME")
        self.assertAlmostEqual(float(alerts.iloc[0]["price"]), 100.25)


if __name__ == "__main__":
    unittest.main(verbosity=2)
