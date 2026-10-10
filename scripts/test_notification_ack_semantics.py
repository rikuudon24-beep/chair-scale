#!/usr/bin/env python3
"""Regression tests for FX notification lag measurement and publication semantics."""
import tempfile
import unittest
from pathlib import Path

from fx_lifecycle_contract import EVENT_FIELDS, upsert_ledger, validate_event
from fx_notification_lag import measure_signal_to_issue
from fx_notification_titles import issue_title_candidates
from acknowledge_fx_notification_outbox import reconcile_rows


class NotificationLagTests(unittest.TestCase):
    def test_h1_lag_is_measured_and_flagged_over_two_hours(self):
        result = measure_signal_to_issue("2026-10-10T00:00:00Z", "2026-10-10T02:30:00Z", "H1")
        self.assertEqual(result["signal_to_issue_seconds"], "9000.0")
        self.assertEqual(result["signal_to_issue_status"], "LATE")

    def test_h4_lag_within_six_hours_is_on_time(self):
        result = measure_signal_to_issue("2026-10-10T00:00:00Z", "2026-10-10T05:59:00Z", "H4")
        self.assertEqual(result["signal_to_issue_status"], "ON_TIME")

    def test_missing_timezone_is_rejected(self):
        with self.assertRaises(ValueError):
            measure_signal_to_issue("2026-10-10T00:00:00", "2026-10-10T01:00:00Z", "H1")

    def test_issue_created_before_signal_is_flagged(self):
        result = measure_signal_to_issue("2026-10-10T02:00:00Z", "2026-10-10T01:00:00Z", "H1")
        self.assertEqual(result["signal_to_issue_status"], "TIMESTAMP_ORDER_INVALID")
        self.assertEqual(result["signal_to_issue_seconds"], "")

    def test_outbox_ack_uses_actual_issue_created_at_and_keeps_device_unverified(self):
        row = {field: "" for field in EVENT_FIELDS}
        row.update(event_id="e1", trade_id="t1", event_type="EXIT_SIGNAL",
                   event_time="2026-10-10T00:00:00Z", pair="AUDNZD", timeframe="H4",
                   direction="LONG", strategy_id="h4_v1", delivery_status="PENDING",
                   attempt_count="0")
        title = "FX EXIT AUDNZD LONG 2026-10-10T00:00:00Z"
        rows, confirmed, late = reconcile_rows(
            [row], [{"title": title, "created_at": "2026-10-10T07:00:00Z"}],
            "2026-10-10T07:01:00Z",
        )
        self.assertEqual(confirmed, 1)
        self.assertEqual(late, 1)
        self.assertEqual(rows[0]["issue_created_at"], "2026-10-10T07:00:00+00:00")
        self.assertEqual(rows[0]["signal_to_issue_seconds"], "25200.0")
        self.assertEqual(rows[0]["signal_to_issue_status"], "LATE")
        self.assertEqual(rows[0]["delivery_status"], "ISSUE_CONFIRMED")
        self.assertEqual(rows[0]["delivered_at"], "")

    def test_stale_retry_cannot_erase_lag_measurement(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "outbox.csv"
            confirmed = {field: "" for field in EVENT_FIELDS}
            confirmed.update(event_id="e1", trade_id="t1", event_type="EXIT_SIGNAL",
                             event_time="2026-10-10T00:00:00Z", pair="AUDNZD",
                             strategy_id="h4_v1", delivery_status="ISSUE_CONFIRMED",
                             issue_confirmed_at="2026-10-10T07:01:00Z",
                             issue_created_at="2026-10-10T07:00:00+00:00",
                             signal_to_issue_seconds="25200.0", signal_to_issue_status="LATE",
                             delivered_at="")
            upsert_ledger(path, EVENT_FIELDS, [confirmed], "event_id")
            stale = {**confirmed, "delivery_status": "PENDING", "issue_created_at": "",
                     "signal_to_issue_seconds": "", "signal_to_issue_status": ""}
            final = upsert_ledger(path, EVENT_FIELDS, [stale], "event_id")
            self.assertEqual(final[0]["delivery_status"], "ISSUE_CONFIRMED")
            self.assertEqual(final[0]["signal_to_issue_seconds"], "25200.0")
            self.assertEqual(final[0]["signal_to_issue_status"], "LATE")

    def test_issue_confirmed_is_not_device_delivery(self):
        event = {"event_id":"e1", "trade_id":"t1", "event_type":"EXIT_SIGNAL",
                 "event_time":"2026-10-10T00:00:00Z", "pair":"AUDNZD",
                 "strategy_id":"h4_v1", "delivery_status":"ISSUE_CONFIRMED"}
        validate_event(event)
        self.assertNotEqual(event["delivery_status"], "DELIVERED")

    def test_audnzd_title_mapping_and_legacy_h4_compatibility(self):
        row = {"timeframe":"H4", "event_type":"EXIT_SIGNAL", "pair":"AUDNZD",
               "direction":"LONG", "event_time":"2026-10-09T16:00:00+00:00"}
        self.assertEqual(issue_title_candidates(row)[0],
                         "FX EXIT AUDNZD LONG 2026-10-09T16:00:00+00:00")
        old = {"timeframe":"H4", "event_type":"EXIT_SIGNAL", "pair":"USDCAD",
               "direction":"LONG", "event_time":"2026-10-06T12:00:00+00:00"}
        self.assertIn("FX EXIT usdcad long 2026-10-06T12:00:00+00:00",
                      issue_title_candidates(old))


if __name__ == "__main__":
    unittest.main(verbosity=2)
