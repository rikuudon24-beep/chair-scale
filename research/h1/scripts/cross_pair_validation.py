#!/usr/bin/env python3
from pathlib import Path
import numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[3]; DATA=ROOT/"research/h1/results/datasets"; OUT=ROOT/"research/h1/results"
PAIRS=["usdjpy","eurjpy","gbpjpy","audjpy","eurusd","gbpusd","audusd","nzdusd","usdcad","usdchf","eurgbp","audnzd"]

def split(x):
    n=len(x); a=int(n*.6); b=int(n*.2); return x.iloc[:a],x.iloc[a:a+b],x.iloc[a+b:]
def ps(pair): return .01 if "jpy" in pair else .0001

def simulate(x,pair,mask,direction,tp,sl,h=48):
    p=ps(pair); idx=np.flatnonzero(mask.fillna(False).to_numpy()); chosen=[]; nxt=-1
    for i in idx:
        if i<nxt or i+h>=len(x): continue
        chosen.append(i); nxt=i+h+1
    op=x.open.to_numpy(); hi=x.high.to_numpy(); lo=x.low.to_numpy()
    rr=[]
    for i in chosen:
        entry=op[i+1]; result=None
        for j in range(i+1,i+h+1):
            th=entry+tp*p if direction=="long" else entry-tp*p
            st=entry-sl*p if direction=="long" else entry+sl*p
            ht=hi[j]>=th if direction=="long" else lo[j]<=th
            hs=lo[j]<=st if direction=="long" else hi[j]>=st
            if ht and hs: result=-1; break
            if ht: result=tp/sl; break
            if hs: result=-1; break
        if result is None: result=0
        rr.append(result)
    if not rr:return None
    z=np.array(rr); wins=(z>0)
    gp=z[z>0].sum(); gl=-z[z<0].sum()
    return {"trades":len(z),"win_rate":float(wins.mean()),"pf":float(gp/gl) if gl else np.inf,"expectancy_R":float(z.mean())}

def main():
    # Structure discovered from prior GBPJPY research; no pair-specific parameter tuning.
    structures={
      "pullback_reversal":"trend_down & h4_bull & d1_bull",
      "pullback_reversal_rsi":"trend_down & d1_bull & rsi_up6",
      "mid_rsi_reversal":"trend_down & rsi55_60 & d1_bull",
      "pullback_reversal_macd":"trend_down & macd_pos & d1_bull",
    }
    tps=[50,75]; sls=[50,75]
    rows=[]
    for pair in PAIRS:
      fp=DATA/f"{pair}.parquet"
      if not fp.exists(): continue
      x=pd.read_parquet(fp).sort_index(); parts=split(x)
      for name,conds in structures.items():
        for sn,part in zip(["discovery","validation","oos"],parts):
          r=part.rsi14
          aa={
            "trend_down":part.trend_down,"d1_bull":part.d1_close>part.d1_open,
            "h4_bull":part.h4_close>part.h4_open,"rsi_up6":r-r.shift(6)>3,
            "rsi55_60":r.between(55,60),"macd_pos":part.macd_hist>0,
          }
          m=pd.Series(True,index=part.index)
          for n in [q.strip() for q in conds.split("&")]: m &= aa[n].fillna(False)
          for tp in tps:
            for sl in sls:
              q=simulate(part,pair,m,"long",tp,sl)
              if q: rows.append({"pair":pair,"structure":name,"split":sn,"tp":tp,"sl":sl,**q})
    df=pd.DataFrame(rows); df.to_csv(OUT/"cross_pair_validation.csv",index=False)
    lines=["# H1 cross-pair validation","","Structures were frozen from prior GBPJPY research and applied unchanged to all configured pairs. No pair-specific selection was performed here.","","|Pair|Structure|Split|TP|SL|Trades|Win|PF|Exp R|","|---|---|---|---:|---:|---:|---:|---:|---:|"]
    for _,r in df.iterrows(): lines.append(f"|{r.pair}|{r.structure}|{r.split}|{int(r.tp)}|{int(r.sl)}|{int(r.trades)}|{r.win_rate:.3f}|{r.pf:.3f}|{r.expectancy_R:.3f}|")
    (OUT/"cross_pair_validation.md").write_text("\n".join(lines)+"\n")
if __name__=="__main__": main()
