#!/usr/bin/env python3
"""Refresh live H1 candles from Yahoo Finance with overlap validation.

Research history remains untouched as the frozen baseline. Live candles are
merged only after the provider's recent overlap agrees with the frozen data.
"""
import json
import time
from urllib.parse import quote
from urllib.request import Request, urlopen
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "market" / "h1"

SYMBOLS = {
    "eurjpy": "EURJPY=X",
    "usdchf": "CHF=X",
    "audnzd": "AUDNZD=X",
}
PIP = {"eurjpy": 0.01, "usdchf": 0.0001, "audnzd": 0.0001}
RANGE = "14d"
MAX_AGE_HOURS = 2.0
OVERLAP_HOURS = 72
MEDIAN_MAX_PIPS = 3.0
P95_MAX_PIPS = 10.0


def normalize_ohlc(df):
    """Repair only the OHLC envelope; preserve open/close and source precision."""
    out = df.copy()
    high = out[["open", "high", "low", "close"]].max(axis=1)
    low = out[["open", "high", "low", "close"]].min(axis=1)
    repaired = ((out["high"] < high) | (out["low"] > low)).sum()
    out["high"] = high
    out["low"] = low
    if repaired:
        print(f"[REPAIR] normalized {int(repaired)} rounded OHLC envelope rows", flush=True)
    return out


def fetch(symbol):
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        + quote(symbol, safe="")
        + "?interval=1h&range=" + RANGE + "&events=history"
    )
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=30) as r:
        payload = json.loads(r.read().decode("utf-8"))
    result = payload.get("chart", {}).get("result")
    if not result:
        raise RuntimeError(f"Yahoo chart error for {symbol}: {payload.get('chart', {}).get('error')}")
    z = result[0]
    ts = z.get("timestamp") or []
    q = (z.get("indicators") or {}).get("quote", [{}])[0]
    rows = []
    for i, t in enumerate(ts):
        vals = [q.get(k, [None] * len(ts))[i] for k in ("open", "high", "low", "close")]
        if any(v is None for v in vals):
            continue
        rows.append({
            "timestamp": int(t) * 1000,
            "open": float(vals[0]),
            "high": float(vals[1]),
            "low": float(vals[2]),
            "close": float(vals[3]),
            "volume": 0,
        })
    if not rows:
        raise RuntimeError(f"Yahoo returned no usable H1 rows for {symbol}")
    return normalize_ohlc(pd.DataFrame(rows).drop_duplicates("timestamp").sort_values("timestamp"))


def read_existing(path):
    if not path.exists():
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
    return pd.read_csv(path)


def validate_overlap(pair, old, fresh):
    if old.empty:
        return
    cutoff = int((time.time() - OVERLAP_HOURS * 3600) * 1000)
    a = old[old.timestamp >= cutoff][["timestamp", "close"]].copy()
    b = fresh[fresh.timestamp >= cutoff][["timestamp", "close"]].copy()
    if a.empty or b.empty:
        return
    m = a.merge(b, on="timestamp", suffixes=("_old", "_new"))
    if len(m) < 24:
        raise RuntimeError(f"{pair}: only {len(m)} overlap bars; refusing source switch")
    diff_pips = (m.close_new - m.close_old).abs() / PIP[pair]
    median = float(diff_pips.median())
    p95 = float(diff_pips.quantile(0.95))
    print(f"[CHECK] {pair}: overlap={len(m)} median_diff={median:.3f} p95_diff={p95:.3f} pips")
    if median > MEDIAN_MAX_PIPS or p95 > P95_MAX_PIPS:
        raise RuntimeError(f"{pair}: source divergence too large: median={median:.3f} p95={p95:.3f} pips")


def merge(pair, fresh):
    path = OUT / f"{pair}.csv"
    old = read_existing(path)
    validate_overlap(pair, old, fresh)
    if old.empty:
        merged = fresh
    else:
        merged = pd.concat([old, fresh], ignore_index=True)
        merged = merged.drop_duplicates("timestamp", keep="last").sort_values("timestamp")
    merged = normalize_ohlc(merged)
    merged[["timestamp", "open", "high", "low", "close", "volume"]].to_csv(path, index=False)
    latest = pd.to_datetime(int(merged.timestamp.max()), unit="ms", utc=True)
    age = (pd.Timestamp.now(tz="UTC") - latest).total_seconds() / 3600
    print(f"[OK] {pair}: rows={len(merged)} latest={latest.isoformat()} age={age:.2f}h")
    if age > MAX_AGE_HOURS:
        raise RuntimeError(f"{pair}: live H1 data stale after refresh: age={age:.2f}h")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    failures = []
    for pair, symbol in SYMBOLS.items():
        try:
            fresh = fetch(symbol)
            merge(pair, fresh)
        except Exception as e:
            failures.append(f"{pair}: {e}")
    if failures:
        raise SystemExit("[FAIL]\n" + "\n".join(failures))


if __name__ == "__main__":
    main()
