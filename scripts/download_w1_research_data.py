#!/usr/bin/env python3
"""Build causal W1 research candles from the repository's completed D1 candles.

Dukascopy-node does not support a native W1 timeframe, so W1 is derived by
aggregating completed UTC D1 candles into Monday-Sunday weeks. The current
incomplete week is excluded. This is isolated research data and does not alter
the frozen H4/D1 pipeline.
"""
import csv, json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config/market_data.json").read_text())
D1 = ROOT / "data/market/d1"
OUT = ROOT / "data/market/w1"
OUT.mkdir(parents=True, exist_ok=True)

def build(pair):
    src = D1 / f"{pair}.csv"
    if not src.exists():
        raise FileNotFoundError(src)
    rows = []
    with src.open(newline="") as f:
        for r in csv.DictReader(f):
            if not r.get("timestamp"):
                continue
            ts = int(r["timestamp"])
            dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
            rows.append((dt, r))
    if not rows:
        raise RuntimeError(f"no D1 rows for {pair}")

    # Only completed UTC weeks: Monday 00:00 through Sunday 23:59.
    now = datetime.now(timezone.utc)
    current_monday = now.date().fromordinal(now.date().toordinal() - now.weekday())

    groups = {}
    for dt, r in rows:
        monday = dt.date().fromordinal(dt.date().toordinal() - dt.weekday())
        if monday >= current_monday:
            continue
        groups.setdefault(monday, []).append((dt, r))

    out = OUT / f"{pair}.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["timestamp","open","high","low","close","volume"])
        w.writeheader()
        for monday in sorted(groups):
            g = sorted(groups[monday], key=lambda x: x[0])
            # Require at least one completed D1 candle; FX holiday weeks may be sparse.
            first = g[0][1]
            last = g[-1][1]
            w.writerow({
                "timestamp": int(datetime(monday.year, monday.month, monday.day, tzinfo=timezone.utc).timestamp() * 1000),
                "open": first["open"],
                "high": max(float(x[1]["high"]) for x in g),
                "low": min(float(x[1]["low"]) for x in g),
                "close": last["close"],
                "volume": sum(float(x[1].get("volume") or 0) for x in g),
            })
    print(f"[OK] {pair} derived W1: {len(groups)} completed weeks")

missing = []
for pair in CFG["pairs"]:
    try:
        build(pair)
    except Exception as e:
        print(f"[WARN] {pair}: {e}", flush=True)
        missing.append(pair)

if missing:
    raise SystemExit("missing D1 source: " + ",".join(missing))
