#!/usr/bin/env python3
from pathlib import Path
import numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[3]; DATA=ROOT/"research/h1/results/datasets"; OUT=ROOT/"research/h1/results"

def split(x):
    n=len(x); a=int(n*.6); b=int(n*.2); return x.iloc[:a],x.iloc[a:a+b],x.iloc[a+b:]
def ps(pair): return .01 if "jpy" in pair else .0001

def atoms(x):
    r=x.rsi14
    return {
      "trend_down":x.trend_down,"d1_bull":x.d1_close>x.d1_open,"h4_bull":x.h4_close>x.h4_open,
      "rsi_up6":r-r.shift(6)>3,"rsi55_60":r.between(55,60),"far_ema200":x.dist_ema200_atr.abs()>=1.0,
      "macd_pos":x.macd_hist>0
    }

def simulate(x,pair,mask,direction,tp,sl,h=48):
    p=ps(pair); idx=np.flatnonzero(mask.fillna(False).to_numpy()); chosen=[]; nxt=-1
    for i in idx:
        if i<nxt or i+h>=len(x): continue
        chosen.append(i); nxt=i+h+1
    op=x.open.to_numpy(); hi=x.high.to_numpy(); lo=x.low.to_numpy()
    wins=[]; rmult=[]
    for i in chosen:
        entry=op[i+1]; hit=None
        for j in range(i+1,i+h+1):
            if direction=="long":
                th=entry+tp*p; st=entry-sl*p
                hit_tp=hi[j]>=th; hit_sl=lo[j]<=st
            else:
                th=entry-tp*p; st=entry+sl*p
                hit_tp=lo[j]<=th; hit_sl=hi[j]>=st
            if hit_tp and hit_sl: hit="sl"; break
            if hit_tp: hit="tp"; break
            if hit_sl: hit="sl"; break
        if hit=="tp": wins.append(1); rmult.append(tp/sl)
        elif hit=="sl": wins.append(0); rmult.append(-1)
        else:
            wins.append(0)
            if direction=="long": pnl=(x.close.iloc[i+h]-entry)/p
            else: pnl=(entry-x.close.iloc[i+h])/p
            rmult.append(pnl/sl)
    if not wins:return None
    w=np.array(wins); rr=np.array(rmult)
    gross_win=rr[rr>0].sum(); gross_loss=-rr[rr<0].sum()
    return {"trades":len(w),"win_rate":float(w.mean()),"pf":float(gross_win/gross_loss) if gross_loss else np.inf,"expectancy_R":float(rr.mean()),"total_R":float(rr.sum())}

def main():
    candidates=[
      ("gbpjpy","long","trend_down & h4_bull & d1_bull"),
      ("gbpjpy","long","trend_down & d1_bull & rsi_up6"),
      ("gbpjpy","long","trend_down & rsi55_60 & d1_bull"),
      ("gbpjpy","long","trend_down & macd_pos & d1_bull"),
    ]
    tps=[50,75,100,125,150]; sls=[25,35,50,60,75]
    rows=[]
    for pair,direction,conds in candidates:
        x=pd.read_parquet(DATA/f"{pair}.parquet").sort_index(); parts=split(x); names=[z.strip() for z in conds.split("&")]
        for sn,part in zip(["discovery","validation","oos"],parts):
            aa=atoms(part); m=pd.Series(True,index=part.index)
            for n in names:m &= aa[n]
            for tp in tps:
                for sl in sls:
                    q=simulate(part,pair,m,direction,tp,sl)
                    if q: rows.append({"pair":pair,"direction":direction,"conditions":conds,"split":sn,"tp":tp,"sl":sl,**q})
    df=pd.DataFrame(rows); df.to_csv(OUT/"precursor_tp_sl.csv",index=False)
    lines=["# H1 precursor TP/SL robustness","","Candidates are preselected from prior research. TP/SL are evaluated with next-open entry, non-overlapping trades, 48-H1 horizon, and conservative SL when both levels are touched in one candle.","","|Pair|Conditions|Split|TP|SL|Trades|Win|PF|Exp R|Total R|","|---|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for _,r in df.iterrows(): lines.append(f"|{r.pair}|{r.conditions}|{r.split}|{int(r.tp)}|{int(r.sl)}|{int(r.trades)}|{r.win_rate:.3f}|{r.pf:.3f}|{r.expectancy_R:.3f}|{r.total_R:.2f}|")
    (OUT/"precursor_tp_sl.md").write_text("\n".join(lines)+"\n")
if __name__=="__main__": main()
