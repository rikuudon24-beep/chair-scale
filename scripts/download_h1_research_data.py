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

def read_valid_csv(path):
    """Reject empty, malformed, or OHLC-invalid downloads before merging."""
    if path.stat().st_size == 0:
        raise RuntimeError(f"empty download file: {path}")
    df = pd.read_csv(path)
    cols = ["timestamp", "open", "high", "low", "close", "volume"]
    missing = sorted(set(cols) - set(df.columns))
    if missing:
        raise RuntimeError(f"missing columns {missing}: {path}")
    if df.empty:
        raise RuntimeError(f"download contains header only: {path}")
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if df[cols].isna().any().any():
        raise RuntimeError(f"non-numeric or missing candle values: {path}")
    if (df[["open", "high", "low", "close"]] <= 0).any().any():
        raise RuntimeError(f"non-positive OHLC values: {path}")
    if (df["high"] < df[["open", "close", "low"]].max(axis=1)).any():
        raise RuntimeError(f"invalid high envelope: {path}")
    if (df["low"] > df[["open", "close", "high"]].min(axis=1)).any():
        raise RuntimeError(f"invalid low envelope: {path}")
    return df[cols]


def merge(pair, files):
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / f"{pair}.csv"
    rows = {}
    if final.exists():
        old = read_valid_csv(final)
        for r in old.to_dict("records"):
            rows[int(r["timestamp"])] = r

    valid_files = []
    errors = []
    for fp in files:
        try:
            valid_files.append((fp, read_valid_csv(fp)))
        except Exception as exc:
            errors.append(f"{fp.name}: {exc}")
    if not valid_files:
        raise RuntimeError("no valid download CSVs; " + "; ".join(errors[:3]))
    for fp, df in valid_files:
        for r in df.to_dict("records"):
            rows[int(r["timestamp"])] = r
    if not rows:
        raise RuntimeError("no valid rows after merge")
    z = pd.DataFrame(sorted(rows.values(), key=lambda r:int(r["timestamp"])))
    cols = ["timestamp","open","high","low","close","volume"]
    z = z[cols]
    # Only write after every input file has been validated and at least one
    # valid downloaded file is available; bad downloads never truncate cache.
    tmp = final.with_suffix(".csv.tmp")
    z.to_csv(tmp,index=False)
    tmp.replace(final)

def main():
  for pair in PAIRS:
    tmp = TMP / pair
    tmp.mkdir(parents=True, exist_ok=True)
    ok = False
    for attempt in range(1,4):
        # Isolate attempts so an empty newest response cannot shadow a prior
        # valid CSV from the same temp directory.
        attempt_tmp = tmp / f"attempt-{attempt}"
        attempt_tmp.mkdir(parents=True, exist_ok=True)
        cmd = [
            "npx","--yes","dukascopy-node@1.50.0",
            "-i",pair,"-from",START.isoformat(),"-to",END.isoformat(),
            "-t","h1","-f","csv","-p","bid","-v","-s","-dir",str(attempt_tmp),
            "-bs","5","-bp","1500"
        ]
        try:
            subprocess.run(cmd,cwd=ROOT,check=True,timeout=900)
            files = sorted(attempt_tmp.glob("*.csv"), key=lambda p:p.stat().st_mtime, reverse=True)
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


if __name__ == "__main__":
    main()
