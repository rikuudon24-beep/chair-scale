#!/usr/bin/env python3
"""Audit H1/H4/D1 market data before any rule research."""
import csv,json,sys
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[3]
CFG=json.loads((ROOT/"research/h1/config.json").read_text())
paths={"h1":ROOT/CFG["h1_path"],"h4":ROOT/CFG["raw_source_paths"]["h4"],"d1":ROOT/CFG["raw_source_paths"]["d1"]}
rows=[]
fail=False
for tf,base in paths.items():
    for pair in CFG["symbols"]:
        fp=base/f"{pair}.csv"
        if not fp.exists():
            rows.append((tf,pair,"MISSING",0,"")); fail=True; continue
        n=0; first=last=""; prev=None; gaps=0; bad_ohlc=0; dup=0; bad_ts=0
        with fp.open(newline="") as f:
            for r in csv.DictReader(f):
                ts=r.get("timestamp","")
                try:
                    t=int(ts); dt=datetime.fromtimestamp(t/1000,tz=timezone.utc)
                    first=first or dt.isoformat(); last=dt.isoformat()
                    if prev is not None and t<=prev: dup+=1
                    prev=t; n+=1
                    o,h,l,c=[float(r[x]) for x in ("open","high","low","close")]
                    if not (l<=o<=h and l<=c<=h): bad_ohlc+=1
                except Exception: bad_ts+=1
        rows.append((tf,pair,"OK",n,f"{first} -> {last}; bad_ohlc={bad_ohlc}; non_increasing={dup}; bad_ts={bad_ts}"))
        if n==0 or bad_ts or bad_ohlc or dup: fail=True
out=ROOT/"research/h1/results/data_audit.md"
out.parent.mkdir(parents=True,exist_ok=True)
lines=["# H1 Data Audit", "", f"- generated: {datetime.now(timezone.utc).isoformat()}", "", "|TF|Pair|Status|Rows|Details|","|---|---|---|---:|---|"]
for r in rows: lines.append("|"+"|".join(map(str,r))+"|")
out.write_text("\n".join(lines)+"\n")
print("\n".join(lines))
sys.exit(1 if fail else 0)
