#!/usr/bin/env python3
"""Ensure market download merge preserves source OHLC for the audit step."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "download_market_data.py"
SPEC = importlib.util.spec_from_file_location("download_market_data_under_test", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DownloadOHLCPreservationTests(unittest.TestCase):
    def test_merge_does_not_repair_source_ohlc_before_audit(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source.csv"
            final = root / "final.csv"
            source.write_text(
                "timestamp,open,high,low,close,volume\n"
                "1728615600000,0.83727,0.83805,0.83729,0.83794,5364.13\n",
                encoding="utf-8",
            )
            MODULE.merge(final, [source])
            lines = final.read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines[1].split(",")[3], "0.83729")
            # The close/low violation is intentionally preserved so the
            # dedicated OHLC repair script can reject/audit it, not hide it.
            self.assertEqual(lines[1].split(",")[4], "0.83794")


if __name__ == "__main__":
    unittest.main(verbosity=2)
