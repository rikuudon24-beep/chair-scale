#!/usr/bin/env python3
"""Regression tests for AUD/NZD manual-position lifecycle integration."""
import csv
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
spec = importlib.util.spec_from_file_location("reconcile_audnzd_manual_position", SCRIPTS / "reconcile_audnzd_manual_position.py")
module = importlib.util.module_from_spec(spec)
import sys
sys.path.insert(0, str(SCRIPTS))
spec.loader.exec_module(module)


class AudNzdManualPositionLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.state = self.root / "audnzd_exit_state.json"
        self.trades = self.root / "fx_trade_lifecycle.csv"
        self.outbox = self.root / "fx_notification_outbox.csv"
        module.STATE = self.state
        module.TRADES = self.trades
        module.OUTBOX = self.outbox

    def write_state(self, state="NO_EXIT_CANDIDATE", candle="2026-10-09T16:00:00+00:00"):
        self.state.write_text(json.dumps({
            "pair": "AUD/NZD", "direction": "LONG", "state": state,
            "signal_candle_utc": candle, "signal_close": 1.24446,
            "reasons": "EMA/support/structure confluence" if state == "EXIT_CANDIDATE" else "",
            "data_status": "FRESH_CONFIRMED_H4",
        }), encoding="utf-8")

    def rows(self, path):
        with path.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def test_unknown_entry_details_are_not_fabricated(self):
        self.write_state()
        with patch.object(module, "ROOT", self.root):
            module.main()
        row = self.rows(self.trades)[0]
        self.assertEqual(row["trade_id"], "manual_audnzd_long_position")
        self.assertEqual(row["status"], "OPEN")
        self.assertEqual(row["entry_time"], "")
        self.assertEqual(row["entry_price"], "")
        self.assertEqual(row["signal_time"], "")
        self.assertEqual(row["pair"], "AUDNZD")

    def test_exit_candidate_creates_one_stable_pending_event(self):
        self.write_state("EXIT_CANDIDATE")
        module.main()
        trade = self.rows(self.trades)[0]
        events = self.rows(self.outbox)
        self.assertEqual(trade["status"], "EXIT_PENDING")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "EXIT_SIGNAL")
        self.assertEqual(events[0]["delivery_status"], "PENDING")
        self.assertEqual(events[0]["price"], "1.24446")
        module.main()
        self.assertEqual(len(self.rows(self.outbox)), 1)

    def test_no_exit_after_candidate_does_not_erase_pending_intent(self):
        self.write_state("EXIT_CANDIDATE")
        module.main()
        self.write_state("NO_EXIT_CANDIDATE", "2026-10-09T20:00:00+00:00")
        module.main()
        self.assertEqual(self.rows(self.trades)[0]["status"], "EXIT_PENDING")
        self.assertEqual(len(self.rows(self.outbox)), 1)

    def test_stale_or_unverified_state_is_rejected(self):
        self.write_state()
        state = json.loads(self.state.read_text(encoding="utf-8"))
        state["data_status"] = "UNKNOWN"
        self.state.write_text(json.dumps(state), encoding="utf-8")
        with self.assertRaises(RuntimeError):
            module.main()

    def test_terminal_trade_is_never_reopened(self):
        self.write_state()
        from fx_lifecycle_contract import TRADE_FIELDS, upsert_ledger
        closed = {field: "" for field in TRADE_FIELDS}
        closed.update(trade_id=module.TRADE_ID, status="CLOSED", pair="AUDNZD")
        upsert_ledger(self.trades, TRADE_FIELDS, [closed], "trade_id")
        module.main()
        self.assertEqual(self.rows(self.trades)[0]["status"], "CLOSED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
