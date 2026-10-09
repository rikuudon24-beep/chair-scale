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

def completed_market(pair):
    g=d.load_market("h4",pair).sort_values("timestamp").reset_index(drop=True)
    if g.empty:
        raise RuntimeError(f"{pair}: H4 market data is empty; exit state is UNKNOWN")
    now=pd.Timestamp.now(tz="UTC")
    latest_ts=pd.to_datetime(g.timestamp.iloc[-1],utc=True)

    # Never label an evaluation on stale data as HOLD_NO_EXIT.
    # Allow the normal Friday close/weekend gap.
    weekday=now.weekday()  # Monday=0 ... Sunday=6
    market_closed=(weekday==4 and now.hour>=21) or weekday==5 or (weekday==6 and now.hour<21)
    if not market_closed:
        expected_latest=now.floor("4h")-H4
        lag_hours=(expected_latest-latest_ts).total_seconds()/3600
        if lag_hours>8:
            raise RuntimeError(
                f"{pair}: H4 market data stale; latest={latest_ts.isoformat()}, "
                f"expected_at_least={expected_latest.isoformat()}, lag={lag_hours:.1f}h. "
                "Exit state is UNKNOWN; do not treat this as HOLD_NO_EXIT."
            )

    cutoff=now.floor("4h")-H4
    closed=g[pd.to_datetime(g.timestamp,utc=True)<=cutoff].copy().reset_index(drop=True)
    if closed.empty:
        raise RuntimeError(f"{pair}: no completed H4 candles available; exit state is UNKNOWN")
    return closed

def evaluate(pos):
    pair=pos["pair"]; direction=pos["direction"]; g=completed_market(pair)
    f=d.build_features(g)
    if direction=="long":
        sig=f.price20_cross_down & f.di_spread_down3
        reached50 = g.high.astype(float) >= float(pos["reference_entry_price"]) + 50*0.0001
    else:
        sig=f.price20_cross_up & f.di_spread_up3
        reached50 = g.low.astype(float) <= float(pos["reference_entry_price"]) - 50*0.0001
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
