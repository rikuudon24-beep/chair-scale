#!/usr/bin/env python3
"""Leakage-safe study of H1 state changes immediately before +100 pip moves."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/"research/h1/results/datasets"
OUT=ROOT/"research/h1/results"
PAIRS=sorted(DATA.glob("*.parquet"))

FEATURES=[
    "rsi14","adx14","macd_hist","roc12","atr14","bb_width",
    "ema20_slope","ema50_slope","body_range","dist_ema20_atr","dist_ema200_atr",
    "range20","h4_close","d1_close","w1_close"
]
BOOLS=["trend_up","trend_down","break20_up","break20_down","pullback_up","pullback_down"]

def split(df):
    n=len(df); a=int(n*.60); b=int(n*.20)
    return df.iloc[:a],df.iloc[a:a+b],df.iloc[a+b:]

def pip_size(pair): return .01 if "jpy" in pair else .0001

def event_mask(x,direction):
    if direction=="long":
        return x["mfe_up_48"]>=100
    return x["mfe_down_48"]>=100

def sample_events(x,direction):
    # Signal is known at close i; outcome starts at next H1 open.
    # Non-overlap prevents one move from creating many apparent successes.
    m=event_mask(x,direction).fillna(False).to_numpy()
    idx=np.flatnonzero(m)
    chosen=[]; next_allowed=-1
    for i in idx:
        if i < next_allowed or i+48 >= len(x): continue
        chosen.append(i); next_allowed=i+49
    return chosen

def feature_stats(part,pair,direction):
    rows=[]
    ps=pip_size(pair)
    for i in sample_events(part,direction):
        row={"pair":pair,"direction":direction,"idx":i}
        for f in FEATURES:
            if f not in part: continue
            v=part[f].iloc[i]
            row[f]=v
            for lag in [1,3,6,12,24]:
                if i-lag>=0:
                    row[f"{f}_chg_{lag}"] = (v-part[f].iloc[i-lag])/ps if f in ["atr14","range20"] else v-part[f].iloc[i-lag]
        for f in BOOLS:
            row[f]=bool(part[f].iloc[i]) if f in part else False
        rows.append(row)
    return pd.DataFrame(rows)

def score_events(ev,allrows):
    if ev.empty: return pd.DataFrame()
    # Baseline state is sampled from all eligible bars, not only event bars.
    rows=[]
    for col in ev.columns:
        if col in {"pair","direction","idx"}: continue
        s=ev[col].dropna()
        if s.empty: continue
        base=allrows[col].dropna() if col in allrows else pd.Series(dtype=float)
        if base.empty: continue
        if pd.api.types.is_bool_dtype(s):
            rate=float(s.mean()); br=float(base.mean())
            lift=rate-br
            rows.append({"feature":col,"event_rate":rate,"baseline_rate":br,"lift":lift,"events":len(s)})
        else:
            med=float(s.median()); bmed=float(base.median())
            rows.append({"feature":col,"event_median":med,"baseline_median":bmed,
                         "median_delta":med-bmed,"events":len(s)})
    return pd.DataFrame(rows)

def process_split(part,pair,direction):
    # eligible bars have complete predictors and enough future outcome.
    needed=[f for f in FEATURES+BOOLS if f in part]
    eligible=part.dropna(subset=[f for f in FEATURES if f in part]).copy()
    ev=feature_stats(eligible,direction)
    allrows=eligible.reset_index(drop=True)
    return ev,score_events(ev,allrows)

def main():
    discovery_scores=[]
    follow=[]
    for fp in PAIRS:
        pair=fp.stem; x=pd.read_parquet(fp).sort_index()
        disc,val,oos=split(x)
        for direction in ["long","short"]:
            ev,sc=process_split(disc,pair,direction)
            if sc.empty: continue
            sc["pair"]=pair; sc["direction"]=direction
            discovery_scores.append(sc)
    d=pd.concat(discovery_scores,ignore_index=True) if discovery_scores else pd.DataFrame()
    if d.empty:
        (OUT/"precursor_study.md").write_text("# H1 +100 Pip Precursor Study\n\nNo usable events.\n"); return
    # Rank only within discovery. Focus on repeated state changes with at least 30 events.
    d=d[d.events>=30].copy()
    if "lift" in d:
        bools=d[d.lift.notna()].sort_values(["lift","events"],ascending=False).head(40)
    else: bools=pd.DataFrame()
    nums=d[d.median_delta.notna()].copy()
    nums["abs_delta"]=nums.median_delta.abs()
    nums=nums.sort_values(["abs_delta","events"],ascending=False).head(40)
    d.to_csv(OUT/"precursor_discovery.csv",index=False)
    lines=["# H1 +100 Pip Precursor Study","","Protocol: signal at H1 close; +100 pips measured only in the next 48 H1 bars; events are non-overlapping.",
           "Discovery is used for pattern discovery only. No notification rule is frozen from this study.","",
           "## Repeated boolean states before +100 pip moves","","|Pair|Dir|Feature|Event rate|Baseline rate|Lift|Events|","|---|---|---|---:|---:|---:|---:|"]
    if bools.empty: lines.append("|—|—|No repeated boolean states.|—|—|—|—|")
    else:
        for _,r in bools.iterrows():
            lines.append(f"|{r.pair}|{r.direction}|{r.feature}|{r.event_rate:.3f}|{r.baseline_rate:.3f}|{r.lift:.3f}|{int(r.events)}|")
    lines += ["","## Largest numeric state changes (median vs baseline)","","|Pair|Dir|Feature|Event median|Baseline median|Median delta|Events|","|---|---|---|---:|---:|---:|---:|"]
    for _,r in nums.head(40).iterrows():
        lines.append(f"|{r.pair}|{r.direction}|{r.feature}|{r.event_median:.4g}|{r.baseline_median:.4g}|{r.median_delta:.4g}|{int(r.events)}|")
    (OUT/"precursor_study.md").write_text("\n".join(lines)+"\n")
    print("precursor study complete")

if __name__=="__main__": main()
