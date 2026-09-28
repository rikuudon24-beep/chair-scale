#!/usr/bin/env python3
"""Recent entry-timing audit: find trigger-like candles that the state machine did not alert on.

This is deliberately diagnostic, not a new trading rule. It compares completed H4
candles from 2026 onward and flags candles where the breakout + direction filter
were true while the live state was not TRIGGERED. It then measures whether the
move subsequently reached +50 pips within 12 H4 bars.
"""
from pathlib import Path
import importlib.util
import pandas as pd

spec=importlib.util.spec_from_file_location("d","scripts/research_50pip_direct_entry.py")
d=importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
PIP={p:(0.01 if "jpy" in p else 0.0001) for p in d.PAIRS}

def run(pair):
    g=d.load_market("h4",pair).sort_values("timestamp").reset_index(drop=True)
    g["timestamp"]=pd.to_datetime(g.timestamp,utc=True)
    f=d.build_features(g)
    e20=g.close.ewm(span=20,adjust=False).mean()
    e200=g.close.ewm(span=200,adjust=False).mean()
    gc=(e20.shift(1)<=e200.shift(1))&(e20>e200)
    dc=(e20.shift(1)>=e200.shift(1))&(e20<e200)
    state="WAIT"; direction=None; touch=None; ref=None; breach=0
    out=[]
    for i in range(1,len(g)):
        ts=g.timestamp.iloc[i]
        if ts < pd.Timestamp("2026-01-01",tz="UTC"): continue
        # Process current state exactly as live engine, then test blocked candidates.
        prev_state=state; prev_dir=direction
        if state=="WAIT":
            if bool(gc.iloc[i]): direction="long"; state="SEARCH_TOUCH"; breach=0
            elif bool(dc.iloc[i]): direction="short"; state="SEARCH_TOUCH"; breach=0
        elif state=="SEARCH_TOUCH":
            if (direction=="long" and bool(dc.iloc[i])) or (direction=="short" and bool(gc.iloc[i])):
                state="WAIT"; direction=None; touch=None; ref=None; breach=0
            elif float(g.low.iloc[i])<=float(e20.iloc[i])<=float(g.high.iloc[i]):
                touch=i; ref=float(g.high.iloc[i] if direction=="long" else g.low.iloc[i]); breach=0; state="ARMED"
        elif state=="ARMED":
            if (direction=="long" and bool(dc.iloc[i])) or (direction=="short" and bool(gc.iloc[i])):
                state="WAIT"; direction=None; touch=None; ref=None; breach=0
            else:
                filt=(bool(f.sma_stack_bull.iloc[i]) and bool(f.di_strong_bull.iloc[i])
                      if direction=="long" else bool(f.strong_close_bear.iloc[i]))
                trig=(float(g.close.iloc[i])>ref if direction=="long" else float(g.close.iloc[i])<ref)
                if filt and trig:
                    state="TRIGGERED"
                else:
                    breached=((direction=="long" and float(g.close.iloc[i])<=float(g.low.iloc[touch]))
                              or (direction=="short" and float(g.close.iloc[i])>=float(g.high.iloc[touch])))
                    breach=breach+1 if breached else 0
                    if breach>=2:
                        state="WAIT"; direction=None; touch=None; ref=None; breach=0
        elif state=="TRIGGERED":
            if i < len(g)-1:
                state="WAIT"; direction=None; touch=None; ref=None; breach=0
        # Diagnostic: independent trigger-like condition when engine did not trigger.
        bull=(float(g.close.iloc[i])>ref if direction=="long" and ref is not None else False)
        bear=(float(g.close.iloc[i])<ref if direction=="short" and ref is not None else False)
        bullf=bool(f.sma_stack_bull.iloc[i]) and bool(f.di_strong_bull.iloc[i])
        bearf=bool(f.strong_close_bear.iloc[i])
        blocked=((direction=="long" and bull and bullf and state!="TRIGGERED")
                 or (direction=="short" and bear and bearf and state!="TRIGGERED"))
        if blocked:
            entry=float(g.close.iloc[i]); pip=PIP[pair]
            if direction=="long":
                mfe=(float(g.high.iloc[min(i+12,len(g)-1):].max())-entry)/pip
                target=mfe>=50
            else:
                mfe=(entry-float(g.low.iloc[min(i+12,len(g)-1):].min()))/pip
                target=mfe>=50
            out.append({"pair":pair,"timestamp":ts.isoformat(),"direction":direction,
                        "state_after_processing":state,"reason":"trigger-like candle blocked",
                        "close":entry,"mfe_12bars_pips":round(mfe,1),"reached_plus50":target})
    return pd.DataFrame(out)

def main():
    frames=[run(p) for p in d.PAIRS]
    out=pd.concat([x for x in frames if len(x)],ignore_index=True) if any(len(x) for x in frames) else pd.DataFrame()
    Path("reports").mkdir(exist_ok=True)
    out.to_csv("reports/entry_timing_missed_signals.csv",index=False)
    if len(out):
        s=out.groupby(["direction","reached_plus50"]).size().reset_index(name="count")
    else:
        s=pd.DataFrame(columns=["direction","reached_plus50","count"])
    s.to_csv("reports/entry_timing_missed_summary.csv",index=False)
    print("=== BLOCKED TRIGGER-LIKE CANDIDATES ===")
    print(out.to_string(index=False) if len(out) else "none")
    print("\n=== SUMMARY ===")
    print(s.to_string(index=False) if len(s) else "none")
if __name__=="__main__": main()
