#!/usr/bin/env python3
"""Leakage-safe systematic H1 condition mining for large-move precursors."""
import itertools, json, math
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "research/h1/results/datasets"
OUT = ROOT / "research/h1/results"
OUT.mkdir(parents=True, exist_ok=True)

def split(df):
    n = len(df); a = int(n * 0.60); b = int(n * 0.20)
    return df.iloc[:a], df.iloc[a:a+b], df.iloc[a+b:]

def wilson_lower(k, n, z=1.96):
    if n <= 0: return 0.0
    p = k / n; den = 1 + z*z/n
    centre = p + z*z/(2*n)
    adj = z * math.sqrt((p*(1-p) + z*z/(4*n))/n)
    return (centre - adj) / den

def atoms(x, direction):
    atr_med = x.atr14.rolling(200, min_periods=100).median()
    bw_med = x.bb_width.rolling(200, min_periods=100).median()
    a = {
        "trend_up": x.trend_up, "trend_down": x.trend_down,
        "pullback_up": x.pullback_up, "pullback_down": x.pullback_down,
        "adx20+": x.adx14 >= 20, "adx25+": x.adx14 >= 25,
        "rsi30_45": x.rsi14.between(30,45), "rsi45_55": x.rsi14.between(45,55),
        "rsi55_70": x.rsi14.between(55,70), "rsi_extreme_low": x.rsi14 < 30,
        "rsi_extreme_high": x.rsi14 > 70, "macd_pos": x.macd_hist > 0,
        "macd_neg": x.macd_hist < 0, "roc_pos": x.roc12 > 0, "roc_neg": x.roc12 < 0,
        "atr_above_med": x.atr14 > atr_med, "bb_below_med": x.bb_width < bw_med,
        "body_strong": x.body_range >= 0.60, "break20_up": x.break20_up,
        "break20_down": x.break20_down, "dist_ema20_near": x.dist_ema20_atr.between(-0.50,0.50),
        "dist_ema20_far": x.dist_ema20_atr.abs() >= 1.0,
        "h4_bull": x.h4_close > x.h4_open, "h4_bear": x.h4_close < x.h4_open,
        "d1_bull": x.d1_close > x.d1_open, "d1_bear": x.d1_close < x.d1_open,
        "w1_bull": x.w1_close > x.w1_open, "w1_bear": x.w1_close < x.w1_open
    }
    directional = {"long":{"h4_bear","d1_bear","w1_bear","break20_down","trend_down","pullback_down",
                           "rsi_extreme_high","macd_neg","roc_neg"},
                   "short":{"h4_bull","d1_bull","w1_bull","break20_up","trend_up","pullback_up",
                            "rsi_extreme_low","macd_pos","roc_pos"}}
    return {k:v.fillna(False) for k,v in a.items() if k not in directional[direction]}

def evaluate(x, mask, direction):
    ps = 0.01 if "jpy" in str(x.pair.iloc[0]) else 0.0001
    idx = np.flatnonzero(mask.fillna(False).to_numpy())
    selected = []
    next_allowed = -1
    for i in idx:
        if i < next_allowed or i + 48 >= len(x):
            continue
        selected.append(i)
        next_allowed = i + 49
    if not selected:
        return None
    op=x.open.to_numpy(); hi=x.high.to_numpy(); lo=x.low.to_numpy()
    mfe_vals=[]; mae_vals=[]; hits=0
    for i in selected:
        entry=op[i+1]; fh=np.max(hi[i+1:i+49]); fl=np.min(lo[i+1:i+49])
        if direction=="long":
            mfe_vals.append((fh-entry)/ps); mae_vals.append((fl-entry)/ps); hits += int(fh-entry >= 100*ps)
        else:
            mfe_vals.append((entry-fl)/ps); mae_vals.append((entry-fh)/ps); hits += int(entry-fl >= 100*ps)
    n=len(selected); hit=hits/n
    return {"trades":n,"hit_rate":hit,"lcb95":wilson_lower(hits,n),
            "mean_mfe":float(np.mean(mfe_vals)),"median_mfe":float(np.median(mfe_vals)),
            "mean_mae":float(np.mean(mae_vals))}

def main():
    rows = []
    for fp in sorted(DATA.glob("*.parquet")):
        pair = fp.stem; x = pd.read_parquet(fp).sort_index(); x["pair"]=pair; disc,_,_ = split(x)
        for direction in ["long","short"]:
            aa = atoms(disc, direction)
            eligible = [k for k,v in aa.items() if int(v.sum()) >= 50]
            for size in (1,2,3):
                for names in itertools.combinations(eligible, size):
                    mask = pd.Series(True, index=disc.index)
                    for name in names: mask &= aa[name]
                    ev = evaluate(disc, mask, direction)
                    if ev and ev["trades"] >= 50:
                        rows.append({"pair":pair,"direction":direction,"conditions":" & ".join(names),
                                      "n_conditions":size,**ev})
    res = pd.DataFrame(rows)
    if res.empty:
        (OUT/"mined_conditions.md").write_text("# Systematic H1 Condition Mining\n\nNo combinations.\n"); return
    res = res[(res.hit_rate >= 0.55) & (res.lcb95 >= 0.45)]
    res = res.sort_values(["lcb95","hit_rate","trades"],ascending=[False,False,False]).head(80)
    follow=[]
    for _,r in res.iterrows():
        x=pd.read_parquet(DATA/f"{r.pair}.parquet").sort_index(); _,val,oos=split(x)
        for sn,part in [("validation",val),("oos",oos)]:
            part["pair"]=r.pair; aa=atoms(part,r.direction); mask=pd.Series(True,index=part.index)
            for name in r.conditions.split(" & "): mask &= aa[name]
            ev=evaluate(part,mask,r.direction)
            if ev is None: ev={"trades":0,"hit_rate":np.nan,"lcb95":np.nan,"mean_mfe":np.nan,"median_mfe":np.nan,"mean_mae":np.nan}
            follow.append({**r.to_dict(),"split":sn,**ev})
    f=pd.DataFrame(follow)
    res.to_csv(OUT/"mined_conditions_discovery.csv",index=False); f.to_csv(OUT/"mined_conditions_followup.csv",index=False)
    lines=["# Systematic H1 Condition Mining","","Target: +100 pips within 48 H1 bars.",
           "Discovery only was used to nominate conditions; validation/OOS were not used for selection.",
           "Gate: discovery n >= 50, hit rate >= 55%, Wilson 95% lower bound >= 45%.","",
           "## Validation/OOS candidates","","|Pair|Dir|Conditions|Split|Trades|Hit rate|LCB95|Mean MFE|Median MFE|Mean MAE|",
           "|---|---|---|---|---:|---:|---:|---:|---:|---:|"]
    if f.empty: lines.append("|—|—|No candidates passed the discovery gate.|—|—|—|—|—|—|—|")
    else:
        for _,r in f.iterrows():
            lines.append(f"|{r.pair}|{r.direction}|{r.conditions}|{r.split}|{int(r.trades)}|{r.hit_rate:.3f}|{r.lcb95:.3f}|{r.mean_mfe:.1f}|{r.median_mfe:.1f}|{r.mean_mae:.1f}|")
    (OUT/"mined_conditions.md").write_text("\n".join(lines)+"\n")

if __name__=="__main__": main()
