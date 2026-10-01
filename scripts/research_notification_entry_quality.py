#!/usr/bin/env python3
"""Audit whether frozen H4 notification signals are arriving too late.

Research only. The frozen notification rule is replayed exactly, then each
signal is scored using only information available at the completed signal
candle. Future OHLC is used only for outcome labels.
"""
from pathlib import Path
import importlib.util
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("d", ROOT / "scripts/research_50pip_direct_entry.py")
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

PAIRS = d.PAIRS
H4 = pd.Timedelta(hours=4)
TARGETS = [50, 100, 150, 200]
MAX_BARS = 24


def pip_size(pair):
    return 0.01 if "jpy" in pair else 0.0001


def replay_pair(pair):
    g = d.load_market("h4", pair).sort_values("timestamp").reset_index(drop=True)
    if g is None or g.empty:
        return []
    f = d.build_features(g)
    e20 = g.close.ewm(span=20, adjust=False).mean()
    e200 = g.close.ewm(span=200, adjust=False).mean()
    gc = (e20.shift(1) <= e200.shift(1)) & (e20 > e200)
    dc = (e20.shift(1) >= e200.shift(1)) & (e20 < e200)

    state = "WAIT"
    direction = None
    touch = None
    ref = None
    breach_streak = 0
    signals = []

    for i in range(1, len(g)):
        if state == "WAIT":
            if bool(gc.iloc[i]):
                direction = "long"
                state = "SEARCH_TOUCH"
            elif bool(dc.iloc[i]):
                direction = "short"
                state = "SEARCH_TOUCH"

        elif state == "SEARCH_TOUCH":
            reverse = (direction == "long" and bool(dc.iloc[i])) or (direction == "short" and bool(gc.iloc[i]))
            if reverse:
                state = "WAIT"
                direction = None
                touch = None
                ref = None
                breach_streak = 0
                continue
            if float(g.low.iloc[i]) <= float(e20.iloc[i]) <= float(g.high.iloc[i]):
                touch = i
                ref = float(g.high.iloc[i] if direction == "long" else g.low.iloc[i])
                breach_streak = 0
                state = "ARMED"

        elif state == "ARMED":
            reverse = (direction == "long" and bool(dc.iloc[i])) or (direction == "short" and bool(gc.iloc[i]))
            if reverse:
                state = "WAIT"
                direction = None
                touch = None
                ref = None
                breach_streak = 0
                continue

            filt = (
                bool(f.sma_stack_bull.iloc[i]) and bool(f.di_strong_bull.iloc[i])
                if direction == "long" else bool(f.strong_close_bear.iloc[i])
            )
            trig = float(g.close.iloc[i]) > ref if direction == "long" else float(g.close.iloc[i]) < ref
            if filt and trig:
                signals.append((i, touch, direction))
                state = "TRIGGERED"
            else:
                breached = (
                    (direction == "long" and float(g.close.iloc[i]) <= float(g.low.iloc[touch]))
                    or (direction == "short" and float(g.close.iloc[i]) >= float(g.high.iloc[touch]))
                )
                breach_streak = breach_streak + 1 if breached else 0
                if breach_streak >= 2:
                    state = "WAIT"
                    direction = None
                    touch = None
                    ref = None
                    breach_streak = 0

        elif state == "TRIGGERED":
            # Only the next H4 open is the entry candidate.
            state = "WAIT"
            direction = None
            touch = None
            ref = None
            breach_streak = 0

    return build_signal_rows(g, f, e20, e200, pair, signals)


