#!/usr/bin/env python3
"""Download and consolidate H1 bid candles without touching H4/D1 data."""
import argparse,csv,json,subprocess,sys,time
from datetime import date,timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
CFG=json.loads((ROOT/"research/h1/config.json").read_text())
OUT=ROOT/"data/market/h1"

def normalize(r):
    try:
        vals=[float(r[k]) for k in ("open","high","low","close")]
    except Exception:
        return r,False
    hi=max(vals); lo=min(vals); changed=(hi!=float(r["high"]) or lo!=float(r["low"]))
    if changed:
        r["high"]=format(hi,".10f").rstrip("0").rstrip(".")
        r["low"]=format(lo,".10f").rstrip("0").rstrip(".")
    return r,changed

def merge(final,files):
    rows={}
    if final.exists():
        with final.open(newline="") as f:
            for r in csv.DictReader(f):
                if r.get("timestamp"): rows[r["timestamp"]]=r
    for fp in files:
        with fp.open(newline="") as f:
            for r in csv.DictReader(f):
                if r.get("timestamp"): rows[r["timestamp"]]=r
    if not rows: raise RuntimeError("no usable CSV rows")
    cols=["timestamp","open","high","low","close","volume"]
    ordered=sorted(rows.values(),key=lambda r:int(r["timestamp"]))
    repaired=0
    tmp=final.with_suffix(".tmp")
    with tmp.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
        for r in ordered:
            r,rep=normalize(r); repaired+=int(rep)
            w.writerow({c:r.get(c,"") for c in cols})
    tmp.replace(final)
    return len(ordered),repaired

def download(pair,start,end):
    OUT.mkdir(parents=True,exist_ok=True)
    tmp=ROOT/".download_tmp_h1"/pair
    tmp.mkdir(parents=True,exist_ok=True)
    cmd=["npx","--yes","dukascopy-node@1.50.0","-i",pair,"-from",start.isoformat(),"-to",end.isoformat(),"-t","h1","-f","csv","-p",CFG["price_type"],"-v","-s","-dir",str(tmp),"-bs","5","-bp","1500"]
    for attempt in range(1,4):
        try:
            subprocess.run(cmd,cwd=ROOT,check=True,timeout=1200)
            files=sorted(tmp.glob("*.csv"),key=lambda p:p.stat().st_mtime)
            if not files: raise RuntimeError("no CSV produced")
            n,rep=merge(OUT/f"{pair}.csv",files)
            print(f"[OK] {pair}: rows={n}, repaired={rep}",flush=True)
            return
        except Exception as e:
            print(f"[WARN] {pair} attempt {attempt}/3: {e}",flush=True)
            if attempt<3: time.sleep(5*attempt)
    raise RuntimeError(f"download failed: {pair}")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--start"); ap.add_argument("--end")
    a=ap.parse_args()
    start=date.fromisoformat(a.start) if a.start else date.fromisoformat(CFG["history_start"])
    end=date.fromisoformat(a.end) if a.end else date.today()+timedelta(days=1)
    bad=[]
    for pair in CFG["symbols"]:
        try: download(pair,start,end)
        except Exception as e: bad.append(str(e))
    if bad:
        print("[FAIL]\n"+"\n".join(bad)); sys.exit(2)

if __name__=="__main__": main()
