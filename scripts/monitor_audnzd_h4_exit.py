#!/usr/bin/env python3
"""AUD/NZD LONG exit-candidate monitor; completed H4 bars only, no order execution."""
import json
from pathlib import Path
import pandas as pd
import numpy as np
import importlib.util
spec=importlib.util.spec_from_file_location("features","scripts/research_50pip_direct_entry.py")
d=importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
def market_closed_utc(now):
    now = pd.Timestamp(now)
    if now.tzinfo is None:
        now = now.tz_localize("UTC")
    else:
        now = now.tz_convert("UTC")
    return (now.weekday() == 4 and now.hour >= 21) or now.weekday() == 5 or (now.weekday() == 6 and now.hour < 21)


def expected_last_completed_h4_open(now):
    now = pd.Timestamp(now)
    if now.tzinfo is None:
        now = now.tz_localize("UTC")
    else:
        now = now.tz_convert("UTC")
    days_since_friday = (now.weekday() - 4) % 7
    return now.normalize() - pd.Timedelta(days=days_since_friday) + pd.Timedelta(hours=16)


def validate_h4_freshness(latest, now):
    latest = pd.Timestamp(latest)
    now = pd.Timestamp(now)
    if latest.tzinfo is None:
        latest = latest.tz_localize("UTC")
    else:
        latest = latest.tz_convert("UTC")
    if now.tzinfo is None:
        now = now.tz_localize("UTC")
    else:
        now = now.tz_convert("UTC")
    if market_closed_utc(now):
        expected_last = expected_last_completed_h4_open(now)
        if latest < expected_last:
            raise RuntimeError(f"AUDNZD H4 data predates weekly close: latest={latest.isoformat()} expected_last={expected_last.isoformat()}; EXIT state UNKNOWN")
        print(f"[OK-CLOSED] AUDNZD H4 latest={latest.isoformat()} expected_last={expected_last.isoformat()}; weekly closure freshness rule applied")
        return
    expected = now.floor("4h") - pd.Timedelta(hours=4)
    if (expected - latest).total_seconds() > 8 * 3600:
        raise RuntimeError(f"AUDNZD H4 data stale ({latest.isoformat()}); EXIT state UNKNOWN")

def main():
    df=d.load_market("h4","audnzd")
    if len(df)<220: raise RuntimeError("AUDNZD H4 history insufficient; EXIT state UNKNOWN")
    now=pd.Timestamp.now(tz="UTC")
    # H4 candle timestamps are candle-open times; only include fully closed bars.
    expected=now.floor("4h")-pd.Timedelta(hours=4)
    closed=df[pd.to_datetime(df.timestamp,utc=True)<=expected].copy().reset_index(drop=True)
    if len(closed)<220: raise RuntimeError("Not enough completed AUDNZD H4 candles; EXIT state UNKNOWN")
    latest=pd.to_datetime(closed.timestamp.iloc[-1],utc=True)
    validate_h4_freshness(latest, now)
    f=d.build_features(closed)
    c=closed.close.astype(float); h=closed.high.astype(float); l=closed.low.astype(float)
    ema10=c.ewm(span=10,adjust=False).mean(); ema20=c.ewm(span=20,adjust=False).mean()
    macd=c.ewm(span=12,adjust=False).mean()-c.ewm(span=26,adjust=False).mean()
    macds=macd.ewm(span=9,adjust=False).mean()
    pdi=f.get("plus_di",None); mdi=f.get("minus_di",None)
    # build_features names are not assumed for DMI; calculate canonical Wilder DI here.
    tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    atr=d.rma(tr,14); up=h.diff(); dn=-l.diff()
    plus=pd.Series(np.where((up>dn)&(up>0),up,0),index=closed.index)
    minus=pd.Series(np.where((dn>up)&(dn>0),dn,0),index=closed.index)
    pdi=100*d.rma(plus,14)/atr; mdi=100*d.rma(minus,14)/atr
    spread=pdi-mdi
    swing_low=l.shift(1).rolling(10).min()
    row=len(closed)-1; prev=row-1
    reasons=[]
    if c.iloc[row]<ema20.iloc[row] and c.iloc[prev]>=ema20.iloc[prev]: reasons.append("H4 close crossed below EMA20")
    if ema10.iloc[row]<ema20.iloc[row] and ema10.iloc[prev]>=ema20.iloc[prev]: reasons.append("EMA10/20 bearish cross")
    if spread.iloc[row]<spread.iloc[row-1]<spread.iloc[row-2] and spread.iloc[row]<0: reasons.append("DI spread clearly deteriorating; -DI dominates")
    if macd.iloc[row]<macds.iloc[row] and macd.iloc[prev]>=macds.iloc[prev]: reasons.append("MACD bearish cross")
    if c.iloc[row]<swing_low.iloc[row]: reasons.append("confirmed close below prior 10-bar swing support")
    # Structure break: two consecutive lower lows and closes below prior candle lows.
    if l.iloc[row]<l.iloc[row-1]<l.iloc[row-2] and c.iloc[row]<l.iloc[row-1]: reasons.append("H4 bearish structure breakdown")
    # Require multiple independent reasons and at least one structural/EMA/support trigger.
    core=any(x.startswith(("H4 close crossed below EMA20","confirmed close below","H4 bearish structure")) for x in reasons)
    triggered=len(reasons)>=3 and core
    result={"pair":"AUD/NZD","direction":"LONG","state":"EXIT_CANDIDATE" if triggered else "NO_EXIT_CANDIDATE",
      "signal_candle_utc":latest.isoformat(),"signal_candle_jst":latest.tz_convert("Asia/Tokyo").isoformat(),
      "signal_close":float(c.iloc[row]),"reasons":"; ".join(reasons),"reason_count":len(reasons),
      "latest_close":float(c.iloc[row]),"data_status":"FRESH_CONFIRMED_H4"}
    Path("reports").mkdir(exist_ok=True)
    Path("reports/audnzd_exit_state.json").write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if triggered:
      out=Path("reports/audnzd_exit_alert.md")
      out.write_text("# FX EXIT candidate — AUD/NZD LONG\n\n"+
        f"- Confirmed H4 candle (JST): {result['signal_candle_jst']}\n- Signal close: {result['signal_close']}\n"+
        f"- Overlapping reasons ({len(reasons)}): {result['reasons']}\n\nNotification only; no order is executed.\n")
if __name__=="__main__": main()
