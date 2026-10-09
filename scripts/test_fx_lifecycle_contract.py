#!/usr/bin/env python3
"""Regression tests for the shared FX lifecycle contract; no network or market data."""
import tempfile
import unittest
from pathlib import Path

from fx_lifecycle_contract import (
    EVENT_FIELDS, TRADE_FIELDS, make_event_id, make_trade_id,
    upsert_ledger, validate_event, validate_transition,
)


class SharedLifecycleContractTests(unittest.TestCase):
    def test_ids_are_stable_and_event_sensitive(self):
        trade = make_trade_id("h1_v1", "EURJPY", "2026-10-09T00:00:00Z")
        self.assertEqual(trade, make_trade_id("h1_v1", "eurjpy", "2026-10-09T00:00:00Z"))
        self.assertEqual(make_event_id(trade, "EXIT_SL", "2026-10-09T01:00:00Z"),
                         make_event_id(trade, "EXIT_SL", "2026-10-09T01:00:00Z"))
        self.assertNotEqual(make_event_id(trade, "EXIT_SL", "t1"),
                            make_event_id(trade, "EXIT_TP", "t1"))

    def test_transition_contract_rejects_reopening_closed_trade(self):
        validate_transition("OPEN", "CLOSED")
        with self.assertRaises(ValueError):
            validate_transition("CLOSED", "OPEN")

    def test_event_requires_identity_and_known_type(self):
        good = {"event_id": "e1", "trade_id": "t1", "event_type": "EXIT_SL",
                "event_time": "t", "pair": "EURJPY", "strategy_id": "h1_v1",
                "delivery_status": "PENDING"}
        validate_event(good)
        with self.assertRaises(ValueError):
            validate_event({**good, "event_type": "MAGIC"})

    def test_upsert_is_idempotent_and_atomic(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "events.csv"
            row = {field: "" for field in EVENT_FIELDS}
            row.update(event_id="e1", trade_id="t1", event_type="EXIT_SL",
                       event_time="t1", pair="EURJPY", strategy_id="h1_v1",
                       delivery_status="PENDING", attempt_count="0")
            upsert_ledger(path, EVENT_FIELDS, [row], "event_id")
            upsert_ledger(path, EVENT_FIELDS, [row], "event_id")
            import csv
            with path.open(newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 1)
            rows[0]["delivery_status"] = "DELIVERED"
            rows[0]["delivered_at"] = "t2"
            upsert_ledger(path, EVENT_FIELDS, rows, "event_id")
            pending = {**row, "delivery_status": "PENDING", "delivered_at": ""}
            final = upsert_ledger(path, EVENT_FIELDS, [pending], "event_id")
            self.assertEqual(len(final), 1)
            self.assertEqual(final[0]["delivery_status"], "DELIVERED")
            self.assertEqual(final[0]["delivered_at"], "t2")

    def test_trade_schema_contains_entry_exit_and_audit_fields(self):
        for field in ("trade_id", "entry_price", "status", "exit_time", "exit_price", "exit_reason"):
            self.assertIn(field, TRADE_FIELDS)

    def test_terminal_trade_cannot_be_reopened_by_stale_state(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "trades.csv"
            closed = {field: "" for field in TRADE_FIELDS}
            closed.update(trade_id="t1", status="CLOSED", exit_reason="EXIT_SL")
            upsert_ledger(path, TRADE_FIELDS, [closed], "trade_id")
            stale_open = {**closed, "status": "OPEN", "exit_reason": ""}
            with self.assertRaises(ValueError):
                upsert_ledger(path, TRADE_FIELDS, [stale_open], "trade_id")




if __name__ == "__main__":
    unittest.main(verbosity=2)
