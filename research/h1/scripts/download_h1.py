#!/usr/bin/env python3
"""Download H1 bid candles for the H1 research universe.

Uses the repository's existing Dukascopy downloader convention but writes only
to data/market/h1. Existing H4/D1 files are never touched.
"""

import argparse
import json
import subprocess
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CFG = json.loads((ROOT / "research/h1/config.json").read_text())
OUT = ROOT / "data" / "market" / "h1"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start")
    ap.add_argument("--end")
    args = ap.parse_args()

    start = date.fromisoformat(args.start) if args.start else date.fromisoformat(CFG["history_start"])
    end = date.fromisoformat(args.end) if args.end else date.today() + timedelta(days=1)
    OUT.mkdir(parents=True, exist_ok=True)

    failed = []
    for pair in CFG["symbols"]:
        tmp = ROOT / ".download_tmp_h1" / pair
        tmp.mkdir(parents=True, exist_ok=True)
        cmd = [
            "npx", "--yes", "dukascopy-node@1.50.0",
            "-i", pair, "-from", start.isoformat(), "-to", end.isoformat(),
            "-t", "h1", "-f", "csv", "-p", CFG["price_type"],
            "-v", "-s", "-dir", str(tmp), "-bs", "5", "-bp", "1500"
        ]
        try:
            subprocess.run(cmd, cwd=ROOT, check=True, timeout=900)
            csvs = sorted(tmp.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
            if not csvs:
                raise RuntimeError("no CSV produced")
            # Keep raw H1 acquisition isolated. Consolidation/repair is a later audited step.
            (OUT / f"{pair}.csv").write_bytes(csvs[0].read_bytes())
            print(f"[OK] {pair}")
        except Exception as exc:
            failed.append(f"{pair}: {exc}")

    if failed:
        print("[FAIL]")
        print("\n".join(failed))
        raise SystemExit(2)

if __name__ == "__main__":
    main()
