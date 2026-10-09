#!/usr/bin/env python3
"""Ensure production validators do not scan unrelated research timeframes."""
import json
import tempfile
import unittest
from pathlib import Path

from production_market_scope import production_market_files


class ProductionMarketScopeTests(unittest.TestCase):
    def test_only_configured_timeframes_are_scanned(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data = root / "market"
            for tf in ("h1", "h4", "d1"):
                folder = data / tf
                folder.mkdir(parents=True)
                (folder / f"{tf}_pair.csv").write_text("timestamp\n1\n", encoding="utf-8")
            config = root / "market_data.json"
            config.write_text(json.dumps({"timeframes": ["h4", "d1"]}), encoding="utf-8")
            files = production_market_files(data, config)
            self.assertEqual({p.parent.name for p in files}, {"h4", "d1"})
            self.assertNotIn(data / "h1" / "h1_pair.csv", files)

    def test_invalid_timeframe_config_fails_clearly(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config = root / "market_data.json"
            config.write_text(json.dumps({"timeframes": []}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid production timeframes"):
                production_market_files(root / "market", config)


if __name__ == "__main__":
    unittest.main(verbosity=2)
