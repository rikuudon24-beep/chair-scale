#!/usr/bin/env python3
from pathlib import Path
import pandas as pd, numpy as np
ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/"research/h1/results/datasets"; OUT=ROOT/"research/h1/results"
PAIRS=["usdjpy","eurjpy","gbpjpy"]
CONFIGS=[(40,75,48),(40,90,48),(40,100,48),(50,100,48)]

def split(x):
    n=len(x); a=int(n*.6); b=int(n*.2)
    return x.iloc[:a],x.iloc[a:a+b],x.iloc[a+b:]

def ids(x,mask,h):
    raw=np.flatnonzero(mask.to_numpy()); out=[]; nxt=-1
    for i in raw:
        if i<nxt or i+h>=len(x): continue
        out.append(i); nxt=i+h+1
    return out

def result(x,i,tp,sl,h):
    e=float(x.open.iloc[i+1]); hi=x.high.to_numpy(); lo=x.low.to_numpy(); p=.01
    for j in range(i+1,min(i+h+1,len(x))):
        ht=hi[j]>=e+tp*p; hs=lo[j]<=e-sl*p
        if ht and hs:return -1
        if hs:return -1
        if ht:return 1
    return 0

def metrics(vals):
    vals=np.array(vals,dtype=int); n=len(vals); w=(vals>0).sum()
    eq=np.cumsum(vals); peak=np.maximum.accumulate(np.r_[0,eq])[:-1]
    dd=peak-eq
    streak=cur=0
    for v in vals:
        if v<0: cur+=1; streak=max(streak,cur)
        else: cur=0
    gaps=np.diff(np.where(vals!=0)[0]) if n else np.array([])
    return {"trades":n,"wins":int(w),"win":w/n if n else np.nan,
            "net_r":int(vals.sum()),"max_dd_r":int(dd.max()) if len(dd) else 0,
            "max_loss_streak":streak,"signals_per_year":n/(5 if n else 1)}

def main():
    rows=[]
    for pair in PAIRS:
        data=pd.read_parquet(DATA/f"{pair}.parquet").sort_index()
        for sn,x in zip(["discovery","validation","oos"],split(data)):
            mask=x.trend_down&(x.h4_close>x.h4_open)&(x.d1_close>x.d1_open)&(x.adx14>=20)&((x.rsi14-x.rsi14.shift(6))>3)
            years=max((x.index[-1]-x.index[0]).days/365.25,1/365.25)
            for tp,sl,h in CONFIGS:
                vals=[result(x,i,tp,sl,h) for i in ids(x,mask,h)]
                m=metrics(vals); m.update({"pair":pair,"split":sn,"tp":tp,"sl":sl,"horizon":h,"years":years,"signals_per_year":m["trades"]/years})
                rows.append(m)
    df=pd.DataFrame(rows); df.to_csv(OUT/"stable_jpy_adx_rsi_risk_profile.csv",index=False)
    lines=["# Stable JPY ADX+RSI risk profile","","Frozen condition: trend_down & h4_bull & d1_bull & ADX>=20 & RSI14 change over 6 H1 bars > 3.","Metrics use binary TP/SL outcomes: +1R win, -1R loss, TIME=0. Selection is not performed here.",""]
    for cfg,g in df.groupby(["tp","sl","horizon"]):
        lines.append(f"## TP{cfg[0]}/SL{cfg[1]}/H{cfg[2]}")
        lines.append("|Pair|Split|Trades|Win|Net R|Max DD R|Max loss streak|Signals/year|")
        lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
        for _,r in g.iterrows():
            lines.append(f"|{r.pair}|{r.split}|{int(r.trades)}|{r.win:.3f}|{int(r.net_r)}|{int(r.max_dd_r)}|{int(r.max_loss_streak)}|{r.signals_per_year:.1f}|")
        lines.append("")
    (OUT/"stable_jpy_adx_rsi_risk_profile.md").write_text("\n".join(lines)+"\n")
    print("[OK] ADX+RSI risk profile complete")
if __name__=="__main__": main()
