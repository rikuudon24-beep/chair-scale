#!/usr/bin/env python3
"""Regression tests for notification publication vs end-user delivery semantics."""
import tempfile
import unittest
from pathlib import Path

from fx_lifecycle_contract import EVENT_FIELDS, upsert_ledger, validate_event


class NotificationAckSemanticsTests(unittest.TestCase):
    def test_issue_confirmed_is_valid_and_distinct_from_device_delivery(self):
        event = {
            "event_id": "e1", "trade_id": "t1", "event_type": "EXIT_SIGNAL",
            "event_time": "2026-10-09T12:00:00Z", "pair": "AUDNZD",
            "strategy_id": "h4_v1", "delivery_status": "ISSUE_CONFIRMED",
        }
        validate_event(event)
        self.assertNotEqual(event["delivery_status"], "DELIVERED")

    def test_stale_pending_retry_cannot_downgrade_issue_confirmation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "outbox.csv"
            confirmed = {field: "" for field in EVENT_FIELDS}
            confirmed.update(
                event_id="e1", trade_id="t1", event_type="EXIT_SIGNAL",
                event_time="2026-10-09T12:00:00Z", pair="AUDNZD",
                strategy_id="h4_v1", delivery_status="ISSUE_CONFIRMED",
                issue_confirmed_at="2026-10-09T12:01:00Z", delivered_at="",
            )
            upsert_ledger(path, EVENT_FIELDS, [confirmed], "event_id")
            stale = {**confirmed, "delivery_status": "PENDING",
                     "issue_confirmed_at": "", "delivered_at": ""}
            final = upsert_ledger(path, EVENT_FIELDS, [stale], "event_id")
            self.assertEqual(final[0]["delivery_status"], "ISSUE_CONFIRMED")
            self.assertEqual(final[0]["issue_confirmed_at"], "2026-10-09T12:01:00Z")
            self.assertEqual(final[0]["delivered_at"], "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
