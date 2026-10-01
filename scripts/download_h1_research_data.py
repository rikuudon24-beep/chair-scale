#!/usr/bin/env python3
"""Download H1 research data without touching the frozen H4/D1 production pipeline."""
import subprocess, time
from datetime import date, timedelta
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PAIRS = ["usdjpy","eurjpy","gbpjpy","audjpy","eurusd","gbpusd","audusd","nzdusd","usdcad","usdchf","audnzd","eurgbp"]
OUT = ROOT / "data" / "market" / "h1"
TMP = ROOT / ".download_tmp" / "h1"
START = date(2021,1,1)
END = date.today() + timedelta(days=1)

def merge(pair, files):
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / f"{pair}.csv"
    rows = {}
    if final.exists():
        old = pd.read_csv(final)
        for r in old.to_dict("records"):
            if pd.notna(r.get("timestamp")): rows[int(r["timestamp"])] = r
    for fp in files:
        df = pd.read_csv(fp)
        for r in df.to_dict("records"):
            if pd.notna(r.get("timestamp")): rows[int(r["timestamp"])] = r
    if not rows: raise RuntimeError("no rows")
    z = pd.DataFrame(sorted(rows.values(), key=lambda r:int(r["timestamp"])))
    cols = ["timestamp","open","high","low","close","volume"]
    z = z[cols]
    z.to_csv(final,index=False)

for pair in PAIRS:
    tmp = TMP / pair
    tmp.mkdir(parents=True, exist_ok=True)
    ok = False
    for attempt in range(1,4):
        cmd = [
            "npx","--yes","dukascopy-node@1.50.0",
            "-i",pair,"-from",START.isoformat(),"-to",END.isoformat(),
            "-t","h1","-f","csv","-p","bid","-v","-s","-dir",str(tmp),
            "-bs","5","-bp","1500"
        ]
        try:
            subprocess.run(cmd,cwd=ROOT,check=True,timeout=900)
            files = sorted(tmp.glob("*.csv"), key=lambda p:p.stat().st_mtime, reverse=True)
            if not files: raise RuntimeError("no CSV produced")
            merge(pair, files)
            print(f"[OK] {pair} h1", flush=True)
            ok=True
            break
        except Exception as e:
            print(f"[WARN] {pair} attempt {attempt}/3: {e}", flush=True)
            time.sleep(5*attempt)
    if not ok:
        raise SystemExit(f"[FAIL] {pair} h1")
