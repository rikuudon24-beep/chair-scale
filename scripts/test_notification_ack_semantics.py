#!/usr/bin/env python3
"""Regression tests for notification publication vs end-user delivery semantics."""
import tempfile
import unittest
from pathlib import Path

from fx_lifecycle_contract import EVENT_FIELDS, upsert_ledger, validate_event
from fx_notification_titles import issue_title_candidates


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

    def test_legacy_delivered_state_can_be_migrated_to_issue_confirmed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "outbox.csv"
            legacy = {field: "" for field in EVENT_FIELDS}
            legacy.update(
                event_id="e2", trade_id="t2", event_type="EXIT_SIGNAL",
                event_time="2026-10-09T12:00:00Z", pair="AUDNZD",
                strategy_id="h4_v1", delivery_status="DELIVERED",
                delivered_at="2026-10-09T12:05:00Z",
            )
            upsert_ledger(path, EVENT_FIELDS, [legacy], "event_id")
            migrated = {**legacy, "delivery_status": "ISSUE_CONFIRMED",
                        "issue_confirmed_at": "2026-10-09T12:06:00Z", "delivered_at": ""}
            final = upsert_ledger(path, EVENT_FIELDS, [migrated], "event_id")
            self.assertEqual(final[0]["delivery_status"], "ISSUE_CONFIRMED")
            self.assertEqual(final[0]["issue_confirmed_at"], "2026-10-09T12:06:00Z")
            self.assertEqual(final[0]["delivered_at"], "")

    def test_audnzd_uppercase_title_matches_current_publisher(self):
        row = {"timeframe": "H4", "event_type": "EXIT_SIGNAL", "pair": "AUDNZD",
               "direction": "LONG", "event_time": "2026-10-09T16:00:00+00:00"}
        self.assertEqual(issue_title_candidates(row)[0],
                         "FX EXIT AUDNZD LONG 2026-10-09T16:00:00+00:00")

    def test_h4_title_mapping_keeps_legacy_lowercase_compatibility(self):
        row = {"timeframe": "H4", "event_type": "EXIT_SIGNAL", "pair": "USDCAD",
               "direction": "LONG", "event_time": "2026-10-06T12:00:00+00:00"}
        self.assertIn("FX EXIT usdcad long 2026-10-06T12:00:00+00:00",
                      issue_title_candidates(row))

    def test_unknown_event_mapping_stays_unmapped(self):
        self.assertEqual(issue_title_candidates({"timeframe": "D1", "event_type": "EXIT_SIGNAL"}), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
