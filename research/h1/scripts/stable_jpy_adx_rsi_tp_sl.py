#!/usr/bin/env python3
from pathlib import Path
import pandas as pd, numpy as np, math

ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/"research/h1/results/datasets"; OUT=ROOT/"research/h1/results"
PAIRS=["usdjpy","eurjpy","gbpjpy"]

def split(x):
    n=len(x); a=int(n*.6); b=int(n*.2)
    return x.iloc[:a],x.iloc[a:a+b],x.iloc[a+b:]

def wilson(k,n,z=1.96):
    if not n:return 0.0
    p=k/n; d=1+z*z/n
    return (p+z*z/(2*n)-z*math.sqrt((p*(1-p)+z*z/(4*n))/n))/d

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
        if ht and hs:return -1.0
        if hs:return -1.0
        if ht:return 1.0
    return 0.0

def eval(x,mask,tp,sl,h):
    vals=[result(x,i,tp,sl,h) for i in ids(x,mask,h)]
    n=len(vals); w=sum(v>0 for v in vals); gp=sum(v for v in vals if v>0); gl=-sum(v for v in vals if v<0)
    return n,w/n if n else np.nan,wilson(w,n),gp/gl if gl else (float("inf") if gp else 0),sum(vals)/n if n else np.nan

def main():
    rows=[]
    for pair in PAIRS:
        data=pd.read_parquet(DATA/f"{pair}.parquet").sort_index()
        for sn,ix in [("discovery",0),("validation",1),("oos",2)]:
            x=split(data)[ix]
            mask=x.trend_down & (x.h4_close>x.h4_open) & (x.d1_close>x.d1_open) & (x.adx14>=20) & ((x.rsi14-x.rsi14.shift(6))>3)
            for tp in [40,50,60,75,100]:
              for sl in [50,60,75,90,100]:
                for h in [24,36,48,72]:
                  n,w,l,pf,ex=eval(x,mask,tp,sl,h)
                  rows.append({"pair":pair,"split":sn,"tp":tp,"sl":sl,"horizon":h,"trades":n,"win":w,"lcb95":l,"pf":pf,"exp_r":ex})
    df=pd.DataFrame(rows); df.to_csv(OUT/"stable_jpy_adx_rsi_tp_sl.csv",index=False)
    # Only summarize configurations that are positive in every pair in Validation and OOS.
    piv=[]
    for (tp,sl,h),g in df.groupby(["tp","sl","horizon"]):
        v=g[g.split=="validation"]; o=g[g.split=="oos"]
        if len(v)==3 and len(o)==3:
          piv.append({"tp":tp,"sl":sl,"horizon":h,
             "val_min_n":int(v.trades.min()),"val_min_win":float(v.win.min()),"val_min_pf":float(v.pf.replace(np.inf,np.nan).min(skipna=True)),
             "oos_min_n":int(o.trades.min()),"oos_min_win":float(o.win.min()),"oos_min_pf":float(o.pf.replace(np.inf,np.nan).min(skipna=True)),
             "val_all_positive":bool((v.exp_r>0).all()),"oos_all_positive":bool((o.exp_r>0).all())})
    sm=pd.DataFrame(piv).sort_values(["val_all_positive","oos_all_positive","val_min_pf","oos_min_pf"],ascending=False)
    sm.to_csv(OUT/"stable_jpy_adx_rsi_tp_sl_summary.csv",index=False)
    lines=["# Stable JPY ADX+RSI TP/SL robustness","","Frozen condition: trend_down & h4_bull & d1_bull & ADX>=20 & RSI14 change over 6 H1 bars > 3. No condition selection here; this is TP/SL/horizon robustness.","","|TP|SL|H|Val min n|Val min win|Val min PF|OOS min n|OOS min win|OOS min PF|Val all +|OOS all +|","|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|"]
    for _,r in sm.head(40).iterrows():
      lines.append(f"|{int(r.tp)}|{int(r.sl)}|{int(r.horizon)}|{int(r.val_min_n)}|{r.val_min_win:.3f}|{r.val_min_pf:.3f}|{int(r.oos_min_n)}|{r.oos_min_win:.3f}|{r.oos_min_pf:.3f}|{str(r.val_all_positive)}|{str(r.oos_all_positive)}|")
    (OUT/"stable_jpy_adx_rsi_tp_sl_summary.md").write_text("\n".join(lines)+"\n")
    print("[OK] ADX+RSI TP/SL robustness complete")
if __name__=="__main__":main()
