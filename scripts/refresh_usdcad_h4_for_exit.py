#!/usr/bin/env python3
"""Refresh only the USDCAD H4 data used by the open-position exit monitor."""
import csv
import subprocess
import tempfile
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "market" / "h4" / "usdcad.csv"
START = date.today() - timedelta(days=14)
END = date.today() + timedelta(days=1)

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="usdcad-h4-") as td:
        cmd = [
            "npx", "--yes", "dukascopy-node@1.50.0",
            "-i", "usdcad", "-from", START.isoformat(), "-to", END.isoformat(),
            "-t", "h4", "-f", "csv", "-p", "bid", "-v", "-s",
            "-dir", td, "-bs", "5", "-bp", "1500",
        ]
        subprocess.run(cmd, cwd=ROOT, check=True, timeout=900)
        files = sorted(Path(td).glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not files:
            raise RuntimeError("USDCAD H4 refresh produced no CSV")
        rows = {}
        if OUT.exists():
            with OUT.open(newline="") as f:
                for row in csv.DictReader(f):
                    if row.get("timestamp"):
                        rows[int(row["timestamp"])] = row
        with files[0].open(newline="") as f:
            fresh = list(csv.DictReader(f))
        if not fresh:
            raise RuntimeError("USDCAD H4 refresh CSV is empty")
        for row in fresh:
            if row.get("timestamp"):
                rows[int(row["timestamp"])] = row
        ordered = [rows[k] for k in sorted(rows)]
        tmp = OUT.with_suffix(".tmp")
        fields = ["timestamp", "open", "high", "low", "close", "volume"]
        with tmp.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for row in ordered:
                writer.writerow({k: row.get(k, "") for k in fields})
        tmp.replace(OUT)
        print(f"[OK] refreshed USDCAD H4; downloaded={len(fresh)} merged_total={len(ordered)} latest_timestamp={ordered[-1]['timestamp']}")

if __name__ == "__main__":
    main()
