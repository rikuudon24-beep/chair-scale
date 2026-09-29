#!/usr/bin/env python3
from pathlib import Path
import math, numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/"research/h1/results/datasets"
OUT=ROOT/"research/h1/results"

def split(x):
    n=len(x); a=int(n*.6); b=int(n*.2)
    return x.iloc[:a],x.iloc[a:a+b],x.iloc[a+b:]

def ps(pair): return .01 if "jpy" in pair else .0001

def atoms(x):
    r=x.rsi14
    a={
      "break20_up":x.break20_up,"break20_down":x.break20_down,
      "trend_up":x.trend_up,"trend_down":x.trend_down,
      "adx20+":x.adx14>=20,"adx25+":x.adx14>=25,
      "rsi<40":r<40,"rsi40_45":r.between(40,45),"rsi45_55":r.between(45,55),
      "rsi55_60":r.between(55,60),"rsi>60":r>60,
      "macd_pos":x.macd_hist>0,"macd_neg":x.macd_hist<0,
      "atr_above_med":x.atr14>x.atr14.rolling(200,min_periods=100).median(),
      "bb_narrow":x.bb_width<x.bb_width.rolling(200,min_periods=100).median(),
      "near_ema20":x.dist_ema20_atr.abs()<=.5,
      "far_ema200":x.dist_ema200_atr.abs()>=1.0,
      "h4_bull":x.h4_close>x.h4_open,"h4_bear":x.h4_close<x.h4_open,
      "d1_bull":x.d1_close>x.d1_open,"d1_bear":x.d1_close<x.d1_open,
      "w1_bull":x.w1_close>x.w1_open,"w1_bear":x.w1_close<x.w1_open,
      "rsi_up6":r-r.shift(6)>3,"rsi_down6":r-r.shift(6)<-3,
      "adx_up6":x.adx14-x.adx14.shift(6)>2,
    }
    return {k:v.fillna(False) for k,v in a.items()}

def quality(x,pair,mask,direction):
    p=ps(pair); idx=np.flatnonzero(mask.fillna(False).to_numpy())
    chosen=[]; nxt=-1
    for i in idx:
        if i<nxt or i+48>=len(x): continue
        chosen.append(i); nxt=i+49
    if not chosen: return {}
    op=x.open.to_numpy(); hi=x.high.to_numpy(); lo=x.low.to_numpy()
    rows=[]
    for i in chosen:
        entry=op[i+1]
        fh=hi[i+1:i+49]; fl=lo[i+1:i+49]
        if direction=="long":
            mfe=(np.max(fh)-entry)/p; mae=(entry-np.min(fl))/p
            hit=np.max(fh)-entry>=100*p
            target=next((j+1 for j,v in enumerate(fh) if v-entry>=100*p),np.nan)
        else:
            mfe=(entry-np.min(fl))/p; mae=(np.max(fh)-entry)/p
            hit=entry-np.min(fl)>=100*p
            target=next((j+1 for j,v in enumerate(fl) if entry-v>=100*p),np.nan)
        rows.append((hit,mfe,mae,target))
    z=np.array(rows,dtype=float)
    return {
      "trades":len(rows),
      "hit_rate":float(z[:,0].mean()),
      "mfe_median_pips":float(np.median(z[:,1])),
      "mfe_p75_pips":float(np.percentile(z[:,1],75)),
      "mae_median_pips":float(np.median(z[:,2])),
      "mae_p75_pips":float(np.percentile(z[:,2],75)),
      "target100_median_h1":float(np.nanmedian(z[:,3])) if np.isfinite(z[:,3]).any() else np.nan,
      "target100_p25_h1":float(np.nanpercentile(z[:,3],25)) if np.isfinite(z[:,3]).any() else np.nan,
      "target100_p75_h1":float(np.nanpercentile(z[:,3],75)) if np.isfinite(z[:,3]).any() else np.nan,
    }

def main():
    src=OUT/"precursor_candidates_followup.csv"
    if not src.exists(): return
    base=pd.read_csv(src)
    keys=base[["pair","direction","conditions"]].drop_duplicates()
    out=[]
    for _,r in keys.iterrows():
        x=pd.read_parquet(DATA/f"{r.pair}.parquet").sort_index()
        parts=split(x)
        names=[s.strip() for s in r.conditions.split("&")]
        for sn,part in zip(["discovery","validation","oos"],parts):
            aa=atoms(part); m=pd.Series(True,index=part.index)
            for name in names: m &= aa[name]
            q=quality(part,r.pair,m,r.direction)
            if q: out.append({"pair":r.pair,"direction":r.direction,"conditions":r.conditions,"split":sn,**q})
    pd.DataFrame(out).to_csv(OUT/"precursor_trade_quality.csv",index=False)
    if out:
        df=pd.DataFrame(out)
        lines=["# H1 precursor trade quality","","Metrics use next H1 open entry and non-overlapping 48-H1 outcome windows. MFE/MAE are excursion over the full window; target100_h1 is first H1 bar reaching +100 pips.","","|Pair|Dir|Conditions|Split|Trades|Hit|MFE med|MFE p75|MAE med|MAE p75|100p med H1|100p p25|100p p75|","|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for _,r in df.iterrows():
            lines.append(f"|{r.pair}|{r.direction}|{r.conditions}|{r.split}|{int(r.trades)}|{r.hit_rate:.3f}|{r.mfe_median_pips:.1f}|{r.mfe_p75_pips:.1f}|{r.mae_median_pips:.1f}|{r.mae_p75_pips:.1f}|{r.target100_median_h1:.1f}|{r.target100_p25_h1:.1f}|{r.target100_p75_h1:.1f}|")
        (OUT/"precursor_trade_quality.md").write_text("\n".join(lines)+"\n")

if __name__=="__main__": main()
