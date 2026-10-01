#!/usr/bin/env python3
"""Research causal price-structure / momentum-transition patterns.

The source idea is:
1) strong directional move,
2) opposing side stops extending,
3) swing structure changes (HL for bullish / LH for bearish),
4) the last opposing swing / descending-or-ascending structure breaks,
5) enter only after candle close confirmation.

This is research only. It does NOT modify or reproduce the frozen H4 notification rule.

Causality:
- Swing points are confirmed with LEFT/RIGHT bars. A swing is only available after
  the required RIGHT bars have completed.
- Trendline values are calculated only from already-confirmed swing points.
- Breakout is evaluated on the completed candle close.
- Future +50/+100/+150/+200 pip moves are labels only.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    "usdjpy","eurjpy","gbpjpy","audjpy",
    "eurusd","gbpusd","audusd","nzdusd",
    "usdcad","usdchf","audnzd","eurgbp",
]
TFS = ["w1", "d1", "h4", "h1"]
# W1/D1 are first-class structure timeframes; H1 remains optional research data.
HORIZONS = {"w1": [1, 2, 3, 6, 12], "d1": [1, 3, 6, 12, 24], "h4": [1, 3, 6, 12, 24], "h1": [1, 3, 6, 12, 24]}
TARGETS = [50, 100, 150, 200]
SWING_N = 2


def load_market(tf, pair):
    path = ROOT / "data" / "market" / tf / f"{pair}.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    return df.sort_values("timestamp").drop_duplicates("timestamp").reset_index(drop=True)


def pip_size(pair):
    return 0.01 if "jpy" in pair else 0.0001


def confirmed_swings(df, n=SWING_N):
    h, l = df["high"], df["low"]
    # A swing is only marked at index i+n, so the pivot was known only after n
    # completed candles to the right.
    sh = pd.Series(False, index=df.index)
    sl = pd.Series(False, index=df.index)
    for i in range(n, len(df)-n):
        if h.iloc[i] == h.iloc[i-n:i+n+1].max() and (h.iloc[i-n:i+n+1] == h.iloc[i]).sum() == 1:
            sh.iloc[i+n] = True
        if l.iloc[i] == l.iloc[i-n:i+n+1].min() and (l.iloc[i-n:i+n+1] == l.iloc[i]).sum() == 1:
            sl.iloc[i+n] = True
    return sh, sl


def add_labels(df, pair):
    p = pip_size(pair)
    out = {}
    close = df["close"].to_numpy()
    high = df["high"].to_numpy()
    low = df["low"].to_numpy()
    for target in TARGETS:
        up = np.zeros(len(df), dtype=bool)
        dn = np.zeros(len(df), dtype=bool)
        for i in range(len(df)):
            end = min(len(df), i + 25)
            if i + 1 < end:
                up[i] = np.max(high[i+1:end]) >= close[i] + target*p
                dn[i] = np.min(low[i+1:end]) <= close[i] - target*p
        out[f"hit_up_{target}"] = up
        out[f"hit_dn_{target}"] = dn
    return pd.DataFrame(out, index=df.index)


def build_features(df, pair):
    x = df.copy()
    x["atr14"] = (x["high"]-x["low"]).rolling(14).mean()
    sh, sl = confirmed_swings(x)
    x["confirmed_swing_high"] = sh
    x["confirmed_swing_low"] = sl

    # Store the latest two confirmed swing highs/lows available at each candle.
    high_idx = []
    low_idx = []
    last_highs = []
    last_lows = []
    for i in range(len(x)):
        if sh.iloc[i]:
            high_idx.append(i)
        if sl.iloc[i]:
            low_idx.append(i)
        high_idx = high_idx[-8:]
        low_idx = low_idx[-8:]
        last_highs.append(tuple(high_idx))
        last_lows.append(tuple(low_idx))

    bull_hl = np.zeros(len(x), dtype=bool)
    bear_lh = np.zeros(len(x), dtype=bool)
    bull_break = np.zeros(len(x), dtype=bool)
    bear_break = np.zeros(len(x), dtype=bool)
    down_line_break = np.zeros(len(x), dtype=bool)
    up_line_break = np.zeros(len(x), dtype=bool)
    down_line_break_event = np.zeros(len(x), dtype=bool)
    up_line_break_event = np.zeros(len(x), dtype=bool)
    strong_bull = np.zeros(len(x), dtype=bool)
    strong_bear = np.zeros(len(x), dtype=bool)

    for i in range(len(x)):
        highs = last_highs[i]
        lows = last_lows[i]

        if len(lows) >= 2:
            a, b = lows[-2], lows[-1]
            bull_hl[i] = x.loc[b, "low"] > x.loc[a, "low"]

        if len(highs) >= 2:
            a, b = highs[-2], highs[-1]
            bear_lh[i] = x.loc[b, "high"] < x.loc[a, "high"]

        if len(highs) >= 1:
            last_h = x.loc[highs[-1], "high"]
            bull_break[i] = x.loc[i, "close"] > last_h

        if len(lows) >= 1:
            last_l = x.loc[lows[-1], "low"]
            bear_break[i] = x.loc[i, "close"] < last_l

        # Descending line from the latest two confirmed swing highs.
        if len(highs) >= 2:
            a, b = highs[-2], highs[-1]
            if x.loc[b, "high"] < x.loc[a, "high"] and b > a:
                slope = (x.loc[b, "high"] - x.loc[a, "high"]) / (b-a)
                line = x.loc[b, "high"] + slope * (i-b)
                down_line_break[i] = x.loc[i, "close"] > line
                if i > b:
                    prev_line = x.loc[b, "high"] + slope * (i-1-b)
                    down_line_break_event[i] = x.loc[i, "close"] > line and x.loc[i-1, "close"] <= prev_line

        # Ascending line from the latest two confirmed swing lows.
        if len(lows) >= 2:
            a, b = lows[-2], lows[-1]
            if x.loc[b, "low"] > x.loc[a, "low"] and b > a:
                slope = (x.loc[b, "low"] - x.loc[a, "low"]) / (b-a)
                line = x.loc[b, "low"] + slope * (i-b)
                up_line_break[i] = x.loc[i, "close"] < line
                if i > b:
                    prev_line = x.loc[b, "low"] + slope * (i-1-b)
                    up_line_break_event[i] = x.loc[i, "close"] < line and x.loc[i-1, "close"] >= prev_line

        rng = x.loc[i, "high"] - x.loc[i, "low"]
        body = abs(x.loc[i, "close"] - x.loc[i, "open"])
        strong_bull[i] = rng > 0 and x.loc[i, "close"] > x.loc[i, "open"] and body/rng >= 0.60
        strong_bear[i] = rng > 0 and x.loc[i, "close"] < x.loc[i, "open"] and body/rng >= 0.60

    x["bull_hl"] = bull_hl
    x["bear_lh"] = bear_lh
    x["bull_break"] = bull_break
    x["bear_break"] = bear_break
    x["descending_line_break_up"] = down_line_break
    x["ascending_line_break_down"] = up_line_break
    x["descending_line_break_up_event"] = down_line_break_event
    x["ascending_line_break_down_event"] = up_line_break_event
    x["strong_bull_close"] = strong_bull
    x["strong_bear_close"] = strong_bear

    # Composite hypotheses derived from the source material.
    x["bull_structure_shift"] = x["bull_hl"] & x["bull_break"]
    x["bear_structure_shift"] = x["bear_lh"] & x["bear_break"]
    x["bull_trendline_confirmation"] = x["bull_hl"] & x["descending_line_break_up"]
    x["bear_trendline_confirmation"] = x["bear_lh"] & x["ascending_line_break_down"]
    x["bull_full_structure"] = x["bull_hl"] & x["bull_break"] & x["descending_line_break_up"] & x["strong_bull_close"]
    x["bear_full_structure"] = x["bear_lh"] & x["bear_break"] & x["ascending_line_break_down"] & x["strong_bear_close"]
    return x


def evaluate(g, features, direction, period):
    rows = []
    for feature in features:
        m = g[feature].fillna(False)
        for target in TARGETS:
            label = f"hit_{'up' if direction=='bull' else 'dn'}_{target}"
            a = g.loc[m, label]
            b = g.loc[~m, label]
            if len(a) == 0:
                continue
            ar = float(a.mean())
            br = float(b.mean()) if len(b) else np.nan
            rows.append([
                period, direction, feature, target, int(len(a)), ar, br,
                ar-br if np.isfinite(br) else np.nan,
                ar/br if np.isfinite(br) and br else np.nan
            ])
    return rows


def main():
    Path("reports").mkdir(exist_ok=True)
    chunks = []
    missing = []
    for tf in TFS:
        for pair in PAIRS:
            df = load_market(tf, pair)
            if df is None:
                missing.append(f"{tf}:{pair}")
                continue
            f = build_features(df, pair)
            labels = add_labels(df, pair)
            z = pd.concat([df[["timestamp","open","high","low","close"]], f.drop(columns=df.columns, errors="ignore"), labels], axis=1)
            z["pair"] = pair
            z["timeframe"] = tf
            chunks.append(z)

    if not chunks:
        raise RuntimeError("No market data found.")

    all_df = pd.concat(chunks, ignore_index=True)
    features_bull = [
        "bull_hl","bull_break","descending_line_break_up","descending_line_break_up_event",
        "bull_structure_shift","bull_trendline_confirmation","bull_full_structure"
    ]
    features_bear = [
        "bear_lh","bear_break","ascending_line_break_down","ascending_line_break_down_event",
        "bear_structure_shift","bear_trendline_confirmation","bear_full_structure"
    ]

    rows = []
    for tf in TFS:
        gtf = all_df[all_df.timeframe == tf]
        if gtf.empty:
            continue
        for period, g in [
            ("discovery", gtf[gtf.timestamp.dt.year <= 2024]),
            ("validation", gtf[gtf.timestamp.dt.year == 2025]),
            ("oos", gtf[gtf.timestamp.dt.year >= 2026]),
        ]:
            if g.empty:
                continue
            for direction, feats in [("bull", features_bull), ("bear", features_bear)]:
                rows.extend(evaluate(g, feats, direction, period))

    out = pd.DataFrame(rows, columns=[
        "period","direction","feature","target_pips","samples",
        "hit_rate","baseline_without_feature","difference","lift"
    ])
    out.to_csv("reports/price_structure_transition_effects.csv", index=False, float_format="%.8f")

    # Pair robustness on OOS for the composite candidates.
    rob = []
    composites = [
        ("bull","descending_line_break_up_event"),
        ("bull","bull_structure_shift"),
        ("bull","bull_trendline_confirmation"),
        ("bull","bull_full_structure"),
        ("bear","ascending_line_break_down_event"),
        ("bear","bear_structure_shift"),
        ("bear","bear_trendline_confirmation"),
        ("bear","bear_full_structure"),
    ]
    for tf in TFS:
        gtf = all_df[(all_df.timeframe == tf) & (all_df.timestamp.dt.year >= 2026)]
        for pair in PAIRS:
            g = gtf[gtf.pair == pair]
            for direction, feature in composites:
                for target in TARGETS:
                    label = f"hit_{'up' if direction=='bull' else 'dn'}_{target}"
                    m = g[feature].fillna(False)
                    if int(m.sum()) >= 5:
                        rob.append([tf,pair,direction,feature,target,int(m.sum()),float(g.loc[m,label].mean())])
    pd.DataFrame(rob, columns=[
        "timeframe","pair","direction","feature","target_pips","samples","oos_hit_rate"
    ]).to_csv("reports/price_structure_transition_pair_robustness.csv", index=False, float_format="%.8f")

    summary = {
        "missing_data": ",".join(missing),
        "rows_analyzed": int(len(all_df)),
        "timeframes_available": ",".join(sorted(all_df.timeframe.unique())),
        "status": "PASS"
    }
    pd.DataFrame([summary]).to_csv("reports/price_structure_transition_summary.csv", index=False)

    print("rows_analyzed", len(all_df))
    print("missing_data", ",".join(missing) if missing else "none")
    print(out[out.period=="oos"].sort_values(["lift","samples"], ascending=[False,False]).head(40).to_string(index=False))


if __name__ == "__main__":
    main()
