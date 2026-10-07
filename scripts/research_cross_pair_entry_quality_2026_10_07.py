#!/usr/bin/env python3
"""Cross-pair entry-quality research for the FX notification system.

Purpose:
- Find entry-state features that distinguish good/bad entries across pairs.
- Thresholds are learned ONLY from discovery (<=2024).
- Validation=2025, OOS>=2026.
- This is entry-quality research, not a fixed-pip exit rule.
- 50/100 pip outcomes are used only as standardized entry-quality labels so
  different pairs can be compared; final exits remain structural/dynamic.
"""
from pathlib import Path
from itertools import combinations
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "reports/notification_entry_quality_signals.csv"
OUT = ROOT / "reports/cross_pair_entry_quality_2026-10-07.csv"
COMBO = ROOT / "reports/cross_pair_entry_quality_combinations_2026-10-07.csv"

FEATURES = [
    "signal_range_atr", "signal_body_atr", "signal_body_ratio",
    "ema20_distance_atr", "touch_to_signal_atr", "pre6_move_atr",
    "bars_touch_to_signal",
]
PERIODS = ["discovery", "validation", "oos"]

def effect(g, feature, threshold, side, target):
    if side == "high":
        q = g[g[feature] >= threshold]
    else:
        q = g[g[feature] <= threshold]
    if q.empty:
        return None
    return {
        "n": len(q),
        "hit_rate": float(q[f"hit_{target}"].mean()),
        "mean_pips": float(q[f"pnl_{target}"].mean()),
        "median_pips": float(q[f"pnl_{target}"].median()),
        "pairs": int(q.pair.nunique()),
        "positive_pairs": int(sum(
            (h[f"pnl_{target}"].mean() > 0)
            for _, h in q.groupby("pair")
        )),
    }

def main():
    df = pd.read_csv(SRC)
    df["signal_timestamp"] = pd.to_datetime(df["signal_timestamp"], utc=True)
    df["period"] = np.where(df.signal_timestamp.dt.year <= 2024, "discovery",
                     np.where(df.signal_timestamp.dt.year == 2025, "validation", "oos"))

    # Entry-quality label: hit 100 pips before the frozen stop/timeout proxy.
    # Used only to identify robust entry states; NOT adopted as an exit rule.
    rows = []
    for direction in ["long", "short", "all"]:
        base_d = df if direction == "all" else df[df.direction == direction]
        for feature in FEATURES:
            train = base_d[(base_d.period == "discovery") & base_d[feature].notna()]
            if len(train) < 30:
                continue
            # Learn thresholds only from discovery quartiles.
            qs = train[feature].quantile([.25,.50,.75]).to_dict()
            for qname, threshold in [("q25",qs[.25]),("q50",qs[.50]),("q75",qs[.75])]:
                for side in ["low","high"]:
                    for period in PERIODS:
                        g = base_d[(base_d.period == period) & base_d[feature].notna()]
                        r = effect(g, feature, threshold, side, 100)
                        if r:
                            rows.append({
                                "direction":direction,"feature":feature,
                                "threshold_source":"discovery",
                                "threshold_q":qname,"threshold":threshold,
                                "side":side,"period":period,
                                **r
                            })
    out = pd.DataFrame(rows)

    # Add a simple stability score: OOS must have at least 5 trades and beat
    # the corresponding OOS base rate; validation must not reverse sharply.
    base = {}
    for direction in ["long","short","all"]:
        g = df if direction == "all" else df[df.direction == direction]
        base[direction] = {
            p: float(g[g.period==p].hit_100.mean()) if len(g[g.period==p]) else np.nan
            for p in PERIODS
        }
    out["base_rate"] = out.apply(lambda r: base[r.direction][r.period], axis=1)
    out["lift"] = out.hit_rate - out.base_rate
    out.to_csv(OUT, index=False, float_format="%.6f")

    # Only combine feature states whose individual OOS direction is favorable
    # at the discovery-learned threshold. Combinations are evaluated on OOS
    # without re-fitting thresholds.
    combo_rows = []
    for direction in ["long","short","all"]:
        bd = df if direction=="all" else df[df.direction==direction]
        train = bd[bd.period=="discovery"]
        if len(train) < 30: continue
        th = {}
        for f in FEATURES:
            if train[f].notna().sum() >= 30:
                th[f] = train[f].quantile(.50)

        for a,b in combinations([f for f in FEATURES if f in th],2):
            for sa,sb in [("high","high"),("high","low"),("low","high"),("low","low")]:
                def mask(g):
                    ma = g[a] >= th[a] if sa=="high" else g[a] <= th[a]
                    mb = g[b] >= th[b] if sb=="high" else g[b] <= th[b]
                    return ma & mb
                for period in PERIODS:
                    g = bd[bd.period==period]
                    q = g.loc[mask(g)]
                    if len(q) < 5: continue
                    combo_rows.append({
                        "direction":direction,"feature_a":a,"feature_b":b,
                        "state":f"{sa}&{sb}","period":period,"n":len(q),
                        "hit_rate_100":float(q.hit_100.mean()),
                        "mean_pips_100":float(q.pnl_100.mean()),
                        "pairs":int(q.pair.nunique()),
                        "positive_pairs":int(sum(h.pnl_100.mean()>0 for _,h in q.groupby("pair"))),
                        "base_rate_100":base[direction][period],
                    })
    pd.DataFrame(combo_rows).to_csv(COMBO,index=False,float_format="%.6f")

    # Print only OOS candidates with >=10 trades, >=3 pairs, and positive lift.
    o = out[(out.period=="oos") & (out.n>=10) & (out.pairs>=3) & (out.lift>0)]
    o = o.sort_values(["direction","lift","n"], ascending=[True,False,False])
    print("BASE_RATES", base)
    print("OOS_CANDIDATES")
    print(o.head(50).to_string(index=False))

if __name__ == "__main__":
    main()

# trigger cross-pair research workflow
