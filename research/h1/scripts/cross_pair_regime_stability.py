#!/usr/bin/env python3
from pathlib import Path
import numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[3]; DATA=ROOT/"research/h1/results/datasets"; OUT=ROOT/"research/h1/results"
PAIRS=["usdjpy","eurjpy","gbpjpy","audjpy","eurusd","gbpusd","audusd","nzdusd","usdcad","usdchf","eurgbp","audnzd"]

def ps(pair): return .01 if "jpy" in pair else .0001

def simulate(x,pair,mask,direction,tp,sl,h=48):
    idx=np.flatnonzero(mask.fillna(False).to_numpy()); chosen=[]; nxt=-1
    for i in idx:
        if i<nxt or i+h>=len(x)-1: continue
        chosen.append(i); nxt=i+h+1
    op=x.open.to_numpy(); hi=x.high.to_numpy(); lo=x.low.to_numpy(); p=ps(pair); rr=[]
    for i in chosen:
        entry=op[i+1]; result=0
        th=entry+tp*p if direction=="long" else entry-tp*p
        st=entry-sl*p if direction=="long" else entry+sl*p
        for j in range(i+1,i+h+1):
            ht=hi[j]>=th if direction=="long" else lo[j]<=th
            hs=lo[j]<=st if direction=="long" else hi[j]>=st
            if ht and hs: result=-1; break
            if ht: result=tp/sl; break
            if hs: result=-1; break
        rr.append(result)
    if not rr:return None
    z=np.array(rr); gp=z[z>0].sum(); gl=-z[z<0].sum()
    return len(z),float((z>0).mean()),float(gp/gl) if gl else np.inf,float(z.mean())

def main():
    structures={
      "pullback_reversal":"trend_down & h4_bull & d1_bull",
      "pullback_reversal_rsi":"trend_down & d1_bull & rsi_up6",
      "mid_rsi_reversal":"trend_down & rsi55_60 & d1_bull",
      "pullback_reversal_macd":"trend_down & macd_pos & d1_bull",
    }
    rows=[]
    for pair in PAIRS:
      fp=DATA/f"{pair}.parquet"
      if not fp.exists(): continue
      x=pd.read_parquet(fp).sort_index()
      n=len(x); a=int(n*.6); b=int(n*.2); oos=x.iloc[a+b:].copy()
      for name,conds in structures.items():
        r=oos.rsi14
        aa={"trend_down":oos.trend_down,"d1_bull":oos.d1_close>oos.d1_open,
            "h4_bull":oos.h4_close>oos.h4_open,"rsi_up6":r-r.shift(6)>3,
            "rsi55_60":r.between(55,60),"macd_pos":oos.macd_hist>0}
        m=pd.Series(True,index=oos.index)
        for q in [q.strip() for q in conds.split("&")]: m &= aa[q].fillna(False)
        for tp in [50,75]:
          for sl in [50,75]:
            # First/second half of the untouched OOS period; each half is independently simulated.
            cut=len(oos)//2
            for half,part in [("oos_first",oos.iloc[:cut]),("oos_second",oos.iloc[cut:])]:
              mm=m.loc[part.index]
              q=simulate(part,pair,mm,"long",tp,sl)
              if q:
                tr,wr,pf,ex=q
                rows.append({"pair":pair,"structure":name,"period":half,"tp":tp,"sl":sl,"trades":tr,"win_rate":wr,"pf":pf,"expectancy_R":ex})
    df=pd.DataFrame(rows); df.to_csv(OUT/"cross_pair_regime_stability.csv",index=False)
    lines=["# H1 cross-pair OOS regime stability","","The four structures and TP/SL values are frozen from the prior cross-pair test. The untouched OOS segment is split chronologically into first and second halves. This is a stability diagnostic, not a rule-selection stage.","","|Pair|Structure|Period|TP|SL|Trades|Win|PF|Exp R|","|---|---|---|---:|---:|---:|---:|---:|---:|"]
    for _,r in df.iterrows(): lines.append(f"|{r.pair}|{r.structure}|{r.period}|{int(r.tp)}|{int(r.sl)}|{int(r.trades)}|{r.win_rate:.3f}|{r.pf:.3f}|{r.expectancy_R:.3f}|")
    (OUT/"cross_pair_regime_stability.md").write_text("\n".join(lines)+"\n")
if __name__=="__main__": main()
