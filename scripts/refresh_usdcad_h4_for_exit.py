#!/usr/bin/env python3
"""Refresh USDCAD H4 data for the open-position exit monitor with retries."""
import csv
import subprocess
import tempfile
import time
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "market" / "h4" / "usdcad.csv"
START = date.today() - timedelta(days=14)
END_CANDIDATES = [date.today(), date.today() + timedelta(days=1)]

def download_once(start, end, attempt):
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
        with files[0].open(newline="") as f:
            rows = list(csv.DictReader(f))
        rows = [r for r in rows if r.get("timestamp") and r.get("close")]
        if len(rows) < 5:
            raise RuntimeError(f"attempt {attempt}: too few usable H4 rows ({len(rows)})")
        return rows

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fresh = None
    errors = []
    for attempt in range(1, 4):
        end = END_CANDIDATES[(attempt - 1) % len(END_CANDIDATES)]
        try:
            fresh = download_once(START, end, attempt)
            print(f"[OK] Dukascopy returned {len(fresh)} USDCAD H4 rows on attempt {attempt}")
            break
        except Exception as exc:
            errors.append(str(exc))
            print(f"[WARN] {exc}", flush=True)
            if attempt < 3:
                time.sleep(10 * attempt)
    if fresh is None:
        raise RuntimeError("USDCAD H4 refresh failed after 3 attempts: " + " | ".join(errors))

    rows = {}
    if OUT.exists():
        with OUT.open(newline="") as f:
            for row in csv.DictReader(f):
                if row.get("timestamp"):
                    rows[int(row["timestamp"])] = row
    for row in fresh:
        rows[int(row["timestamp"])] = row
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
    print(f"[OK] merged USDCAD H4 rows={len(ordered)} latest_timestamp={latest}")

if __name__ == "__main__":
    main()
