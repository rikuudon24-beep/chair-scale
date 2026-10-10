#!/usr/bin/env python3
"""Tests for idempotent AUD/NZD H4 exit Issue identity."""
import unittest

from scripts.audnzd_h4_exit_notifications import issue_title


class AudnzdExitNotificationIdentityTests(unittest.TestCase):
    def test_same_signal_candle_has_same_issue_title_across_hourly_runs(self):
        state = {
            "state": "EXIT_CANDIDATE",
            "signal_candle_utc": "2026-10-09T16:00:00+00:00",
        }
        first = issue_title(state)
        second = issue_title(dict(state))
        self.assertEqual(first, second)
        self.assertEqual(first, "FX EXIT AUDNZD LONG 2026-10-09T16:00:00+00:00")

    def test_new_signal_candle_gets_a_new_issue_identity(self):
        first = issue_title({
            "state": "EXIT_CANDIDATE",
            "signal_candle_utc": "2026-10-09T16:00:00+00:00",
        })
        second = issue_title({
            "state": "EXIT_CANDIDATE",
            "signal_candle_utc": "2026-10-10T00:00:00+00:00",
        })
        self.assertNotEqual(first, second)

    def test_no_exit_candidate_cannot_create_exit_issue(self):
        with self.assertRaisesRegex(ValueError, "without EXIT_CANDIDATE"):
            issue_title({
                "state": "NO_EXIT_CANDIDATE",
                "signal_candle_utc": "2026-10-09T16:00:00+00:00",
            })

    def test_missing_signal_candle_cannot_create_issue(self):
        with self.assertRaisesRegex(ValueError, "no signal_candle_utc"):
            issue_title({"state": "EXIT_CANDIDATE"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
