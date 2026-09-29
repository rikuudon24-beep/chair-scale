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
    target = x["up_100_48"] if direction == "long" else x["down_100_48"]
    mfe = x["mfe_up_48"] if direction == "long" else x["mfe_down_48"]
    mae = x["mae_long_48"] if direction == "long" else x["mae_short_48"]
    m = mask & target.notna(); n = int(m.sum())
    if n == 0: return None
    k = int(target[m].sum())
    return {"trades":n,"hit_rate":k/n,"lcb95":wilson_lower(k,n),
            "mean_mfe":float(mfe[m].mean()),"median_mfe":float(mfe[m].median()),
            "mean_mae":float(mae[m].mean())}

def main():
    rows = []
    for fp in sorted(DATA.glob("*.parquet")):
        pair = fp.stem; x = pd.read_parquet(fp).sort_index(); disc,_,_ = split(x)
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
            aa=atoms(part,r.direction); mask=pd.Series(True,index=part.index)
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
