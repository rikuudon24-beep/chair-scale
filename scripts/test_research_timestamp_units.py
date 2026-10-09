#!/usr/bin/env python3
"""Regression tests for market timestamp unit normalization."""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("research_price_structure_transition.py")
SPEC = importlib.util.spec_from_file_location("price_structure_transition", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TimestampNormalizationTests(unittest.TestCase):
    def test_unix_seconds(self):
        got = MODULE.normalize_timestamp_column(["1728615600"])
        self.assertEqual(got.iloc[0].isoformat(), "2024-10-11T03:00:00+00:00")

    def test_unix_milliseconds(self):
        got = MODULE.normalize_timestamp_column(["1728615600000"])
        self.assertEqual(got.iloc[0].isoformat(), "2024-10-11T03:00:00+00:00")

    def test_iso8601(self):
        got = MODULE.normalize_timestamp_column(["2026-10-09T12:00:00Z"])
        self.assertEqual(got.iloc[0].isoformat(), "2026-10-09T12:00:00+00:00")

    def test_mixed_seconds_and_milliseconds_rejected(self):
        with self.assertRaisesRegex(ValueError, "mixes Unix seconds and milliseconds"):
            MODULE.normalize_timestamp_column(["1728615600", "1728615600000"])

    def test_out_of_range_numeric_rejected_clearly(self):
        with self.assertRaisesRegex(ValueError, "outside supported Unix seconds/ms ranges"):
            MODULE.normalize_timestamp_column(["1"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
