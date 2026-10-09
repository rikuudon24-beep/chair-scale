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
TFS = ["w1", "d1", "h4"]
# H1 is computationally much larger than the higher timeframes. Keep H1 out
# of the default core run, but allow CI to explicitly select it.
ALL_TFS = ["w1", "d1", "h4", "h1"]
TF_FILTER = __import__("os").environ.get("FX_RESEARCH_TF", "").strip().lower()
if TF_FILTER:
    TFS = [TF_FILTER] if TF_FILTER in ALL_TFS else TFS
# W1/D1/H4 are the first-class core timeframes; H1 is isolated by CI.
HORIZONS = {"w1": [1, 2, 3, 6, 12], "d1": [1, 3, 6, 12, 24], "h4": [1, 3, 6, 12, 24], "h1": [1, 3, 6, 12, 24]}
TARGETS = [50, 100, 150, 200]
SWING_N = 2


def normalize_timestamp_column(values):
    """Parse numeric Unix timestamps in seconds or milliseconds safely.

    Market CSVs have historically used both units. Infer one unit for the
    entire column, reject mixed numeric magnitudes, and fail with a useful
    message instead of allowing a year-52960 OutOfBoundsDatetime exception.
    ISO-8601 strings remain supported for diagnostic/research fixtures.
    """
    raw = pd.Series(values)
    numeric = pd.to_numeric(raw, errors="coerce")
    numeric_mask = numeric.notna()

    if numeric_mask.all():
        if numeric.empty:
            raise ValueError("timestamp column is empty")
        magnitudes = numeric.abs()
        # Current FX data should be either seconds (~1e9) or milliseconds (~1e12).
        is_ms = magnitudes >= 100_000_000_000
        is_seconds = (magnitudes >= 100_000_000) & (magnitudes < 100_000_000_000)
        if not (is_ms | is_seconds).all():
            bad = raw.loc[~(is_ms | is_seconds)].head(3).tolist()
            raise ValueError(f"timestamp values are outside supported Unix seconds/ms ranges: {bad}")
        if is_ms.any() and is_seconds.any():
            raise ValueError("timestamp column mixes Unix seconds and milliseconds")
        unit = "ms" if is_ms.all() else "s"
        try:
            parsed = pd.to_datetime(numeric, unit=unit, utc=True, errors="raise")
        except (ValueError, OverflowError, pd.errors.OutOfBoundsDatetime) as exc:
            raise ValueError(f"invalid Unix timestamp column interpreted as {unit}: {exc}") from exc
    else:
        if numeric_mask.any():
            raise ValueError("timestamp column mixes numeric Unix values and non-numeric timestamps")
        parsed = pd.to_datetime(raw, utc=True, errors="raise")
    if parsed.isna().any():
        raise ValueError("timestamp column contains missing or invalid timestamps")
    return parsed


def load_market(tf, pair):
    path = ROOT / "data" / "market" / tf / f"{pair}.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    if "timestamp" not in df.columns:
        raise ValueError(f"{path}: required timestamp column is missing")
    try:
        df["timestamp"] = normalize_timestamp_column(df["timestamp"])
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{path}: cannot normalize timestamps: {exc}") from exc
    return df.sort_values("timestamp").drop_duplicates("timestamp").reset_index(drop=True)


def pip_size(pair):
    return 0.01 if "jpy" in pair else 0.0001


def confirmed_swings(df, n=SWING_N):
    """Return swing markers at the first candle where the pivot is knowable.

    The pivot itself is at i; it becomes available at i+n after n completed
    right-side candles. The rolling implementation is equivalent to the
    original explicit-window test, but avoids a Python loop over every row.
    """
    h = df["high"]
    l = df["low"]
    width = 2*n + 1

    hmax = h.rolling(width, center=True, min_periods=width).max()
    lmin = l.rolling(width, center=True, min_periods=width).min()
    heq = h.eq(hmax)
    leq = l.eq(lmin)

    # Require the pivot value to be unique inside its confirmation window.
    hcount = heq.astype("int8").rolling(width, center=True, min_periods=width).sum()
    lcount = leq.astype("int8").rolling(width, center=True, min_periods=width).sum()
    pivot_high = heq & hcount.eq(1)
    pivot_low = leq & lcount.eq(1)

    # shift(+n) makes a pivot at i visible at i+n.
    sh = pivot_high.shift(n, fill_value=False).astype(bool)
    sl = pivot_low.shift(n, fill_value=False).astype(bool)
    return sh, sl

