#!/usr/bin/env python3
from pathlib import Path
import math, numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/"research/h1/results/datasets"
OUT=ROOT/"research/h1/results"

PAIRS=["usdjpy","eurjpy","gbpjpy"]
STRUCTURES={
    "pullback_reversal":["trend_down","h4_bull","d1_bull"],
    "pullback_reversal_rsi":["trend_down","d1_bull","rsi_up6"],
}
TP_SL=[(50,50),(50,75),(75,50),(75,75)]

def ps(pair): return .01 if "jpy" in pair else .0001

def atoms(x):
    r=x.rsi14
    return {
      "trend_down":x.trend_down,
      "h4_bull":x.h4_close>x.h4_open,
      "d1_bull":x.d1_close>x.d1_open,
      "rsi_up6":r-r.shift(6)>3,
    }

def trades(x,pair,mask,direction,tp,sl):
    p=ps(pair); idx=np.flatnonzero(mask.fillna(False).to_numpy())
    chosen=[]; nxt=-1
    for i in idx:
        if i<nxt or i+48>=len(x): continue
        chosen.append(i); nxt=i+49
    op=x.open.to_numpy(); hi=x.high.to_numpy(); lo=x.low.to_numpy()
    rows=[]
    for i in chosen:
        entry=op[i+1]
        hit=None
        for j in range(i+1,min(i+49,len(x))):
            if direction=="long":
                tp_hit=hi[j]>=entry+tp*p; sl_hit=lo[j]<=entry-sl*p
            else:
                tp_hit=lo[j]<=entry-tp*p; sl_hit=hi[j]>=entry+sl*p
            if tp_hit and sl_hit: hit="SL"; end=j; break
            if sl_hit: hit="SL"; end=j; break
            if tp_hit: hit="TP"; end=j; break
        if hit is None: hit="TIME"; end=min(i+48,len(x)-1)
        if direction=="long":
            mfe=(np.max(hi[i+1:end+1])-entry)/p
            mae=(entry-np.min(lo[i+1:end+1]))/p
        else:
            mfe=(entry-np.min(lo[i+1:end+1]))/p
            mae=(np.max(hi[i+1:end+1])-entry)/p
        r={"result":hit,"mfe":mfe,"mae":mae,"bars":end-i}
        rows.append(r)
    return pd.DataFrame(rows)

def summarize(df):
    if df.empty: return {}
    w=(df.result=="TP").sum(); l=(df.result=="SL").sum()
    gross_w=w; gross_l=l
    pf=(gross_w*1.0)/(gross_l*1.0) if gross_l else math.inf
    return {
      "trades":len(df),"win":w/len(df),"pf":pf,
      "exp_r":float((df.result=="TP").mean()-(df.result=="SL").mean()),
      "mfe_med":df.mfe.median(),"mfe_p75":df.mfe.quantile(.75),
      "mae_med":df.mae.median(),"mae_p75":df.mae.quantile(.75),
      "bars_med":df.bars.median(),
    }

def main():
    out=[]
    for structure,names in STRUCTURES.items():
      for pair in PAIRS:
        x=pd.read_parquet(DATA/f"{pair}.parquet").sort_index()
        a=atoms(x); m=pd.Series(True,index=x.index)
        for name in names: m &= a[name].fillna(False)
        n=len(x); a60=int(n*.6); b20=int(n*.2)
        parts={"discovery":x.iloc[:a60],"validation":x.iloc[a60:a60+b20],"oos":x.iloc[a60+b20:]}
        masks={"discovery":m.iloc[:a60],"validation":m.iloc[a60:a60+b20],"oos":m.iloc[a60+b20:]}
        for split,part in parts.items():
          mm=masks[split]
          for tp,sl in TP_SL:
            q=summarize(trades(part,pair,mm,"long",tp,sl))
            if q: out.append({"structure":structure,"pair":pair,"split":split,"tp":tp,"sl":sl,**q})
    df=pd.DataFrame(out)
    df.to_csv(OUT/"stable_jpy_trade_quality.csv",index=False)
    lines=["# Stable JPY H1 trade quality","","Only structures that stayed positive in both OOS halves with adequate half-sample size are examined: USDJPY/EURJPY/GBPJPY, long direction. Entry is next H1 open; non-overlapping 48-H1 window; same-candle TP/SL is conservatively treated as SL.","","|Structure|Pair|Split|TP|SL|Trades|Win|PF|ExpR|MFE med|MFE p75|MAE med|MAE p75|Bars med|","|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for _,r in df.iterrows():
      lines.append(f"|{r.structure}|{r.pair}|{r.split}|{int(r.tp)}|{int(r.sl)}|{int(r.trades)}|{r.win:.3f}|{r.pf:.3f}|{r.exp_r:.3f}|{r.mfe_med:.1f}|{r.mfe_p75:.1f}|{r.mae_med:.1f}|{r.mae_p75:.1f}|{r.bars_med:.1f}|")
    (OUT/"stable_jpy_trade_quality.md").write_text("\n".join(lines)+"\n")

if __name__=="__main__": main()
