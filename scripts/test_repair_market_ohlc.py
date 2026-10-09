#!/usr/bin/env python3
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("repair_market_ohlc.py")
SPEC = importlib.util.spec_from_file_location("repair_market_ohlc_under_test", SCRIPT)
REPAIR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPAIR)


class OHLCAuditTests(unittest.TestCase):
    def test_repairs_one_tick_close_below_low(self):
        row = {"timestamp":"1", "open":"0.83675", "high":"0.83692",
               "low":"0.8363", "close":"0.83629"}
        result = REPAIR.analyze_row(row)
        self.assertIsNotNone(result)
        self.assertEqual(result["repaired_low"], "0.83629")
        self.assertEqual(result["tick_size"], "0.00001")

    def test_rejects_large_envelope_violation(self):
        row = {"timestamp":"1", "open":"0.83675", "high":"0.83692",
               "low":"0.8350", "close":"0.83629"}
        with self.assertRaises(ValueError):
            REPAIR.analyze_row(row)

    def test_valid_ohlc_needs_no_repair(self):
        row = {"timestamp":"1", "open":"1.0000", "high":"1.0020",
               "low":"0.9990", "close":"1.0010"}
        self.assertIsNone(REPAIR.analyze_row(row))


if __name__ == "__main__":
    unittest.main(verbosity=2)
