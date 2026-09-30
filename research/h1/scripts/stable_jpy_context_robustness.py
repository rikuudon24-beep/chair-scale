#!/usr/bin/env python3
from pathlib import Path
import pandas as pd, numpy as np

ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/"data/market"; OUT=ROOT/"research/h1/results"
PAIRS=["usdjpy","eurjpy","gbpjpy"]
TP,SL,H=40,75,48

def load(pair,tf):
    x=pd.read_csv(DATA/tf/f"{pair}.csv")
    x["timestamp"]=pd.to_datetime(x["timestamp"],unit="ms",utc=True)
    x=x.drop_duplicates("timestamp").sort_values("timestamp").set_index("timestamp")
    for c in ["open","high","low","close"]: x[c]=pd.to_numeric(x[c],errors="coerce")
    return x.dropna(subset=["open","high","low","close"])

def context(pair,tf):
    x=load(pair,tf).copy()
    x["ema20"]=x.close.ewm(span=20,adjust=False).mean()
    x["ema50"]=x.close.ewm(span=50,adjust=False).mean()
    x["ema200"]=x.close.ewm(span=200,adjust=False).mean()
    x["ema20_slope6"]=x.ema20.pct_change(6)
    y=pd.DataFrame(index=x.index)
    y[f"{tf}_bull_candle"]=x.close>x.open
    y[f"{tf}_close_ema20"]=x.close>x.ema20
    y[f"{tf}_ema20_50"]=x.ema20>x.ema50
    y[f"{tf}_ema20_200"]=x.ema20>x.ema200
    y[f"{tf}_slope_pos"]=x.ema20_slope6>0
    y[f"{tf}_bull_trend"]=(x.close>x.ema20)&(x.ema20>x.ema50)&(x.ema50>x.ema200)
    return y.shift(1)

def split(x):
    n=len(x); a=int(n*.6); b=int(n*.2)
    return x.iloc[:a],x.iloc[a:a+b],x.iloc[a+b:]

def ids(x,mask):
    raw=np.flatnonzero(mask.to_numpy()); out=[]; nxt=-1
    for i in raw:
        if i<nxt or i+H>=len(x): continue
        out.append(i); nxt=i+H+1
    return out

def result(x,i):
    e=float(x.open.iloc[i+1]); p=.01
    for j in range(i+1,min(i+H+1,len(x))):
        ht=x.high.iloc[j]>=e+TP*p; hs=x.low.iloc[j]<=e-SL*p
        if ht and hs:return -1
        if hs:return -1
        if ht:return 1
    return 0

def metric(vals):
    v=np.asarray(vals); r=v[v!=0]; n=len(r)
    w=(r>0).sum(); gp=r[r>0].sum(); gl=-r[r<0].sum()
    return n,w/n if n else np.nan,gp/gl if gl else np.inf,float(r.sum()/n) if n else np.nan

def main():
    rows=[]
    variants=[
      ("candle","h4_bull_candle","d1_bull_candle"),
      ("close_ema20","h4_close_ema20","d1_close_ema20"),
      ("ema20_gt50","h4_ema20_50","d1_ema20_50"),
      ("ema20_gt200","h4_ema20_200","d1_ema20_200"),
      ("slope_pos","h4_slope_pos","d1_slope_pos"),
      ("bull_trend","h4_bull_trend","d1_bull_trend"),
      ("close_ema20_plus_ema20gt50","h4_close_ema20","d1_close_ema20"),
    ]
    for pair in PAIRS:
        h1=load(pair,"h1")
        base=pd.DataFrame(index=h1.index)
        base["trend_down"]=False
        e20=h1.close.ewm(span=20,adjust=False).mean(); e50=h1.close.ewm(span=50,adjust=False).mean(); e200=h1.close.ewm(span=200,adjust=False).mean()
        base["trend_down"]=(e20<e50)&(e50<e200)
        d=h1.close.diff(); up=d.clip(lower=0); dn=-d.clip(upper=0)
        rs=up.ewm(alpha=1/14,adjust=False).mean()/dn.ewm(alpha=1/14,adjust=False).mean().replace(0,np.nan)
        base["rsi"]=100-100/(1+rs)
        tr=pd.concat([h1.high-h1.low,(h1.high-h1.close.shift()).abs(),(h1.low-h1.close.shift()).abs()],axis=1).max(axis=1)
        atr=tr.ewm(alpha=1/14,adjust=False).mean()
        pdm=h1.high.diff(); mdm=-h1.low.diff()
        pdm=pdm.where((pdm>mdm)&(pdm>0),0); mdm=mdm.where((mdm>pdm)&(mdm>0),0)
        pdi=100*pdm.ewm(alpha=1/14,adjust=False).mean()/atr; mdi=100*mdm.ewm(alpha=1/14,adjust=False).mean()/atr
        dx=100*(pdi-mdi).abs()/(pdi+mdi).replace(0,np.nan)
        base["adx"]=dx.ewm(alpha=1/14,adjust=False).mean()
        base["rsi_up6"]=base.rsi-base.rsi.shift(6)>3
        for tf in ["h4","d1"]:
            base=base.join(context(pair,tf),how="left")
        for name,h4c,d1c in variants:
            mask=base.trend_down&base[h4c]&base[d1c]&base.adx.ge(20)&base.rsi_up6
            if name=="close_ema20_plus_ema20gt50":
                mask=base.trend_down&base.h4_close_ema20&base.h4_ema20_50&base.d1_close_ema20&base.d1_ema20_50&base.adx.ge(20)&base.rsi_up6
            for sn,x in zip(["discovery","validation","oos"],split(pd.concat([h1,base],axis=1))):
                m=mask.loc[x.index]
                vals=[result(x,i) for i in ids(x,m)]
                n,w,pf,ex=metric(vals)
                rows.append({"pair":pair,"variant":name,"split":sn,"n":n,"win":w,"pf":pf,"expectancy_r":ex})
    df=pd.DataFrame(rows); df.to_csv(OUT/"stable_jpy_context_robustness.csv",index=False)
    lines=["# Stable JPY context robustness","",f"Frozen H1 setup: trend_down + ADX>=20 + RSI6 change >3, TP{TP}/SL{SL}/H{H}. Only H4/D1 context definition is varied.",""]
    for v,g in df.groupby("variant"):
        lines.append(f"## {v}")
        lines.append("|Pair|Split|N|Win|PF|ExpR|"); lines.append("|---|---|---:|---:|---:|---:|")
        for _,r in g.iterrows(): lines.append(f"|{r.pair}|{r.split}|{int(r.n)}|{r.win:.3f}|{r.pf:.3f}|{r.expectancy_r:.3f}|")
        lines.append("")
    (OUT/"stable_jpy_context_robustness.md").write_text("\n".join(lines)+"\n")
    print("[OK] context robustness complete")

if __name__=="__main__": main()
