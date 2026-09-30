#!/usr/bin/env python3
from pathlib import Path
import pandas as pd, numpy as np

ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/"research/h1/results/datasets"
OUT=ROOT/"research/h1/results"
PAIRS=["usdjpy","eurjpy","gbpjpy"]
CONFIGS=[(40,75,48),(40,90,48),(40,100,48),(50,100,48)]
COSTS=[0.5,1.0,2.0,3.0,5.0]

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

def metrics(vals,tp,sl,cost):
    vals=np.asarray(vals,dtype=int)
    resolved=vals!=0
    r=np.where(vals>0,(tp-cost)/sl,np.where(vals<0,-(sl+cost)/sl,0.0))
    rr=r[resolved]
    n=len(vals); rn=len(rr)
    wins=int((vals>0).sum())
    eq=np.cumsum(r); peak=np.maximum.accumulate(np.r_[0,eq])[:-1]
    dd=peak-eq
    streak=cur=0
    for v in vals:
        if v<0: cur+=1; streak=max(streak,cur)
        else: cur=0
    gross_profit=rr[rr>0].sum()
    gross_loss=-rr[rr<0].sum()
    pf=gross_profit/gross_loss if gross_loss>0 else np.inf
    return {
        "signals":n,"resolved":rn,"win":wins/rn if rn else np.nan,
        "net_r":float(rr.sum()),"expectancy_r":float(rr.mean()) if rn else np.nan,
        "pf":float(pf),"max_dd_r":float(dd.max()) if len(dd) else 0,
        "max_loss_streak":streak
    }

def main():
    rows=[]
    for pair in PAIRS:
        data=pd.read_parquet(DATA/f"{pair}.parquet").sort_index()
        for split_name,x in zip(["discovery","validation","oos"],split(data)):
            mask=x.trend_down&(x.h4_close>x.h4_open)&(x.d1_close>x.d1_open)&(x.adx14>=20)&((x.rsi14-x.rsi14.shift(6))>3)
            for tp,sl,h in CONFIGS:
                vals=[result(x,i,tp,sl,h) for i in ids(x,mask,h)]
                for cost in COSTS:
                    m=metrics(vals,tp,sl,cost)
                    m.update({"pair":pair,"split":split_name,"tp":tp,"sl":sl,"horizon":h,"cost_pips":cost})
                    rows.append(m)
    df=pd.DataFrame(rows)
    df.to_csv(OUT/"stable_jpy_adx_rsi_cost_sensitivity.csv",index=False)
    lines=["# Stable JPY ADX+RSI cost sensitivity","","Frozen condition: trend_down & h4_bull & d1_bull & ADX>=20 & RSI14 change over 6 H1 bars > 3.","TP/SL triggers are unchanged. Cost is modeled as a round-trip pip deduction from every resolved trade; TIME trades are excluded from resolved P&L because their exit price is not modeled.",""]
    for cfg,g in df.groupby(["tp","sl","horizon"]):
        lines.append(f"## TP{cfg[0]}/SL{cfg[1]}/H{cfg[2]}")
        lines.append("|Pair|Split|Cost pips|Signals|Resolved|Win|PF|Expectancy R|Net R|")
        lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|")
        for _,r in g.iterrows():
            lines.append(f"|{r.pair}|{r.split}|{r.cost_pips:.1f}|{int(r.signals)}|{int(r.resolved)}|{r.win:.3f}|{r.pf:.3f}|{r.expectancy_r:.3f}|{r.net_r:.2f}|")
        lines.append("")
    (OUT/"stable_jpy_adx_rsi_cost_sensitivity.md").write_text("\n".join(lines)+"\n")
    print("[OK] ADX+RSI cost sensitivity complete")

if __name__=="__main__": main()
