#!/usr/bin/env python3
"""Refresh USDCAD H4 data for the open-position exit monitor.

Try Dukascopy first, then fall back to Yahoo Finance's hourly chart endpoint.
Only complete four-hour buckets made from four consecutive closed hourly bars
are written. Existing history is preserved and merged by timestamp.
"""
import csv
import json
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "market" / "h4" / "usdcad.csv"
START = date.today() - timedelta(days=14)
END_CANDIDATES = [date.today(), date.today() + timedelta(days=1)]


def usable_rows(path, attempt):
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    rows = [r for r in rows if r.get("timestamp") and r.get("close")]
    if len(rows) < 5:
        raise RuntimeError(f"attempt {attempt}: too few usable H4 rows ({len(rows)})")
    return rows


def download_dukascopy(start, end, attempt):
    with tempfile.TemporaryDirectory(prefix=f"usdcad-h4-{attempt}-") as td:
        cmd = [
            "npx", "--yes", "dukascopy-node@1.50.0",
            "-i", "usdcad", "-from", start.isoformat(), "-to", end.isoformat(),
            "-t", "h4", "-f", "csv", "-p", "bid", "-v", "-s",
            "-dir", td, "-bs", "5", "-bp", "1500",
        ]
        subprocess.run(cmd, cwd=ROOT, check=True, timeout=900)
        files = sorted(Path(td).glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not files or files[0].stat().st_size == 0:
            raise RuntimeError(f"attempt {attempt}: Dukascopy returned an empty CSV")
        return usable_rows(files[0], attempt)


def download_yahoo_h4():
    """Fallback: aggregate Yahoo's 60-minute candles into verified UTC H4 bars."""
    now = datetime.now(timezone.utc)
    period1 = int((now - timedelta(days=14)).timestamp())
    period2 = int(now.timestamp())
    query = urllib.parse.urlencode({
        "period1": period1, "period2": period2, "interval": "60m",
        "events": "history", "includeAdjustedClose": "false",
    })
    url = "https://query1.finance.yahoo.com/v8/finance/chart/USDCAD=X?" + query
    request = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (compatible; FXResearchMonitor/1.0)"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    result = (payload.get("chart", {}).get("result") or [None])[0]
    if not result:
        raise RuntimeError("Yahoo Finance returned no USDCAD chart result")
    timestamps = result.get("timestamp") or []
    quotes = (result.get("indicators", {}).get("quote") or [{}])[0]
    bars = {}
    for i, ts in enumerate(timestamps):
        values = [quotes.get(k, [None] * len(timestamps))[i] for k in ("open", "high", "low", "close")]
        if any(v is None for v in values):
            continue
        ts = int(ts)
        bucket = (ts // 14400) * 14400
        bars.setdefault(bucket, []).append((ts, values, (quotes.get("volume") or [None] * len(timestamps))[i]))
    fresh = []
    for bucket, items in sorted(bars.items()):
        items.sort(key=lambda x: x[0])
        expected = [bucket + 3600 * n for n in range(4)]
        # Reject partial bars, missing hourly candles, and the currently forming H4 bar.
        if [x[0] for x in items] != expected or bucket + 14400 > int(now.timestamp()):
            continue
        values = [x[1] for x in items]
        volumes = [x[2] for x in items if x[2] is not None]
        fresh.append({
            "timestamp": bucket * 1000,
            "open": values[0][0],
            "high": max(v[1] for v in values),
            "low": min(v[2] for v in values),
            "close": values[-1][3],
            "volume": sum(volumes) if volumes else 0,
        })
    if len(fresh) < 5:
        raise RuntimeError(f"Yahoo Finance fallback returned only {len(fresh)} complete H4 bars")
    print(f"[OK] Yahoo Finance fallback returned {len(fresh)} complete USDCAD H4 bars")
    return fresh


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fresh = None
    errors = []
    for attempt in range(1, 4):
        end = END_CANDIDATES[(attempt - 1) % len(END_CANDIDATES)]
        try:
            fresh = download_dukascopy(START, end, attempt)
            print(f"[OK] Dukascopy returned {len(fresh)} USDCAD H4 rows on attempt {attempt}")
            break
        except Exception as exc:
            errors.append(str(exc))
            print(f"[WARN] {exc}", flush=True)
            if attempt < 3:
                time.sleep(5 * attempt)
    if fresh is None:
        print("[WARN] Dukascopy failed; trying Yahoo Finance hourly-data fallback", flush=True)
        try:
            fresh = download_yahoo_h4()
        except Exception as exc:
            errors.append(f"Yahoo fallback: {exc}")
            raise RuntimeError("USDCAD H4 refresh failed: " + " | ".join(errors)) from exc

    rows = {}
    if OUT.exists():
        with OUT.open(newline="") as f:
            for row in csv.DictReader(f):
                if row.get("timestamp"):
                    rows[int(float(row["timestamp"]))] = row
    for row in fresh:
        # All sources are normalized to epoch milliseconds for the repository schema.
        ts = int(float(row["timestamp"]))
        if ts < 100000000000:
            ts *= 1000
        row["timestamp"] = ts
        rows[ts] = row
    ordered = [rows[k] for k in sorted(rows)]
    fields = ["timestamp", "open", "high", "low", "close", "volume"]
    tmp = OUT.with_suffix(".tmp")
    with tmp.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in ordered:
            writer.writerow({k: row.get(k, "") for k in fields})
    tmp.replace(OUT)
    latest = int(ordered[-1]["timestamp"])
    latest_dt = datetime.fromtimestamp(latest / 1000, timezone.utc)
    age_hours = (datetime.now(timezone.utc) - latest_dt).total_seconds() / 3600
    if age_hours > 120:
        raise RuntimeError(f"Refreshed USDCAD H4 data is stale: latest={latest_dt.isoformat()}, age={age_hours:.1f}h")
    print(f"[OK] merged USDCAD H4 rows={len(ordered)} latest_timestamp={latest} ({latest_dt.isoformat()})")


if __name__ == "__main__":
    main()
