#!/usr/bin/env python3
"""Leakage-safe study of H1 state changes immediately before +100 pip moves."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/"research/h1/results/datasets"
OUT=ROOT/"research/h1/results"
FEATURES=["rsi14","adx14","macd_hist","roc12","atr14","bb_width","ema20_slope","ema50_slope","body_range","dist_ema20_atr","dist_ema200_atr","range20"]
BOOLS=["trend_up","trend_down","break20_up","break20_down","pullback_up","pullback_down"]

def split(df):
    n=len(df); a=int(n*.60); b=int(n*.20)
    return df.iloc[:a],df.iloc[a:a+b],df.iloc[a+b:]

def pip_size(pair): return .01 if "jpy" in pair else .0001

def sample_events(x,pair,direction):
    ps=pip_size(pair); chosen=[]; next_allowed=-1
    op=x.open.to_numpy(); hi=x.high.to_numpy(); lo=x.low.to_numpy()
    for i in range(0,len(x)-48):
        if i < next_allowed: continue
        entry=op[i+1]
        hit=(np.max(hi[i+1:i+49])-entry >= 100*ps) if direction=="long" else (entry-np.min(lo[i+1:i+49]) >= 100*ps)
        if hit: chosen.append(i); next_allowed=i+49
    return chosen

def feature_stats(part,pair,direction):
    rows=[]
    for i in sample_events(part,pair,direction):
        row={"pair":pair,"direction":direction,"idx":i}
        for f in FEATURES:
            if f not in part: continue
            v=part[f].iloc[i]; row[f]=v
            for lag in [1,3,6,12,24]:
                if i-lag>=0: row[f"{f}_chg_{lag}"]=v-part[f].iloc[i-lag]
        for f in BOOLS:
            if f in part: row[f]=bool(part[f].iloc[i])
        rows.append(row)
    return pd.DataFrame(rows)

def score_events(ev,base):
    rows=[]
    for col in ev.columns:
        if col in {"pair","direction","idx"}: continue
        s=ev[col].dropna(); b=base[col].dropna() if col in base else pd.Series(dtype=float)
        if s.empty or b.empty: continue
        if pd.api.types.is_bool_dtype(s):
            rows.append({"feature":col,"event_rate":float(s.mean()),"baseline_rate":float(b.mean()),"lift":float(s.mean()-b.mean()),"events":len(s)})
        else:
            rows.append({"feature":col,"event_median":float(s.median()),"baseline_median":float(b.median()),"median_delta":float(s.median()-b.median()),"events":len(s)})
    return pd.DataFrame(rows)

def main():
    scores=[]
    for fp in sorted(DATA.glob("*.parquet")):
        pair=fp.stem; x=pd.read_parquet(fp).sort_index(); disc,_,_=split(x)
        eligible=disc.dropna(subset=[f for f in FEATURES if f in disc]).copy(); base=eligible.reset_index(drop=True)
        for direction in ["long","short"]:
            ev=feature_stats(eligible,pair,direction)
            if not ev.empty:
                sc=score_events(ev,base); sc["pair"]=pair; sc["direction"]=direction; scores.append(sc)
    d=pd.concat(scores,ignore_index=True) if scores else pd.DataFrame()
    if d.empty:
        (OUT/"precursor_study.md").write_text("# H1 +100 Pip Precursor Study\n\nNo usable events.\n"); return
    d=d[d.events>=30].copy()
    bools=d[d.lift.notna()].sort_values(["lift","events"],ascending=False).head(40)
    nums=d[d.median_delta.notna()].copy(); nums["abs_delta"]=nums.median_delta.abs(); nums=nums.sort_values(["abs_delta","events"],ascending=False).head(40)
    d.to_csv(OUT/"precursor_discovery.csv",index=False)
    lines=["# H1 +100 Pip Precursor Study","","Protocol: signal at H1 close; entry at next H1 open; +100 pips measured over the following 48 H1 bars; events are non-overlapping.","Discovery only. This study identifies candidate state changes; it does not freeze a notification rule.","","## Repeated boolean states before +100 pip moves","","|Pair|Dir|Feature|Event rate|Baseline rate|Lift|Events|","|---|---|---|---:|---:|---:|---:|"]
    if bools.empty: lines.append("|—|—|No repeated boolean states.|—|—|—|—|")
    else:
        for _,r in bools.iterrows(): lines.append(f"|{r.pair}|{r.direction}|{r.feature}|{r.event_rate:.3f}|{r.baseline_rate:.3f}|{r.lift:.3f}|{int(r.events)}|")
    lines += ["","## Largest numeric state changes (median vs baseline)","","|Pair|Dir|Feature|Event median|Baseline median|Median delta|Events|","|---|---|---|---:|---:|---:|---:|"]
    for _,r in nums.iterrows(): lines.append(f"|{r.pair}|{r.direction}|{r.feature}|{r.event_median:.4g}|{r.baseline_median:.4g}|{r.median_delta:.4g}|{int(r.events)}|")
    (OUT/"precursor_study.md").write_text("\n".join(lines)+"\n")

if __name__=="__main__": main()
