#!/usr/bin/env python3
"""Stable, candle-keyed identity for AUD/NZD H4 exit-candidate Issues."""
import json
import sys
from pathlib import Path


def issue_title(state):
    if str(state.get("state", "")).upper() != "EXIT_CANDIDATE":
        raise ValueError("cannot publish an AUDNZD exit Issue without EXIT_CANDIDATE state")
    signal_candle = str(state.get("signal_candle_utc", "")).strip()
    if not signal_candle:
        raise ValueError("EXIT_CANDIDATE state has no signal_candle_utc")
    return f"FX EXIT AUDNZD LONG {signal_candle}"


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("reports/audnzd_exit_state.json")
    state = json.loads(path.read_text(encoding="utf-8"))
    print(issue_title(state))


if __name__ == "__main__":
    main()
