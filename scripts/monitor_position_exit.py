#!/usr/bin/env python3
"""Monitor completed-H4 exit conditions for explicitly registered positions.

Frozen exit condition from validated independent-exit research:
LONG: price20_cross_down + di_spread_down3
SHORT: price20_cross_up + di_spread_up3

This is a notification condition, not an order executor.
"""
from pathlib import Path
import importlib.util, json
import pandas as pd

spec=importlib.util.spec_from_file_location("d","scripts/research_50pip_direct_entry.py")
d=importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
H4=pd.Timedelta(hours=4)

def market_closed_utc(now):
    # Approximate FX weekly closure: Friday 21:00 UTC through Sunday 21:00 UTC.
    return (now.weekday()==4 and now.hour>=21) or now.weekday()==5 or (now.weekday()==6 and now.hour<21)

def expected_latest_h4_open(now):
    # H4 timestamps label candle OPEN. During the weekend, the latest expected
    # completed candle is Friday 16:00 UTC (16:00-20:00), not any old row.
    if market_closed_utc(now):
        days_since_friday=(now.weekday()-4)%7
        friday=(now.normalize()-pd.Timedelta(days=days_since_friday))
        return friday+pd.Timedelta(hours=16)
    return now.floor("4h")-H4

def completed_market(pair,now=None):
    g=d.load_market("h4",pair).sort_values("timestamp").reset_index(drop=True)
    if g.empty:
        raise RuntimeError(f"{pair}: H4 market data is empty; exit state is UNKNOWN")
    now=pd.Timestamp.now(tz="UTC") if now is None else pd.Timestamp(now)
    if now.tzinfo is None:
        now=now.tz_localize("UTC")
    else:
        now=now.tz_convert("UTC")
    expected=expected_latest_h4_open(now)
    # Do not include a nominal 20:00 H4 candle over the weekend: it may be a
    # truncated session candle, not a completed four-hour candle.
    closed=g[pd.to_datetime(g.timestamp,utc=True)<=expected].copy().reset_index(drop=True)
    if closed.empty:
        raise RuntimeError(f"{pair}: no completed H4 candles available; exit state is UNKNOWN")
    latest_closed_ts=pd.to_datetime(closed.timestamp.iloc[-1],utc=True)
    lag_hours=(expected-latest_closed_ts).total_seconds()/3600
    # Fail closed on stale data even when the market is closed. Weekend handling
    # changes the expected timestamp; it must never disable the freshness gate.
    if lag_hours>4:
        raise RuntimeError(
            f"{pair}: completed H4 data stale; latest_closed={latest_closed_ts.isoformat()}, "
            f"expected={expected.isoformat()}, lag={lag_hours:.1f}h. "
            "Exit state is UNKNOWN; do not treat this as HOLD_NO_EXIT."
        )
    return closed

def evaluate(pos):
    pair=pos["pair"]; direction=pos["direction"]; g=completed_market(pair)
    f=d.build_features(g)
    if direction=="long":
        sig=f.price20_cross_down & f.di_spread_down3
        reached50 = g.high.astype(float) >= float(pos["reference_entry_price"]) + 50*d.PIP[pair]
    else:
        sig=f.price20_cross_up & f.di_spread_up3
        reached50 = g.low.astype(float) <= float(pos["reference_entry_price"]) - 50*d.PIP[pair]
    entry_ts=pd.Timestamp(pos["entry_timestamp"])
    after=g.timestamp>entry_ts
    target_hits=g.index[after & reached50]
    target_i=int(target_hits[0]) if len(target_hits) else None
    if target_i is not None:
        candidates=g.index[(g.index>target_i) & sig.fillna(False)]
        if len(candidates):
            i=int(candidates[0])
            return {
                **pos, "state":"EXIT_TRIGGERED",
                "plus50_timestamp":pd.Timestamp(g.timestamp.iloc[target_i]).isoformat(),
                "exit_signal_timestamp":pd.Timestamp(g.timestamp.iloc[i]).isoformat(),
                "exit_signal_price":float(g.close.iloc[i]),
                "exit_reason":"price20_cross_down+di_spread_down3" if direction=="long" else "price20_cross_up+di_spread_up3",
                "latest_completed_h4":pd.Timestamp(g.timestamp.iloc[-1]).isoformat(),
                "latest_close":float(g.close.iloc[-1])
            }
    i=len(g)-1
    return {
        **pos, "state":"HOLD_NO_EXIT",
        "exit_signal_timestamp":"",
        "exit_signal_price":"",
        "exit_reason":"",
        "latest_completed_h4":pd.Timestamp(g.timestamp.iloc[i]).isoformat(),
        "latest_close":float(g.close.iloc[i])
    }

def main():
    cfg=json.loads(Path("config/active_positions.json").read_text())
    rows=[evaluate(p) for p in cfg["positions"] if p.get("status")=="open"]
    out=pd.DataFrame(rows)
    Path("reports").mkdir(exist_ok=True)
    out.to_csv("reports/current_position_exit_state.csv",index=False)
    alerts=out[out.state=="EXIT_TRIGGERED"].copy()
    if len(alerts):
        alerts["notification_id"]=alerts.apply(lambda r:f"{r['id']}|{r['exit_signal_timestamp']}",axis=1)
    alerts.to_csv("reports/current_exit_alerts.csv",index=False)
    print(out.to_string(index=False))
    print("EXIT ALERTS")
    print(alerts.to_string(index=False) if len(alerts) else "none")

if __name__=="__main__":
    main()
