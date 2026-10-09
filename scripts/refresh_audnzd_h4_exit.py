#!/usr/bin/env python3
"""Refresh confirmed AUD/NZD H4 candles from Yahoo hourly bars."""
import csv, json, time, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data/market/h4/audnzd.csv"
def main():
    now=datetime.now(timezone.utc)
    q=urllib.parse.urlencode({"period1":int((now-timedelta(days=60)).timestamp()),"period2":int(now.timestamp()),"interval":"60m","events":"history","includeAdjustedClose":"false"})
    url="https://query1.finance.yahoo.com/v8/finance/chart/AUDNZD=X?"+q
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=30) as r: payload=json.load(r)
    result=(payload.get("chart",{}).get("result") or [None])[0]
    if not result: raise RuntimeError("Yahoo returned no AUDNZD data")
    ts=result.get("timestamp") or []; quote=(result.get("indicators",{}).get("quote") or [{}])[0]
    bars={}
    for i,t in enumerate(ts):
        vals=[quote.get(k,[None]*len(ts))[i] for k in ("open","high","low","close")]
        if any(v is None for v in vals): continue
        bucket=(int(t)//14400)*14400
        bars.setdefault(bucket,[]).append((int(t),vals))
    fresh=[]
    now_ts=int(now.timestamp())
    for bucket,items in sorted(bars.items()):
        items.sort()
        if [x[0] for x in items] != [bucket+3600*n for n in range(4)]: continue
        if bucket+14400>now_ts: continue
        v=[x[1] for x in items]
        fresh.append({"timestamp":bucket*1000,"open":v[0][0],"high":max(x[1] for x in v),"low":min(x[2] for x in v),"close":v[-1][3],"volume":0})
    if len(fresh)<30: raise RuntimeError(f"Only {len(fresh)} complete AUDNZD H4 bars; exit state UNKNOWN")
    rows={}
    if OUT.exists():
        with OUT.open(newline="") as f:
            for row in csv.DictReader(f):
                if row.get("timestamp"): rows[int(float(row["timestamp"]))]=row
    for row in fresh: rows[int(row["timestamp"])]=row
    fields=["timestamp","open","high","low","close","volume"]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    tmp=OUT.with_suffix(".tmp")
    with tmp.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for k in sorted(rows): w.writerow({x:rows[k].get(x,"") for x in fields})
    tmp.replace(OUT)
    latest=max(int(x["timestamp"]) for x in fresh)
    age=(now_ts-latest//1000)/3600
    if age>8: raise RuntimeError(f"Latest complete AUDNZD H4 candle too old: {age:.1f}h")
    print(f"Updated AUDNZD complete H4 candles: {len(fresh)}; latest={datetime.fromtimestamp(latest/1000,timezone.utc).isoformat()}")
if __name__=="__main__": main()
