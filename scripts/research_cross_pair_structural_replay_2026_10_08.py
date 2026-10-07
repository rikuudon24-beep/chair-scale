#!/usr/bin/env python3
"""Cross-pair frozen-notification replay with stable entry-quality filters.

Entry filters are frozen from Discovery:
A) EMA20 distance <= 1.365 ATR AND touch->signal bars <= 6
B) signal range <= 1.151613 ATR AND touch->signal bars <= 6

Exits are structural, not fixed-pip:
- initial stop = touch candle extreme
- exit = opposite 3-bar structure break or EMA20 cross
- timeout = market close after 20 H4 bars

Important: favorable structure breaks are continuation signals, NOT exits.
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SIG=ROOT/"reports/notification_entry_quality_signals.csv"
PAIRS=["usdjpy","eurjpy","gbpjpy","audjpy","eurusd","gbpusd","audusd","nzdusd","usdcad","usdchf","audnzd","eurgbp"]
PIP={p:0.01 if "jpy" in p else 0.0001 for p in PAIRS}
MAX_HOLD=20

FILTERS={
 "A_ema_distance_fast":lambda r:r.ema20_distance_atr<=1.365379 and r.bars_touch_to_signal<=6,
 "B_range_fast":lambda r:r.signal_range_atr<=1.151613 and r.bars_touch_to_signal<=6,
}

def period(ts):
    y=ts.year
    return "discovery" if y<=2024 else "validation" if y==2025 else "oos"

def run_row(r):
    pair=r.pair
    pip=PIP[pair]
    g=pd.read_csv(ROOT/f"data/market/h4/{pair}.csv")
    g.timestamp=pd.to_datetime(g.timestamp,unit="ms",utc=True)
    idx=g.index[g.timestamp==pd.Timestamp(r.entry_timestamp)].tolist()
    if not idx:
        return None
    i=idx[0]
    if i>=len(g)-1:
        return None

    e=float(g.open.iloc[i])
    touch_idx=g.index[g.timestamp==pd.Timestamp(r.touch_timestamp)].tolist()
    if not touch_idx:
        return None
    t=touch_idx[0]
    direction=r.direction

    # The touch candle is the structural invalidation point.
    stop=float(g.low.iloc[t]) if direction=="long" else float(g.high.iloc[t])

    ema=g.close.ewm(span=20,adjust=False).mean()
    outcome=None
    exit_i=None
    exit_price=None
    reason=None

    end=min(len(g)-1,i+MAX_HOLD)

    for j in range(i,end+1):
        hi=float(g.high.iloc[j])
        lo=float(g.low.iloc[j])
        c=float(g.close.iloc[j])

        if direction=="long" and lo<=stop:
            outcome=(stop-e)/pip
            exit_i=j
            exit_price=stop
            reason="touch_stop"
            break
        if direction=="short" and hi>=stop:
            outcome=(e-stop)/pip
            exit_i=j
            exit_price=stop
            reason="touch_stop"
            break

        if j>i and j>=3:
            prior_high=float(g.high.iloc[j-3:j].max())
            prior_low=float(g.low.iloc[j-3:j].min())

            # Exit only when price breaks structure AGAINST the position.
            if direction=="long" and c<prior_low:
                outcome=(c-e)/pip
                exit_i=j
                exit_price=c
                reason="structure3_opposite"
                break

            if direction=="short" and c>prior_high:
                outcome=(e-c)/pip
                exit_i=j
                exit_price=c
                reason="structure3_opposite"
                break

        if j>i:
            prev_c=float(g.close.iloc[j-1])
            prev_ema=float(ema.iloc[j-1])
            cur_ema=float(ema.iloc[j])

            if direction=="long" and c<cur_ema and prev_c>=prev_ema:
                outcome=(c-e)/pip
                exit_i=j
                exit_price=c
                reason="ema20"
                break

            if direction=="short" and c>cur_ema and prev_c<=prev_ema:
                outcome=(e-c)/pip
                exit_i=j
                exit_price=c
                reason="ema20"
                break

    if outcome is None:
        c=float(g.close.iloc[end])
        outcome=(c-e)/pip if direction=="long" else (e-c)/pip
        exit_i=end
        exit_price=c
        reason="timeout"

    return outcome,reason,exit_i-i

def main():
    df=pd.read_csv(SIG)
    df.signal_timestamp=pd.to_datetime(df.signal_timestamp,utc=True)
    df.entry_timestamp=pd.to_datetime(df.entry_timestamp,utc=True)
    df.touch_timestamp=pd.to_datetime(df.touch_timestamp,utc=True)

    for f,fn in FILTERS.items():
        rows=[]
        for _,r in df.iterrows():
            if not fn(r):
                continue
            x=run_row(r)
            if not x:
                continue
            pnl,reason,bars=x
            rows.append([f,r.pair,r.direction,period(r.entry_timestamp),r.entry_timestamp,pnl,reason,bars])

        out=pd.DataFrame(
            rows,
            columns=["filter","pair","direction","period","entry_timestamp","pnl_pips","exit_reason","hold_bars"]
        )
        out.to_csv(ROOT/f"reports/cross_pair_structural_replay_{f}_2026-10-08.csv",index=False)

        summ=[]
        for p in ["discovery","validation","oos"]:
            for d in ["long","short","all"]:
                q=out[out.period==p] if d=="all" else out[(out.period==p)&(out.direction==d)]
                if q.empty:
                    continue
                wins=q.pnl_pips>0
                grosswin=q.loc[wins,"pnl_pips"].sum()
                grossloss=-q.loc[~wins,"pnl_pips"].sum()
                pf=grosswin/grossloss if grossloss>0 else np.inf
                summ.append([
                    f,p,d,len(q),float(wins.mean()),float(q.pnl_pips.mean()),
                    float(q.pnl_pips.sum()),float(pf),int(q.pair.nunique()),
                    q.exit_reason.value_counts().to_dict()
                ])

        pd.DataFrame(
            summ,
            columns=["filter","period","direction","n","win_rate","mean_pips","total_pips","profit_factor","pairs","exit_reasons"]
        ).to_csv(ROOT/f"reports/cross_pair_structural_summary_{f}_2026-10-08.csv",index=False)

if __name__=="__main__":
    main()
