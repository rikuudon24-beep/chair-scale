#!/usr/bin/env python3
"""Build leakage-safe H1 research datasets and forward labels."""
import json,math
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[3]
CFG=json.loads((ROOT/"research/h1/config.json").read_text())
OUT=ROOT/"research/h1/results/datasets"; OUT.mkdir(parents=True,exist_ok=True)

def pip_size(pair): return 0.01 if "jpy" in pair else 0.0001

def load(pair,tf):
    fp=ROOT/"data/market"/tf/f"{pair}.csv"
    if not fp.exists(): return None
    df=pd.read_csv(fp)
    df["timestamp"]=pd.to_datetime(df["timestamp"],unit="ms",utc=True)
    df=df.drop_duplicates("timestamp").sort_values("timestamp").set_index("timestamp")
    for c in ["open","high","low","close","volume"]: df[c]=pd.to_numeric(df[c],errors="coerce")
    return df.dropna(subset=["open","high","low","close"])

def add_tf_context(df,pair,tf):
    x=load(pair,tf)
    if x is None or x.empty: return df
    cols=["open","high","low","close"]
    y=x[cols].rename(columns={c:f"{tf}_{c}" for c in cols})
    # Merge only completed higher-timeframe candles: shift by one HTF bar.
    y=y.shift(1)
    return pd.merge_asof(df.sort_index(),y.sort_index(),left_index=True,right_index=True,direction="backward")

