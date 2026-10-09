#!/usr/bin/env python3
"""Synthetic regression tests for H4-to-common-lifecycle reconciliation."""
import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "reconcile_h4_exit_lifecycle.py"
SPEC = importlib.util.spec_from_file_location("reconcile_h4_exit_lifecycle", SCRIPT)
ADAPTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ADAPTER)


class H4LifecycleAdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.config = root / "active_positions.json"
        self.state = root / "state.csv"
        self.alerts = root / "alerts.csv"
        self.trades = root / "trades.csv"
        self.outbox = root / "outbox.csv"
        self.pos = {
            "id": "usdcad-long-test", "pair": "usdcad", "direction": "long",
            "entry_timestamp": "2026-10-01T00:00:00Z",
            "reference_entry_price": 1.42, "source": "frozen_h4_entry_alert",
            "status": "open",
        }
        self.write_config()
        self.write_state("EXIT_TRIGGERED")
        self.write_alerts()
        self.path_patches = [
            patch.object(ADAPTER, "CONFIG", self.config),
            patch.object(ADAPTER, "STATE", self.state),
            patch.object(ADAPTER, "ALERTS", self.alerts),
            patch.object(ADAPTER, "TRADES", self.trades),
            patch.object(ADAPTER, "OUTBOX", self.outbox),
        ]
        for p in self.path_patches:
            p.start()

    def tearDown(self):
        for p in self.path_patches:
            p.stop()
        self.tmp.cleanup()

    def write_config(self):
        self.config.write_text(json.dumps({"positions": [self.pos]}), encoding="utf-8")

    def write_state(self, state):
        row = {
            "id": self.pos["id"], "pair": "usdcad", "direction": "long",
            "entry_timestamp": self.pos["entry_timestamp"], "reference_entry_price": "1.42",
            "source": "frozen_h4_entry_alert", "status": "open", "state": state,
            "exit_signal_timestamp": "2026-10-08T16:00:00+00:00" if state == "EXIT_TRIGGERED" else "",
            "exit_signal_price": "1.43" if state == "EXIT_TRIGGERED" else "",
            "exit_reason": "price20_cross_down+di_spread_down3" if state == "EXIT_TRIGGERED" else "",
            "latest_completed_h4": "2026-10-08T16:00:00+00:00", "latest_close": "1.43",
        }
        self.write_csv(self.state, list(row), [row])

    def write_alerts(self):
        row = {
            "id": self.pos["id"], "pair": "usdcad", "direction": "long",
            "exit_signal_timestamp": "2026-10-08T16:00:00+00:00",
            "exit_signal_price": "1.43", "exit_reason": "price20_cross_down+di_spread_down3",
        }
        self.write_csv(self.alerts, list(row), [row])

    @staticmethod
    def write_csv(path, fields, rows):
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def read_csv(path):
        with path.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def test_exit_signal_creates_pending_trade_and_one_outbox_event(self):
        ADAPTER.main()
        trades = self.read_csv(self.trades)
        events = self.read_csv(self.outbox)
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0]["status"], "EXIT_PENDING")
        self.assertEqual(trades[0]["exit_time"], "")
        self.assertEqual(trades[0]["exit_price"], "")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "EXIT_SIGNAL")
        self.assertEqual(events[0]["price"], "1.43")

    def test_user_confirmed_manual_close_closes_lifecycle_without_fake_fill(self):
        ADAPTER.main()
        self.pos["status"] = "closed"
        self.pos["closure_confirmation"] = "user_confirmed"
        self.pos["closure_confirmed_date"] = "2026-10-09"
        self.pos["actual_exit_timestamp"] = None
        self.pos["actual_exit_price"] = None
        self.write_config()

        ADAPTER.main()
        trade = self.read_csv(self.trades)[0]
        self.assertEqual(trade["status"], "CLOSED")
        self.assertEqual(trade["exit_time"], "")
        self.assertEqual(trade["exit_price"], "")
        self.assertEqual(trade["exit_reason"], "user_confirmed_manual_close_fill_unknown")
        self.assertEqual(len(self.read_csv(self.outbox)), 1)

    def test_outbox_first_write_recovers_if_trade_ledger_write_fails(self):
        real_upsert = ADAPTER.upsert_ledger
        failed = {"done": False}

        def fail_trade_write_once(path, fields, rows, key_field):
            if Path(path) == self.trades and not failed["done"]:
                failed["done"] = True
                raise OSError("simulated trade-ledger write failure")
            return real_upsert(path, fields, rows, key_field)

        with patch.object(ADAPTER, "upsert_ledger", side_effect=fail_trade_write_once):
            with self.assertRaisesRegex(OSError, "simulated trade-ledger"):
                ADAPTER.main()

        # Durable notification intent exists even though the trade-ledger write failed.
        self.assertEqual(len(self.read_csv(self.outbox)), 1)
        self.assertFalse(self.trades.exists())

        # A retry is idempotent and completes the missing trade row.
        ADAPTER.main()
        self.assertEqual(len(self.read_csv(self.outbox)), 1)
        self.assertEqual(len(self.read_csv(self.trades)), 1)
        self.assertEqual(self.read_csv(self.trades)[0]["status"], "EXIT_PENDING")

    def test_repeated_run_does_not_duplicate_exit_event(self):
        ADAPTER.main()
        ADAPTER.main()
        self.assertEqual(len(self.read_csv(self.trades)), 1)
        self.assertEqual(len(self.read_csv(self.outbox)), 1)

    def test_reconciliation_never_downgrades_delivered_exit_event(self):
        ADAPTER.main()
        events = self.read_csv(self.outbox)
        events[0]["delivery_status"] = "DELIVERED"
        events[0]["attempt_count"] = "1"
        events[0]["delivered_at"] = "2026-10-08T17:30:00+00:00"
        self.write_csv(self.outbox, list(events[0]), events)

        ADAPTER.main()
        event = self.read_csv(self.outbox)[0]
        self.assertEqual(event["delivery_status"], "DELIVERED")
        self.assertEqual(event["attempt_count"], "1")
        self.assertEqual(event["delivered_at"], "2026-10-08T17:30:00+00:00")

    def test_reconciliation_preserves_outbox_delivery_metadata(self):
        ADAPTER.main()
        events = self.read_csv(self.outbox)
        events[0]["delivery_status"] = "FAILED"
        events[0]["attempt_count"] = "3"
        events[0]["last_attempt_at"] = "2026-10-08T17:00:00+00:00"
        events[0]["last_error"] = "temporary delivery failure"
        self.write_csv(self.outbox, list(events[0]), events)

        ADAPTER.main()
        event = self.read_csv(self.outbox)[0]
        self.assertEqual(event["delivery_status"], "FAILED")
        self.assertEqual(event["attempt_count"], "3")
        self.assertEqual(event["last_attempt_at"], "2026-10-08T17:00:00+00:00")
        self.assertEqual(event["last_error"], "temporary delivery failure")

    def test_later_hold_does_not_erase_pending_exit(self):
        ADAPTER.main()
        self.write_state("HOLD_NO_EXIT")
        ADAPTER.main()
        trades = self.read_csv(self.trades)
        self.assertEqual(trades[0]["status"], "EXIT_PENDING")
        self.assertEqual(len(self.read_csv(self.outbox)), 1)

    def test_unknown_then_hold_does_not_erase_exit_intent(self):
        ADAPTER.main()
        self.write_state("UNKNOWN")
        ADAPTER.main()
        self.write_state("HOLD_NO_EXIT")
        ADAPTER.main()
        trades = self.read_csv(self.trades)
        self.assertEqual(trades[0]["status"], "EXIT_PENDING")
        self.assertEqual(len(self.read_csv(self.outbox)), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
