#!/usr/bin/env python3
from pathlib import Path
import pandas as pd, numpy as np

ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/"research/h1/results/datasets"; OUT=ROOT/"research/h1/results"
PAIRS=["usdjpy","eurjpy","gbpjpy"]
CONFIGS=[(40,75,48),(40,100,48),(40,90,48),(50,100,48)]

def result(x,i,tp,sl,h):
    e=float(x.open.iloc[i+1]); hi=x.high.to_numpy(); lo=x.low.to_numpy(); p=.01
    for j in range(i+1,min(i+h+1,len(x))):
        ht=hi[j]>=e+tp*p; hs=lo[j]<=e-sl*p
        if ht and hs:return -1.0
        if hs:return -1.0
        if ht:return 1.0
    return 0.0

def ids(x,mask,h):
    raw=np.flatnonzero(mask.to_numpy()); out=[]; nxt=-1
    for i in raw:
        if i<nxt or i+h>=len(x): continue
        out.append(i); nxt=i+h+1
    return out

def stats(x,mask,tp,sl,h):
    vals=[result(x,i,tp,sl,h) for i in ids(x,mask,h)]
    n=len(vals); w=sum(v>0 for v in vals); gp=sum(v for v in vals if v>0); gl=-sum(v for v in vals if v<0)
    return n,(w/n if n else np.nan),(gp/gl if gl else (float("inf") if gp else np.nan)),(sum(vals)/n if n else np.nan)

def main():
    rows=[]
    for pair in PAIRS:
        data=pd.read_parquet(DATA/f"{pair}.parquet").sort_index()
        n=len(data); start=int(n*.8); oos=data.iloc[start:].copy()
        mid=len(oos)//2
        halves=[("oos_first",oos.iloc[:mid]),("oos_second",oos.iloc[mid:])]
        for name,x in halves:
            mask=x.trend_down & (x.h4_close>x.h4_open) & (x.d1_close>x.d1_open) & (x.adx14>=20) & ((x.rsi14-x.rsi14.shift(6))>3)
            for tp,sl,h in CONFIGS:
                ntr,win,pf,ex=stats(x,mask,tp,sl,h)
                rows.append({"pair":pair,"period":name,"tp":tp,"sl":sl,"horizon":h,"trades":ntr,"win":win,"pf":pf,"exp_r":ex})
    df=pd.DataFrame(rows); df.to_csv(OUT/"stable_jpy_adx_rsi_period_stability.csv",index=False)
    lines=["# Stable JPY ADX+RSI period stability","","Frozen condition: trend_down & h4_bull & d1_bull & ADX>=20 & RSI14 change over 6 H1 bars > 3. OOS is split chronologically into first and second halves. No selection on these halves.",""]
    for (tp,sl,h),g in df.groupby(["tp","sl","horizon"]):
        lines.append(f"## TP{tp}/SL{sl}/H{h}")
        lines.append("|Pair|OOS first n|Win|PF|ExpR|OOS second n|Win|PF|ExpR|")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
        for pair in PAIRS:
            a=g[(g.pair==pair)&(g.period=="oos_first")].iloc[0]
            b=g[(g.pair==pair)&(g.period=="oos_second")].iloc[0]
            lines.append(f"|{pair}|{int(a.trades)}|{a.win:.3f}|{a.pf:.3f}|{a.exp_r:.3f}|{int(b.trades)}|{b.win:.3f}|{b.pf:.3f}|{b.exp_r:.3f}|")
        lines.append("")
    (OUT/"stable_jpy_adx_rsi_period_stability.md").write_text("\n".join(lines)+"\n")
    print("[OK] ADX+RSI OOS period stability complete")
if __name__=="__main__": main()
