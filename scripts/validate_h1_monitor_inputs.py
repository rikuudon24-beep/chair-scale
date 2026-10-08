#!/usr/bin/env python3
"""Preflight the H1 live monitor inputs without coupling research-only pairs.

Live v1 pairs must pass this gate. Research-only files are checked and reported,
but a research-only data problem must not suppress alerts for unrelated live v1
pairs. Full-universe research data quality belongs in the research workflow.
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
    research_warnings = []
    print("=== H1 live monitor preflight ===")
    for pair in UNIVERSE:
        path = H1_DIR / f"{pair}.csv"
        scope = "LIVE_V1" if pair in LIVE_V1 else "RESEARCH_ONLY"
        try:
            if not path.exists():
                raise ValueError("missing H1 CSV")
            count, first, last = validate(path)
            print(f"[OK] {pair}: rows={count} range={first}->{last} scope={scope}")
        except Exception as exc:
            message = f"{pair}: {exc}"
            if pair in LIVE_V1:
                failures.append(message)
                print(f"[FAIL] {message} scope=LIVE_V1")
            else:
                research_warnings.append(message)
                print(f"[WARN] {message} scope=RESEARCH_ONLY (does not block live alerts)")

    if failures:
        print("[FAIL] H1 live input preflight failed:")
        print("\\n".join(failures))
        return 2
    print(f"[OK] All {len(LIVE_V1)} live v1 inputs passed.")
    print(f"[INFO] Research-only pairs checked={len(UNIVERSE)-len(LIVE_V1)}; warnings={len(research_warnings)}.")
    print("[INFO] Research-only data issues do not block the independent live v1 monitor.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
