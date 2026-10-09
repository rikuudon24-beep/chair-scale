#!/usr/bin/env python3
"""Scope production market-data validation to configured trading timeframes."""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "market_data.json"


def production_market_files(data_root=None, config_path=None):
    """Return CSVs for configured production timeframes only (currently H4/D1).

    Research-only datasets such as H1 must not block production notifications
    unless they are explicitly added to config/market_data.json.
    """
    root = Path(data_root) if data_root is not None else ROOT / "data" / "market"
    cfg_path = Path(config_path) if config_path is not None else CONFIG_PATH
    config = json.loads(cfg_path.read_text(encoding="utf-8"))
    timeframes = config.get("timeframes")
    if not isinstance(timeframes, list) or not timeframes or not all(isinstance(tf, str) and tf for tf in timeframes):
        raise ValueError(f"invalid production timeframes in {cfg_path}")
    return sorted(path for tf in timeframes for path in (root / tf).glob("*.csv"))
