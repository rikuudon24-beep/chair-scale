#!/usr/bin/env python3
from pathlib import Path
import numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"research/h1/results/datasets"
OUT=ROOT/"research/h1/results"
PAIRS=["usdjpy","eurjpy","gbpjpy","usdchf","audusd","audnzd"]
CANDIDATES=[
 ("usdjpy","pullback_reversal_rsi",50,75),
 ("eurjpy","pullback_reversal_rsi",50,75),
 ("gbpjpy","pullback_reversal",75,50),
 ("usdchf","pullback_reversal_rsi",50,50),
 ("audusd","pullback_reversal_rsi",50,75),
 ("audnzd","pullback_reversal",50,50),
]
COSTS=[0.5,1.0,2.0,3.0,5.0]

def split(x):
    n=len(x); a=int(n*.6); b=int(n*.2)
    return x.iloc[:a],x.iloc[a:a+b],x.iloc[a+b:]

def pip_size(pair): return .01 if "jpy" in pair else .0001

def mask_for(part, structure):
    r=part.rsi14
    aa={
      "trend_down":part.trend_down,
      "d1_bull":part.d1_close>part.d1_open,
      "h4_bull":part.h4_close>part.h4_open,
      "rsi_up6":r-r.shift(6)>3,
      "rsi55_60":r.between(55,60),
      "macd_pos":part.macd_hist>0,
    }
    conds={
      "pullback_reversal":"trend_down & h4_bull & d1_bull",
      "pullback_reversal_rsi":"trend_down & d1_bull & rsi_up6",
      "mid_rsi_reversal":"trend_down & rsi55_60 & d1_bull",
      "pullback_reversal_macd":"trend_down & macd_pos & d1_bull",
    }[structure]
    m=pd.Series(True,index=part.index)
    for n in conds.split("&"): m &= aa[n.strip()].fillna(False)
    return m

def simulate(part,pair,mask,tp,sl,h=48):
    p=pip_size(pair)
    idx=np.flatnonzero(mask.to_numpy())
    chosen=[]; nxt=-1
    for i in idx:
        if i<nxt or i+h>=len(part): continue
        chosen.append(i); nxt=i+h+1
    op=part.open.to_numpy(); hi=part.high.to_numpy(); lo=part.low.to_numpy()
    vals=[]
    for i in chosen:
        e=op[i+1]; out=0
        th=e+tp*p; st=e-sl*p
        for j in range(i+1,i+h+1):
            ht=hi[j]>=th; hs=lo[j]<=st
            if ht and hs: out=-1; break
            if ht: out=1; break
            if hs: out=-1; break
        vals.append(out)
    return np.asarray(vals,dtype=int)

def metrics(vals,tp,sl,cost):
    resolved=vals!=0
    v=vals[resolved]
    if len(v)==0:
        return dict(signals=len(vals),resolved=0,wins=0,win_rate=np.nan,pf=np.nan,expectancy_R=np.nan,net_R=0)
    r=np.where(v>0,(tp-cost)/sl,-(sl+cost)/sl)
    wins=int((v>0).sum()); losses=int((v<0).sum())
    gp=r[r>0].sum(); gl=-r[r<0].sum()
    return dict(
      signals=len(vals),resolved=len(v),wins=wins,win_rate=wins/len(v),
      pf=float(gp/gl) if gl else np.inf,expectancy_R=float(r.mean()),net_R=float(r.sum())
    )

rows=[]
for pair,structure,tp,sl in CANDIDATES:
    fp=DATA/f"{pair}.parquet"
    if not fp.exists(): continue
    x=pd.read_parquet(fp).sort_index()
    for sn,part in zip(["discovery","validation","oos"],split(x)):
        vals=simulate(part,pair,mask_for(part,structure),tp,sl)
        for cost in COSTS:
            rows.append({"pair":pair,"structure":structure,"split":sn,"tp":tp,"sl":sl,"cost_pips":cost,**metrics(vals,tp,sl,cost)})
df=pd.DataFrame(rows)
df.to_csv(OUT/"H1_CANDIDATE_COST_SENSITIVITY.csv",index=False)

lines=[
"# H1 candidate cost sensitivity",
"",
"Only pair-specific candidates that passed the prior OOS routing gate are tested.",
"Signal definitions and TP/SL are unchanged from cross_pair_validation.py.",
"Cost is deducted from every resolved trade; TIME outcomes remain unresolved and contribute zero P&L.",
"",
"|Pair|Structure|Split|TP|SL|Cost|Signals|Resolved|Win|PF|Exp R|Net R|",
"|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
]
for _,r in df.iterrows():
    lines.append(f"|{r.pair}|{r.structure}|{r.split}|{int(r.tp)}|{int(r.sl)}|{r.cost_pips:.1f}|{int(r.signals)}|{int(r.resolved)}|{r.win_rate:.3f}|{r.pf:.3f}|{r.expectancy_R:.3f}|{r.net_R:.2f}|")
(OUT/"H1_CANDIDATE_COST_SENSITIVITY.md").write_text("\n".join(lines)+"\n")
print("[OK] H1 candidate cost sensitivity")

# workflow trigger checkpoint
