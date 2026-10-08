#!/usr/bin/env python3
"""Preflight the H1 universe before the H1 live monitor runs.

This validates the 12-pair historical H1 input set and reports which pairs
have frozen live rules. It does not promote research-only pairs into trading
signals; only the frozen v1 pairs are eligible for live alerts.
"""
import csv
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
H1_DIR = ROOT / "data" / "market" / "h1"
UNIVERSE = [
    "usdjpy", "eurjpy", "gbpjpy", "audjpy",
    "eurusd", "gbpusd", "audusd", "nzdusd",
    "usdcad", "usdchf", "audnzd", "eurgbp",
]
LIVE_V1 = {"eurjpy", "usdchf", "audnzd"}
MIN_ROWS = 1000
REQUIRED = ("timestamp", "open", "high", "low", "close")

def validate(path):
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        missing = set(REQUIRED) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"missing columns: {sorted(missing)}")
        rows = list(reader)
    if len(rows) < MIN_ROWS:
        raise ValueError(f"too few rows: {len(rows)} < {MIN_ROWS}")

    previous = None
    for line, row in enumerate(rows, start=2):
        try:
            ts = int(row["timestamp"])
            o, h, l, c = (float(row[k]) for k in ("open", "high", "low", "close"))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid row at line {line}: {exc}") from exc
        if not all(math.isfinite(v) and v > 0 for v in (o, h, l, c)):
            raise ValueError(f"non-positive/non-finite OHLC at line {line}")
        if h < max(o, c, l) or l > min(o, c, h):
            raise ValueError(f"inconsistent OHLC at line {line}")
        if previous is not None and ts <= previous:
            raise ValueError(f"duplicate/out-of-order timestamp at line {line}")
        previous = ts
    return len(rows), rows[0]["timestamp"], rows[-1]["timestamp"]

def main():
    failures = []
    print("=== H1 universe preflight ===")
    for pair in UNIVERSE:
        path = H1_DIR / f"{pair}.csv"
        if not path.exists():
            failures.append(f"{pair}: missing H1 CSV")
            continue
        try:
            count, first, last = validate(path)
            scope = "LIVE_V1" if pair in LIVE_V1 else "RESEARCH_ONLY"
            print(f"[OK] {pair}: rows={count} range={first}->{last} scope={scope}")
        except Exception as exc:
            failures.append(f"{pair}: {exc}")
    if failures:
        print("[FAIL] H1 input preflight failed:")
        print("\n".join(failures))
        return 2
    print(f"[OK] {len(UNIVERSE)} H1 files passed; {len(LIVE_V1)} pairs have frozen live v1 rules; {len(UNIVERSE)-len(LIVE_V1)} remain research-only.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
