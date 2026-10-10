#!/usr/bin/env python3
"""Offline tests for notification health auditing helpers."""
import csv
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import scripts.audit_fx_notification_health as health


class FxNotificationHealthTests(unittest.TestCase):
    def test_parse_time_requires_timezone(self):
        with self.assertRaises(ValueError):
            health.parse_time("2026-10-10T00:00:00")

    def test_age_minutes_uses_utc_aware_time(self):
        with patch.object(health, "NOW", datetime(2026, 10, 10, 2, 0, tzinfo=timezone.utc)):
            self.assertEqual(health.age_minutes("2026-10-10T00:00:00Z"), 120.0)

    def test_pending_old_h4_event_is_flagged(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "outbox.csv"
            fields = ["event_id", "trade_id", "event_type", "event_time", "pair", "timeframe",
                      "delivery_status", "signal_to_issue_status", "signal_to_issue_seconds"]
            with path.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fields)
                w.writeheader()
                w.writerow({"event_id":"e1", "event_type":"EXIT_SIGNAL", "event_time":"2026-10-10T00:00:00Z",
                            "pair":"USDCAD", "timeframe":"H4", "delivery_status":"PENDING"})
            with patch.object(health, "OUTBOX_PATH", path), patch.object(health, "NOW", datetime(2026, 10, 10, 7, 0, tzinfo=timezone.utc)):
                findings, details = [], []
                health.audit_outbox(findings, details)
            self.assertTrue(any("Pending H4 event e1" in item for item in findings))

    def test_confirmed_historical_late_event_is_reported_but_does_not_page(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "outbox.csv"
            fields = ["event_id", "event_type", "event_time", "pair", "timeframe",
                      "delivery_status", "signal_to_issue_status", "signal_to_issue_seconds"]
            with path.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fields)
                w.writeheader()
                w.writerow({"event_id":"e2", "event_type":"EXIT_SIGNAL", "event_time":"2026-10-06T12:00:00Z",
                            "pair":"USDCAD", "timeframe":"H4", "delivery_status":"ISSUE_CONFIRMED",
                            "signal_to_issue_status":"LATE", "signal_to_issue_seconds":"225945"})
            with patch.object(health, "OUTBOX_PATH", path):
                findings, details = [], []
                health.audit_outbox(findings, details)
            self.assertEqual(findings, [])
            self.assertEqual(details[0]["historical_late_publications"][0]["event_id"], "e2")

    def test_missing_outbox_is_degradation(self):
        with patch.object(health, "OUTBOX_PATH", Path("/definitely/missing/fx-outbox.csv")):
            findings, details = [], []
            health.audit_outbox(findings, details)
        self.assertTrue(any("outbox is missing" in item for item in findings))


if __name__ == "__main__":
    unittest.main(verbosity=2)
