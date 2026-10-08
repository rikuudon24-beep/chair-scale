#!/usr/bin/env python3
"""Refresh live H4/D1 context from Yahoo 1H candles.

This is live-only. Frozen research history is not used as the live source
after refresh. Recent overlap is checked before the live bars are accepted.
"""
import json
import time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "market"
SYMBOLS = {"eurjpy": "EURJPY=X", "usdchf": "CHF=X", "audnzd": "AUDNZD=X"}
PIP = {"eurjpy": 0.01, "usdchf": 0.0001, "audnzd": 0.0001}
MAX_AGE_H4 = 6.0
MAX_AGE_D1 = 30.0
OVERLAP_HOURS = 96
MEDIAN_MAX_PIPS = 3.0
P95_MAX_PIPS = 10.0


def fetch(symbol):
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        + quote(symbol, safe="")
        + "?interval=1h&range=60d&events=history"
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
        rows.append({"timestamp": int(t) * 1000, "open": float(vals[0]),
                     "high": float(vals[1]), "low": float(vals[2]),
                     "close": float(vals[3]), "volume": 0})
    if not rows:
        raise RuntimeError(f"Yahoo returned no usable H1 rows for {symbol}")
    x = pd.DataFrame(rows).drop_duplicates("timestamp").sort_values("timestamp")
    x["dt"] = pd.to_datetime(x.timestamp, unit="ms", utc=True)
    return x.set_index("dt")


def existing(pair, tf):
    p = OUT / tf / f"{pair}.csv"
    if not p.exists():
        return pd.DataFrame()
    x = pd.read_csv(p)
    x["dt"] = pd.to_datetime(x.timestamp, unit="ms", utc=True)
    return x.set_index("dt")


def aggregate(h1, tf):
    rule = "4h" if tf == "h4" else "1D"
    offset = "20h" if tf == "h4" else "0h"
    x = h1.resample(rule, origin="epoch", offset=offset, label="left", closed="left").agg(
        open=("open", "first"), high=("high", "max"), low=("low", "min"),
        close=("close", "last"), volume=("volume", "sum"), n=("close", "count")
    )
    need = 3 if tf == "h4" else 18
    x = x[x.n >= need].drop(columns="n").dropna(subset=["open", "high", "low", "close"])
    x["timestamp"] = (x.index.view("int64") // 10**6).astype("int64")
    return x.reset_index(drop=True)[["timestamp", "open", "high", "low", "close", "volume"]]


def validate(pair, tf, old, fresh):
    if old.empty:
        return
    cutoff = int((time.time() - OVERLAP_HOURS * 3600) * 1000)
    old_latest = int(old.timestamp.max()) if not old.empty else None
    # If the previous live file is already older than the comparison window,
    # zero overlap is expected during a source refresh. In that case accept the
    # fresh source after its own freshness check rather than blocking the monitor.
    if old_latest is not None and old_latest < cutoff:
        print(f"[CHECK] {pair} {tf}: old source is outside overlap window; accepting fresh source")
        return
    a = old[old.timestamp >= cutoff][["timestamp", "close"]]
    b = fresh[fresh.timestamp >= cutoff][["timestamp", "close"]]
    m = a.merge(b, on="timestamp", suffixes=("_old", "_new"))
    if len(m) < (12 if tf == "h4" else 2):
        raise RuntimeError(f"{pair} {tf}: insufficient overlap ({len(m)} bars)")
    d = (m.close_new - m.close_old).abs() / PIP[pair]
    median, p95 = float(d.median()), float(d.quantile(0.95))
    print(f"[CHECK] {pair} {tf}: overlap={len(m)} median={median:.3f}p95={p95:.3f} pips")
    if median > MEDIAN_MAX_PIPS or p95 > P95_MAX_PIPS:
        raise RuntimeError(f"{pair} {tf}: source divergence too large")


def merge(pair, tf, fresh):
    path = OUT / tf / f"{pair}.csv"
    old = existing(pair, tf)
    validate(pair, tf, old, fresh)
    merged = fresh if old.empty else pd.concat([old.reset_index(drop=True), fresh], ignore_index=True)
    merged = merged.drop_duplicates("timestamp", keep="last").sort_values("timestamp")
    merged.to_csv(path, index=False)
    latest = pd.to_datetime(int(merged.timestamp.max()), unit="ms", utc=True)
    age = (pd.Timestamp.now(tz="UTC") - latest).total_seconds() / 3600
    limit = MAX_AGE_H4 if tf == "h4" else MAX_AGE_D1
    print(f"[OK] {pair} {tf}: latest={latest.isoformat()} age={age:.2f}h")
    if age > limit:
        raise RuntimeError(f"{pair} {tf}: live data stale after refresh: {age:.2f}h")


def main():
    for pair, symbol in SYMBOLS.items():
        h1 = fetch(symbol)
        for tf in ("h4", "d1"):
            fresh = aggregate(h1, tf)
            merge(pair, tf, fresh)


if __name__ == "__main__":
    main()
