#!/usr/bin/env python3
"""Refresh live H4/D1 context from Yahoo 1H candles.

This is live-only. Frozen research history is not used as the live source
after refresh. Recent overlap is checked before the live bars are accepted.
"""
import json
import time
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "market"
SYMBOLS = {"eurjpy", "usdchf", "audnzd"}
H1_DIR = OUT / "h1"
PIP = {"eurjpy": 0.01, "usdchf": 0.0001, "audnzd": 0.0001}
MAX_AGE_H4 = 6.0
MAX_AGE_D1 = 48.0
OVERLAP_HOURS = 96
MEDIAN_MAX_PIPS = 3.0
P95_MAX_PIPS = 10.0


def existing(pair, tf):
    p = OUT / tf / f"{pair}.csv"
    if not p.exists():
        return pd.DataFrame()
    x = pd.read_csv(p)
    x["dt"] = pd.to_datetime(x.timestamp, unit="ms", utc=True)
    return x.set_index("dt")


def aggregate(h1, tf):
    rule = "4h" if tf == "h4" else "24h"
    offset = "20h" if tf == "h4" else "0h"
    x = h1.resample(rule, origin="epoch", offset=offset, label="left", closed="left").agg(
        open=("open", "first"), high=("high", "max"), low=("low", "min"),
        close=("close", "last"), volume=("volume", "sum"), n=("close", "count")
    )
    need = 3 if tf == "h4" else 18
    x = x[x.n >= need].drop(columns="n").dropna(subset=["open", "high", "low", "close"])
    # Convert through Unix seconds so pandas datetime resolution (ns/us/ms/s) cannot corrupt the epoch value.
    x["timestamp"] = [int(ts.timestamp() * 1000) for ts in x.index]
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

    # Fresh H1-derived HTF data is the source of truth. Preserve old rows only
    # for history; never let an old stale file mask a fresh aggregation.
    fresh_latest = pd.to_datetime(int(fresh.timestamp.max()), unit="ms", utc=True)
    old_latest = (
        pd.to_datetime(int(old.timestamp.max()), unit="ms", utc=True)
        if not old.empty else None
    )
    print(
        f"[HTF] {pair} {tf}: fresh_latest={fresh_latest.isoformat()} "
        f"old_latest={old_latest.isoformat() if old_latest is not None else 'none'}"
    )

    merged = fresh if old.empty else pd.concat([old.reset_index(drop=True), fresh], ignore_index=True)
    merged = merged.drop_duplicates("timestamp", keep="last").sort_values("timestamp")
    merged.to_csv(path, index=False)

    # Aggregated timestamps label candle OPEN. Exclude the still-forming
    # candle when measuring freshness; otherwise a partial current bar can
    # make an old last-closed bar appear fresh.
    candle_duration = pd.Timedelta(hours=4 if tf == "h4" else 24)
    now = pd.Timestamp.now(tz="UTC")
    opens = pd.to_datetime(merged.timestamp, unit="ms", utc=True)
    closes = opens + candle_duration
    closed_mask = closes <= now
    if not bool(closed_mask.any()):
        raise RuntimeError(f"{pair} {tf}: no fully closed candle available after refresh")
    latest_closed_open = opens[closed_mask].max()
    latest_closed_close = latest_closed_open + candle_duration
    age = (now - latest_closed_close).total_seconds() / 3600
    limit = MAX_AGE_H4 if tf == "h4" else MAX_AGE_D1
    print(
        f"[OK] {pair} {tf}: latest_closed_open={latest_closed_open.isoformat()} "
        f"latest_closed_close={latest_closed_close.isoformat()} age_since_close={age:.2f}h"
    )
    if age > limit:
        raise RuntimeError(
            f"{pair} {tf}: latest fully closed candle is stale: "
            f"age_since_close={age:.2f}h (limit={limit:.2f}h)"
        )


def main():
    # H1 is the single live source. The workflow refreshes it immediately before
    # this script runs, so rebuilding H4/D1 from the same H1 stream avoids a
    # second provider request that can return a different/stale snapshot.
    for pair in sorted(SYMBOLS):
        path = H1_DIR / f"{pair}.csv"
        if not path.exists():
            raise RuntimeError(f"{pair}: live H1 file missing: {path}")
        h1 = pd.read_csv(path)
        if h1.empty:
            raise RuntimeError(f"{pair}: live H1 file is empty")
        h1["dt"] = pd.to_datetime(h1.timestamp, unit="ms", utc=True)
        h1 = h1.set_index("dt").sort_index()
        latest_h1 = h1.index.max()
        h1_age = (pd.Timestamp.now(tz="UTC") - latest_h1).total_seconds() / 3600
        print(f"[H1->HTF] {pair}: h1_latest={latest_h1.isoformat()} age={h1_age:.2f}h")
        if h1_age > 2.0:
            raise RuntimeError(f"{pair}: live H1 source stale before HTF aggregation: {h1_age:.2f}h")
        for tf in ("h4", "d1"):
            fresh = aggregate(h1, tf)
            if fresh.empty:
                raise RuntimeError(f"{pair} {tf}: aggregation produced no rows")
            merge(pair, tf, fresh)


if __name__ == "__main__":
    main()
