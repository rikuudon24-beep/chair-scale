#!/usr/bin/env python3
from pathlib import Path
import pandas as pd, numpy as np, math

ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/"research/h1/results/datasets"
OUT=ROOT/"research/h1/results"
PAIRS=["usdjpy","eurjpy","gbpjpy"]

def split(x):
    n=len(x); a=int(n*.6); b=int(n*.2)
    return x.iloc[:a],x.iloc[a:a+b],x.iloc[a+b:]

def ps(pair): return .01

def wilson(k,n,z=1.96):
    if n==0:return 0.0
    p=k/n; d=1+z*z/n
    return (p+z*z/(2*n)-z*math.sqrt((p*(1-p)+z*z/(4*n))/n))/d

def atoms(x):
    r=x.rsi14
    a={
      "adx20+":x.adx14>=20,"adx25+":x.adx14>=25,
      "rsi<40":r<40,"rsi40_45":r.between(40,45),"rsi45_55":r.between(45,55),
      "rsi55_60":r.between(55,60),"rsi>60":r>60,
      "macd_pos":x.macd_hist>0,"macd_neg":x.macd_hist<0,
      "atr_above_med":x.atr14>x.atr14.rolling(200,min_periods=100).median(),
      "bb_narrow":x.bb_width<x.bb_width.rolling(200,min_periods=100).median(),
      "near_ema20":x.dist_ema20_atr.abs()<=.5,"far_ema200":x.dist_ema200_atr.abs()>=1.0,
      "rsi_up6":r-r.shift(6)>3,"adx_up6":x.adx14-x.adx14.shift(6)>2,
      "break20_up":x.break20_up,"break20_down":x.break20_down,
      "w1_bull":x.w1_close>x.w1_open,"w1_bear":x.w1_close<x.w1_open}
    return {k:v.fillna(False) for k,v in a.items()}

def ids(x,mask):
    raw=np.flatnonzero(mask.to_numpy()); chosen=[]; nxt=-1
    for i in raw:
        if i<nxt or i+48>=len(x): continue
        chosen.append(i); nxt=i+49
    return chosen

def trade(x,i,tp=50,sl=75):
    entry=float(x.open.iloc[i+1]); hi=x.high.to_numpy(); lo=x.low.to_numpy()
    for j in range(i+1,min(i+49,len(x))):
        ht=hi[j]>=entry+tp*.01; hs=lo[j]<=entry-sl*.01
        if ht and hs:return -1.0
        if hs:return -1.0
        if ht:return 1.0
    return 0.0

def evaluate(x,mask):
    vals=[trade(x,i) for i in ids(x,mask)]
    n=len(vals); w=sum(v>0 for v in vals); gp=sum(v for v in vals if v>0); gl=-sum(v for v in vals if v<0)
    return n,w/n if n else np.nan,wilson(w,n),gp/gl if gl else (float("inf") if gp else 0.0),sum(vals)/n if n else np.nan

def main():
    data={p:pd.read_parquet(DATA/f"{p}.parquet").sort_index() for p in PAIRS}
    # Use the already-selected pooled Discovery shortlist; this script does not add candidates.
    src=pd.read_csv(OUT/"stable_jpy_filter_search.csv")
    discovery=src[src.split=="discovery"].copy()
    candidates=discovery.sort_values(["lcb95","win","trades"],ascending=False).head(30)
    rows=[]
    for cond in candidates.conditions:
        extra=[s.strip() for s in cond.split("&")[3:]]
        for pair in PAIRS:
            for split_name,ix in [("validation",1),("oos",2)]:
                x=split(data[pair])[ix]; aa=atoms(x)
                m=x.trend_down & (x.h4_close>x.h4_open) & (x.d1_close>x.d1_open)
                for c in extra:m &= aa[c]
                n,w,l,pf,ex=evaluate(x,m)
                rows.append({"conditions":cond,"pair":pair,"split":split_name,"trades":n,"win":w,"lcb95":l,"pf":pf,"exp_r":ex})
    df=pd.DataFrame(rows)
    df.to_csv(OUT/"stable_jpy_filter_stability.csv",index=False)
    summaries=[]
    for cond,g in df.groupby("conditions"):
        v=g[g.split=="validation"].set_index("pair"); o=g[g.split=="oos"].set_index("pair")
        summaries.append({
          "conditions":cond,
          "val_min_trades":int(v.trades.min()),"val_min_win":float(v.win.min()),
          "val_min_pf":float(v.pf.replace(np.inf,np.nan).min(skipna=True)),
          "oos_min_trades":int(o.trades.min()),"oos_min_win":float(o.win.min()),
          "oos_min_pf":float(o.pf.replace(np.inf,np.nan).min(skipna=True)),
          "oos_all_positive":bool((o.exp_r>0).all()),
          "val_all_positive":bool((v.exp_r>0).all())})
    sm=pd.DataFrame(summaries).sort_values(["oos_all_positive","val_all_positive","oos_min_pf","val_min_pf"],ascending=False)
    sm.to_csv(OUT/"stable_jpy_filter_stability_summary.csv",index=False)
    lines=["# Stable JPY filter pair stability","","Pair-level diagnostic for the pooled Discovery shortlist. No candidate selection is performed here; Validation/OOS are evaluation only.","","|Conditions|Val min n|Val min win|Val min PF|OOS min n|OOS min win|OOS min PF|Val all +|OOS all +|","|---|---:|---:|---:|---:|---:|---:|:---:|:---:|"]
    for _,r in sm.iterrows():
        lines.append(f"|{r.conditions}|{int(r.val_min_trades)}|{r.val_min_win:.3f}|{r.val_min_pf:.3f}|{int(r.oos_min_trades)}|{r.oos_min_win:.3f}|{r.oos_min_pf:.3f}|{str(r.val_all_positive)}|{str(r.oos_all_positive)}|")
    (OUT/"stable_jpy_filter_stability.md").write_text("\n".join(lines)+"\n")
    print(f"[OK] pair stability evaluated for {len(candidates)} candidates")

if __name__=="__main__": main()