def build_signal_rows(g, f, e20, e200, pair, signals):
    pip = pip_size(pair)
    rows = []
    for si, ti, direction in signals:
        if si + 1 >= len(g):
            continue
        entry_i = si + 1
        entry = float(g.open.iloc[entry_i])
        stop = float(g.low.iloc[ti] if direction == "long" else g.high.iloc[ti])
        sign = 1 if direction == "long" else -1

        atr = float(f.atr14.iloc[si]) if "atr14" in f else float((g.high-g.low).rolling(14).mean().iloc[si])
        atr = atr if np.isfinite(atr) and atr > 0 else np.nan

        sig_range = float(g.high.iloc[si] - g.low.iloc[si])
        sig_body = abs(float(g.close.iloc[si] - g.open.iloc[si]))
        pre_i = max(0, si - 6)
        pre_move = sign * (float(g.close.iloc[si]) - float(g.close.iloc[pre_i]))
        touch_move = sign * (float(g.close.iloc[si]) - float(g.close.iloc[ti]))

        row = {
            "pair": pair,
            "direction": direction,
            "signal_timestamp": g.timestamp.iloc[si],
            "entry_timestamp": g.timestamp.iloc[entry_i],
            "touch_timestamp": g.timestamp.iloc[ti],
            "entry_price": entry,
            "stop_price": stop,
            "stop_distance_pips": sign * (stop - entry) / pip,
            "bars_touch_to_signal": si - ti,
            "signal_range_pips": sig_range / pip,
            "signal_body_pips": sig_body / pip,
            "signal_body_ratio": sig_body / sig_range if sig_range > 0 else np.nan,
            "signal_range_atr": sig_range / atr if np.isfinite(atr) else np.nan,
            "signal_body_atr": sig_body / atr if np.isfinite(atr) else np.nan,
            "ema20_distance_pips": sign * (float(g.close.iloc[si]) - float(e20.iloc[si])) / pip,
            "ema20_distance_atr": sign * (float(g.close.iloc[si]) - float(e20.iloc[si])) / atr if np.isfinite(atr) else np.nan,
            "touch_to_signal_pips": touch_move / pip,
            "touch_to_signal_atr": touch_move / atr if np.isfinite(atr) else np.nan,
            "pre6_move_pips": pre_move / pip,
            "pre6_move_atr": pre_move / atr if np.isfinite(atr) else np.nan,
            "atr_pips": atr / pip if np.isfinite(atr) else np.nan,
            "period": ("discovery" if g.timestamp.iloc[entry_i].year <= 2024
                       else "validation" if g.timestamp.iloc[entry_i].year == 2025
                       else "oos"),
        }

        for target in TARGETS:
            result = None
            bars = None
            for k in range(entry_i, min(len(g), entry_i + MAX_BARS + 1)):
                hi = float(g.high.iloc[k])
                lo = float(g.low.iloc[k])
                if (direction == "long" and lo <= stop) or (direction == "short" and hi >= stop):
                    result = sign * (stop - entry) / pip
                    bars = k - entry_i
                    break
                if (direction == "long" and hi >= entry + target * pip) or (
                    direction == "short" and lo <= entry - target * pip
                ):
                    result = float(target)
                    bars = k - entry_i
                    break
            if result is None:
                k = min(len(g) - 1, entry_i + MAX_BARS)
                result = sign * (float(g.close.iloc[k]) - entry) / pip
                bars = k - entry_i
            row[f"pnl_{target}"] = result
            row[f"hit_{target}"] = bool(result >= target)

        rows.append(row)
    return rows


def summarize(df):
    rows = []
    metrics = [
        ("all", pd.Series(True, index=df.index)),
        ("range_atr_le_0_75", df.signal_range_atr <= 0.75),
        ("range_atr_0_75_1_25", (df.signal_range_atr > 0.75) & (df.signal_range_atr <= 1.25)),
        ("range_atr_gt_1_25", df.signal_range_atr > 1.25),
        ("ema20_dist_atr_le_0_50", df.ema20_distance_atr <= 0.50),
        ("ema20_dist_atr_gt_0_50", df.ema20_distance_atr > 0.50),
        ("touch_to_signal_atr_le_1", df.touch_to_signal_atr <= 1.0),
        ("touch_to_signal_atr_gt_1", df.touch_to_signal_atr > 1.0),
        ("pre6_move_atr_le_2", df.pre6_move_atr <= 2.0),
        ("pre6_move_atr_gt_2", df.pre6_move_atr > 2.0),
    ]
    for period in ["discovery", "validation", "oos"]:
        for direction in ["long", "short"]:
            g = df[(df.period == period) & (df.direction == direction)]
            for bucket, mask_all in metrics:
                m = mask_all.loc[g.index]
                q = g.loc[m]
                if q.empty:
                    continue
                for target in TARGETS:
                    v = q[f"pnl_{target}"]
                    rows.append([
                        period, direction, bucket, target, len(q),
                        float(q[f"hit_{target}"].mean()),
                        float(v.mean()), float(v.median()),
                        float(v.sum())
                    ])
    return pd.DataFrame(rows, columns=[
        "period","direction","bucket","target_pips","trades",
        "hit_rate","mean_pips","median_pips","total_pips"
    ])


def main():
    Path("reports").mkdir(exist_ok=True)
    rows = []
    for pair in PAIRS:
        rows.extend(replay_pair(pair))
    if not rows:
        raise RuntimeError("No notification signals found.")

    df = pd.DataFrame(rows)
    df.to_csv("reports/notification_entry_quality_signals.csv", index=False, float_format="%.6f")

    summary = summarize(df)
    summary.to_csv("reports/notification_entry_quality_summary.csv", index=False, float_format="%.6f")

    oos = summary[summary.period == "oos"].sort_values(["target_pips","hit_rate"], ascending=[True,False])
    print("signals", len(df))
    print(oos.head(40).to_string(index=False))


if __name__ == "__main__":
    main()