def add_labels(df, pair):
    p = pip_size(pair)
    out = {}
    close = df["close"].to_numpy()
    high = df["high"].to_numpy()
    low = df["low"].to_numpy()
    # Vectorized future-window labels. These are labels only and never feed
    # feature construction, so using future prices here cannot create leakage.
    future_high = pd.concat([df["high"].shift(-k) for k in range(1, 25)], axis=1).max(axis=1)
    future_low = pd.concat([df["low"].shift(-k) for k in range(1, 25)], axis=1).min(axis=1)
    for target in TARGETS:
        out[f"hit_up_{target}"] = (future_high >= df["close"] + target*p).fillna(False).to_numpy()
        out[f"hit_dn_{target}"] = (future_low <= df["close"] - target*p).fillna(False).to_numpy()
    return pd.DataFrame(out, index=df.index)


def build_features(df, pair):
    x = df.copy()
    high = x["high"].to_numpy(dtype=float)
    low = x["low"].to_numpy(dtype=float)
    open_ = x["open"].to_numpy(dtype=float)
    close = x["close"].to_numpy(dtype=float)

    x["atr14"] = (x["high"]-x["low"]).rolling(14).mean()
    sh, sl = confirmed_swings(x)
    shv = sh.to_numpy(dtype=bool)
    slv = sl.to_numpy(dtype=bool)
    x["confirmed_swing_high"] = shv
    x["confirmed_swing_low"] = slv

    nrows = len(x)
    bull_hl = np.zeros(nrows, dtype=bool)
    bear_lh = np.zeros(nrows, dtype=bool)
    bull_break = np.zeros(nrows, dtype=bool)
    bear_break = np.zeros(nrows, dtype=bool)
    down_line_break = np.zeros(nrows, dtype=bool)
    up_line_break = np.zeros(nrows, dtype=bool)
    down_line_break_event = np.zeros(nrows, dtype=bool)
    up_line_break_event = np.zeros(nrows, dtype=bool)
    strong_bull = np.zeros(nrows, dtype=bool)
    strong_bear = np.zeros(nrows, dtype=bool)

    # Only the latest two confirmed pivots are needed. Keeping scalar indices
    # avoids allocating a tuple/list snapshot for every H1 candle.
    h1 = h2 = l1 = l2 = -1
    for i in range(nrows):
        if shv[i]:
            h1, h2 = h2, i
        if slv[i]:
            l1, l2 = l2, i

        if l1 >= 0 and l2 >= 0:
            bull_hl[i] = low[l2] > low[l1]

        if h1 >= 0 and h2 >= 0:
            bear_lh[i] = high[h2] < high[h1]

        if h2 >= 0:
            bull_break[i] = close[i] > high[h2]

        if l2 >= 0:
            bear_break[i] = close[i] < low[l2]

        # Descending line from the latest two confirmed swing highs.
        if h1 >= 0 and h2 >= 0 and high[h2] < high[h1] and h2 > h1:
            slope = (high[h2] - high[h1]) / (h2-h1)
            line = high[h2] + slope * (i-h2)
            down_line_break[i] = close[i] > line
            if i > h2:
                prev_line = high[h2] + slope * (i-1-h2)
                down_line_break_event[i] = close[i] > line and close[i-1] <= prev_line

        # Ascending line from the latest two confirmed swing lows.
        if l1 >= 0 and l2 >= 0 and low[l2] > low[l1] and l2 > l1:
            slope = (low[l2] - low[l1]) / (l2-l1)
            line = low[l2] + slope * (i-l2)
            up_line_break[i] = close[i] < line
            if i > l2:
                prev_line = low[l2] + slope * (i-1-l2)
                up_line_break_event[i] = close[i] < line and close[i-1] >= prev_line

        rng = high[i] - low[i]
        body = abs(close[i] - open_[i])
        if rng > 0:
            strong_bull[i] = close[i] > open_[i] and body/rng >= 0.60
            strong_bear[i] = close[i] < open_[i] and body/rng >= 0.60

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
    suffix = f"_{TF_FILTER}" if TF_FILTER else ""
    out.to_csv(f"reports/price_structure_transition_effects{suffix}.csv", index=False, float_format="%.8f")

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
    ]).to_csv(f"reports/price_structure_transition_pair_robustness{suffix}.csv", index=False, float_format="%.8f")

    summary = {
        "missing_data": ",".join(missing),
        "rows_analyzed": int(len(all_df)),
        "timeframes_available": ",".join(sorted(all_df.timeframe.unique())),
        "status": "PASS"
    }
    pd.DataFrame([summary]).to_csv(f"reports/price_structure_transition_summary{suffix}.csv", index=False)

    print("rows_analyzed", len(all_df))
    print("missing_data", ",".join(missing) if missing else "none")
    print(out[out.period=="oos"].sort_values(["lift","samples"], ascending=[False,False]).head(40).to_string(index=False))


if __name__ == "__main__":
    main()