def features(df,pair):
    x=df.copy()
    c=x.close; h=x.high; l=x.low; o=x.open
    for n in [20,50,200]:
        x[f"ema{n}"]=c.ewm(span=n,adjust=False).mean()
        x[f"sma{n}"]=c.rolling(n).mean()
    delta=c.diff(); up=delta.clip(lower=0); down=-delta.clip(upper=0)
    rs=up.ewm(alpha=1/14,adjust=False).mean()/down.ewm(alpha=1/14,adjust=False).mean().replace(0,np.nan)
    x["rsi14"]=100-(100/(1+rs))
    tr=pd.concat([(h-l),(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    x["atr14"]=tr.ewm(alpha=1/14,adjust=False).mean()
    x["atr_pct"]=x["atr14"]/c
    x["roc12"]=c.pct_change(12)
    ema12=c.ewm(span=12,adjust=False).mean(); ema26=c.ewm(span=26,adjust=False).mean()
    x["macd"]=ema12-ema26; x["macd_signal"]=x["macd"].ewm(span=9,adjust=False).mean(); x["macd_hist"]=x["macd"]-x["macd_signal"]
    mid=c.rolling(20).mean(); sd=c.rolling(20).std()
    x["bb_mid"]=mid; x["bb_upper"]=mid+2*sd; x["bb_lower"]=mid-2*sd
    x["bb_width"]=(x["bb_upper"]-x["bb_lower"])/mid
    x["bb_pct"]=(c-x["bb_lower"])/(x["bb_upper"]-x["bb_lower"]).replace(0,np.nan)
    x["ema20_slope"]=x["ema20"].pct_change(6)
    x["ema50_slope"]=x["ema50"].pct_change(12)
    # Wilder-style ADX(14), computed only from current/past bars.
    plus_dm=h.diff(); minus_dm=-l.diff(); plus_dm=plus_dm.where((plus_dm>minus_dm)&(plus_dm>0),0.0); minus_dm=minus_dm.where((minus_dm>plus_dm)&(minus_dm>0),0.0)
    atr=x["atr14"].replace(0,np.nan)
    plus_di=100*plus_dm.ewm(alpha=1/14,adjust=False).mean()/atr; minus_di=100*minus_dm.ewm(alpha=1/14,adjust=False).mean()/atr
    dx=100*(plus_di-minus_di).abs()/(plus_di+minus_di).replace(0,np.nan); x["adx14"]=dx.ewm(alpha=1/14,adjust=False).mean()
    x["range20"]=h.rolling(20).max()-l.rolling(20).min()
    x["body"]=c-o; x["body_pct"]=x["body"]/c; x["range"]=h-l
    x["body_range"]=x["body"].abs()/x["range"].replace(0,np.nan)
    x["upper_wick"]=h-np.maximum(o,c); x["lower_wick"]=np.minimum(o,c)-l
    x["prior20_high"]=h.shift(1).rolling(20).max(); x["prior20_low"]=l.shift(1).rolling(20).min()
    x["dist_ema20_atr"]=(c-x["ema20"])/x["atr14"]
    x["dist_ema200_atr"]=(c-x["ema200"])/x["atr14"]
    # H1-only event flags; all use information available at the close of this bar.
    x["trend_up"]=(x.ema20>x.ema50)&(x.ema50>x.ema200)
    x["trend_down"]=(x.ema20<x.ema50)&(x.ema50<x.ema200)
    x["break20_up"]=c>x["prior20_high"]; x["break20_down"]=c<x["prior20_low"]
    x["pullback_up"]=(x.dist_ema20_atr.between(-0.75,0.25))&x.trend_up
    x["pullback_down"]=(x.dist_ema20_atr.between(-0.25,0.75))&x.trend_down
    ps=pip_size(pair)
    for target in CFG["targets_pips"]:
        n=target*ps
        x[f"mfe_up_{target}"]=(h.shift(-1).rolling(24,min_periods=1).max().shift(-23)-c)/ps
        x[f"mfe_down_{target}"]=(c-l.shift(-1).rolling(24,min_periods=1).min().shift(-23))/ps
    # Clean impossible/unstable rows only after all features are computed.
    return x.replace([np.inf,-np.inf],np.nan)

def forward_labels(x,pair):
    ps=pip_size(pair)
    horizons=[24,48,72,120]
    for H in horizons:
        fut_hi=x.high.shift(-1).rolling(H,min_periods=H).max()
        fut_lo=x.low.shift(-1).rolling(H,min_periods=H).min()
        x[f"mfe_up_{H}"]=(fut_hi-x.close)/ps
        x[f"mfe_down_{H}"]=(x.close-fut_lo)/ps
        x[f"mae_long_{H}"]=(fut_lo-x.close)/ps
        x[f"mae_short_{H}"]=(x.close-fut_hi)/ps
        for t in CFG["targets_pips"]:
            x[f"up_{t}_{H}"]=(x[f"mfe_up_{H}"]>=t).astype("Int8")
            x[f"down_{t}_{H}"]=(x[f"mfe_down_{H}"]>=t).astype("Int8")
    return x

def main():
    manifest=[]
    for pair in CFG["symbols"]:
        df=load(pair,"h1")
        if df is None: continue
        for tf in ["h4","d1"]:
            df=add_tf_context(df,pair,tf)
        # Weekly context is derived from D1 so no separate W1 source is required.
        d1=load(pair,"d1")
        if d1 is not None:
            w=d1[["open","high","low","close"]].resample("W-SUN",label="right",closed="right").agg({"open":"first","high":"max","low":"min","close":"last"}).shift(1)
            w=w.rename(columns={c:f"w1_{c}" for c in w.columns})
            df=pd.merge_asof(df.sort_index(),w.sort_index(),left_index=True,right_index=True,direction="backward")
        df=forward_labels(features(df,pair),pair)
        # Require complete feature/label horizon; no current/future row is used as a feature.
        df["pair"]=pair
        df=df.dropna(subset=["ema200","rsi14","atr14","h4_close","d1_close"])
        fp=OUT/f"{pair}.parquet"; df.to_parquet(fp,index=True)
        manifest.append({"pair":pair,"rows":int(len(df)),"start":str(df.index.min()),"end":str(df.index.max()),"file":str(fp.relative_to(ROOT))})
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2))
    print(json.dumps(manifest,indent=2))
if __name__=="__main__": main()
