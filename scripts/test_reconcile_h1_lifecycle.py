#!/usr/bin/env python3
"""Synthetic adapter tests for H1 -> shared lifecycle ledger; no network/live data."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

SCRIPT = Path(__file__).with_name("reconcile_h1_lifecycle.py")
SPEC = importlib.util.spec_from_file_location("reconcile_h1_lifecycle_under_test", SCRIPT)
ADAPTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ADAPTER)


class H1AdapterTests(unittest.TestCase):
    def test_entry_and_exit_are_reconciled_with_stable_trade_id(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            reports = root / "reports"
            reports.mkdir()
            ADAPTER.ROOT = root
            ADAPTER.POSITIONS = reports / "h1_live_positions.csv"
            ADAPTER.ALERTS = reports / "h1_live_alerts.csv"
            ADAPTER.TRADES = reports / "fx_trade_lifecycle.csv"
            ADAPTER.OUTBOX = reports / "fx_notification_outbox.csv"
            signal = "2026-10-09T00:00:00+00:00"
            entry = "2026-10-09T01:00:00+00:00"
            exit_time = "2026-10-09T02:00:00+00:00"
            pd.DataFrame([{
                "pair":"eurjpy", "direction":"long", "signal_time":signal,
                "entry_time":entry, "entry_price":160.0, "tp":161.0, "sl":159.6,
                "horizon":72, "status":"CLOSED", "last_checked":exit_time,
            }]).to_csv(ADAPTER.POSITIONS, index=False)
            pd.DataFrame([
                {"alert_id":"ENTRY|eurjpy|"+signal, "kind":"ENTRY", "pair":"eurjpy",
                 "direction":"long", "signal_time":signal, "entry_time":entry,
                 "price":160.0, "tp":161.0, "sl":159.6, "message":"entry"},
                {"alert_id":"EXIT_TP|eurjpy|"+signal, "kind":"EXIT_TP", "pair":"eurjpy",
                 "direction":"long", "signal_time":signal, "entry_time":entry,
                 "price":161.0, "tp":161.0, "sl":159.6, "message":"exit"},
            ]).to_csv(ADAPTER.ALERTS, index=False)
            with patch.object(ADAPTER, "now", create=True):
                ADAPTER.main()
            trades = pd.read_csv(ADAPTER.TRADES)
            events = pd.read_csv(ADAPTER.OUTBOX)
            self.assertEqual(len(trades), 1)
            self.assertEqual(trades.iloc[0]["status"], "CLOSED")
            self.assertEqual(trades.iloc[0]["exit_reason"], "EXIT_TP")
            self.assertAlmostEqual(float(trades.iloc[0]["gross_pips"]), 100.0)
            self.assertEqual(len(events), 2)
            self.assertEqual(set(events["delivery_status"]), {"PENDING"})
            first_id = trades.iloc[0]["trade_id"]
            ADAPTER.main()
            trades2 = pd.read_csv(ADAPTER.TRADES)
            events2 = pd.read_csv(ADAPTER.OUTBOX)
            self.assertEqual(len(trades2), 1)
            self.assertEqual(len(events2), 2)
            self.assertEqual(trades2.iloc[0]["trade_id"], first_id)

    def test_exit_alert_without_closed_trade_fails_safe(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            reports = root / "reports"; reports.mkdir()
            ADAPTER.ROOT = root
            ADAPTER.POSITIONS = reports / "h1_live_positions.csv"
            ADAPTER.ALERTS = reports / "h1_live_alerts.csv"
            ADAPTER.TRADES = reports / "fx_trade_lifecycle.csv"
            ADAPTER.OUTBOX = reports / "fx_notification_outbox.csv"
            pd.DataFrame([{
                "pair":"eurjpy", "direction":"long", "signal_time":"s",
                "entry_time":"e", "entry_price":160, "tp":161, "sl":159,
                "horizon":72, "status":"OPEN", "last_checked":"t",
            }]).to_csv(ADAPTER.POSITIONS, index=False)
            pd.DataFrame([{
                "alert_id":"EXIT_TP|eurjpy|s", "kind":"EXIT_TP", "pair":"eurjpy",
                "direction":"long", "signal_time":"s", "entry_time":"e",
                "price":161, "tp":161, "sl":159, "message":"exit",
            }]).to_csv(ADAPTER.ALERTS, index=False)
            with self.assertRaises(RuntimeError):
                ADAPTER.main()


if __name__ == "__main__":
    unittest.main(verbosity=2)
