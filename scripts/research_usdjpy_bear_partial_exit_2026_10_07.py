#!/usr/bin/env python3
import pandas as pd
import numpy as np

PATH = "data/market/h4/usdjpy.csv"
ATR_N = 14
BREAK_N = 20
HOLD = 20

def add_indicators(df):
    prev = df.close.shift(1)
    tr = pd.concat([
        df.high - df.low,
        (df.high - prev).abs(),
        (df.low - prev).abs()
    ], axis=1).max(axis=1)
    df["atr"] = tr.rolling(ATR_N).mean()
    df["ema20"] = df.close.ewm(span=20, adjust=False).mean()
    return df

def extract_events(df):
    df = add_indicators(df.copy())
    out = []
    i = BREAK_N + ATR_N + 2

    while i < len(df) - HOLD - 2:
        prior_low = df.low.iloc[i-BREAK_N:i].min()
        prior_high = df.high.iloc[i-BREAK_N:i].max()

        # Initial bearish range break.
        if df.close.iloc[i] >= prior_low:
            i += 1
            continue

        level = float(prior_low)
        base_atr = float(df.atr.iloc[i])
        if not np.isfinite(base_atr):
            i += 1
            continue

        # Require extension below the broken level.
        ext = next(
            (j for j in range(i+1, min(len(df), i+11))
             if df.low.iloc[j] <= level - 0.25 * base_atr),
            None
        )
        if ext is None:
            i += 1
            continue

        # Retest the broken level within 0.10 ATR.
        ret = next(
            (j for j in range(ext+1, min(len(df), ext+11))
             if np.isfinite(df.atr.iloc[j])
             and abs(df.close.iloc[j] - level) <= 0.10 * df.atr.iloc[j]),
            None
        )
        if ret is None or df.close.iloc[ret] >= level:
            i += 1
            continue

        # Entry trigger: two consecutive bearish closes after retest.
        ent = next(
            (j for j in range(ret+1, min(len(df), ret+6))
             if df.close.iloc[j] < df.open.iloc[j]
             and df.close.iloc[j-1] < df.open.iloc[j-1]),
            None
        )
        if ent is None:
            i += 1
            continue

        out.append({
            "i": ent,
            "date": df.timestamp.iloc[ent],
            "entry": float(df.close.iloc[ent]),
            "atr": float(df.atr.iloc[ent]),
            "breakout_level": level,
            "retest_high": float(df.high.iloc[ret]),
            "structure5_high": float(df.high.iloc[ent-5:ent].max()),
            "structure10_high": float(df.high.iloc[ent-10:ent].max()),
            "breakout_i": i,
            "retest_i": ret
        })
        i = ent + 1

    return df, out

def stop_price(e, mode):
    en, a = e["entry"], e["atr"]
    if mode == "atr05":
        return en + 0.50 * a
    if mode == "atr075":
        return en + 0.75 * a
    if mode == "atr10":
        return en + 1.00 * a
    if mode == "retest":
        return e["retest_high"]
    if mode == "struct5":
        return e["structure5_high"]
    if mode == "struct10":
        return e["structure10_high"]
    raise ValueError(mode)

def simulate(df, e, sl_mode, exit_mode):
    i = e["i"]
    en = e["entry"]
    sl = stop_price(e, sl_mode)
    risk = sl - en

    if risk <= 0 or not np.isfinite(risk):
        return np.nan, 0, "INVALID"

    level = e["breakout_level"]

    for j in range(i+1, min(len(df), i+1+HOLD)):
        hi = float(df.high.iloc[j])
        cl = float(df.close.iloc[j])

        # Conservative intrabar ordering: stop is assumed first if both
        # stop and a close-based exit could occur on the same candle.
        if hi >= sl:
            return -1.0, j-i, "SL"

        if exit_mode == "swing3" and j >= i+4:
            if cl > df.high.iloc[j-3:j].max():
                return (cl-en)/risk, j-i, "SWING3"

        elif exit_mode == "ema20" and j >= i+2:
            if cl > df.ema20.iloc[j] and df.close.iloc[j-1] <= df.ema20.iloc[j-1]:
                return (cl-en)/risk, j-i, "EMA20"

        elif exit_mode == "structure5" and j >= i+6:
            if cl > df.high.iloc[j-5:j].max():
                return (cl-en)/risk, j-i, "STRUCT5"

        elif exit_mode == "structure10" and j >= i+11:
            if cl > df.high.iloc[j-10:j].max():
                return (cl-en)/risk, j-i, "STRUCT10"

        elif exit_mode == "bear_momentum" and j >= i+2:
            if (df.close.iloc[j] > df.open.iloc[j]
                    and df.close.iloc[j-1] > df.open.iloc[j-1]):
                return (cl-en)/risk, j-i, "2UP"

        elif exit_mode == "range_reentry":
            # Uses the actual breakout level stored at event detection,
            # not a reconstructed level at entry.
            if cl >= level:
                return (cl-en)/risk, j-i, "REENTRY"

    last = min(len(df)-1, i+HOLD)
    px = float(df.close.iloc[last])
    return (px-en)/risk, last-i, "TIME"

def summarize(out):
    rows = []
    for (sl_mode, exit_mode), g in out.groupby(["sl_mode", "exit_mode"]):
        for period, h in [
            ("discovery", g[g.year <= 2024]),
            ("validation", g[g.year == 2025]),
            ("oos", g[g.year >= 2026])
        ]:
            if len(h) == 0:
                continue
            gains = h.loc[h.r > 0, "r"].sum()
            losses = -h.loc[h.r < 0, "r"].sum()
            pf = gains / losses if losses > 0 else np.nan
            rows.append([
                sl_mode, exit_mode, period, len(h),
                float((h.r > 0).mean()),
                float(h.r.mean()),
                float(pf),
                float(h.r.sum()),
                float(h.r.min()),
                float(h.bars.median())
            ])
    return pd.DataFrame(rows, columns=[
        "sl_mode", "exit_mode", "period", "n", "positive_rate",
        "expectancy_r", "pf", "total_r", "worst_r", "median_bars"
    ])

def main():
    df = pd.read_csv(PATH)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df.sort_values("timestamp").reset_index(drop=True)

    df, events = extract_events(df)
    sl_modes = ["atr05", "atr075", "atr10", "retest", "struct5", "struct10"]
    exit_modes = [
        "swing3", "ema20", "structure5",
        "structure10", "bear_momentum", "range_reentry"
    ]

    rows = []
    for sl_mode in sl_modes:
        for exit_mode in exit_modes:
            for e in events:
                r, bars, outcome = simulate(df, e, sl_mode, exit_mode)
                rows.append([
                    e["date"], sl_mode, exit_mode,
                    outcome, r, bars
                ])

    out = pd.DataFrame(rows, columns=[
        "date", "sl_mode", "exit_mode", "outcome", "r", "bars"
    ])
    out["year"] = out.date.dt.year

    summary = summarize(out)
    summary.to_csv(
        "reports/usdjpy_bear_structural_exit_2026-10-07.csv",
        index=False
    )
    out.to_csv(
        "reports/usdjpy_bear_structural_exit_events_2026-10-07.csv",
        index=False
    )

    print("EVENTS", len(events))
    print(summary.to_string(index=False))

if __name__ == "__main__":
    main()
