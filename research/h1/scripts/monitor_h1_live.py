#!/usr/bin/env python3
"""Live H1 alert monitor for the six routed research candidates.

Backtest-matched conditions:
- trend_down = EMA20 < EMA50 < EMA200 on H1
- pullback_reversal = trend_down & H4 bullish candle & D1 bullish candle
- pullback_reversal_rsi = trend_down & D1 bullish candle & RSI14 change over 6 H1 bars > 3
- signal is evaluated only on a completed H1 candle
- entry is the next H1 open
- exits are fixed pair-specific TP/SL; same-candle TP+SL => SL first
This is a research/alert monitor, not an execution engine.
"""
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[3]
PAIRS={
    "usdjpy": ("pullback_reversal_rsi",50,75),
    "eurjpy": ("pullback_reversal_rsi",50,75),
    "gbpjpy": ("pullback_reversal",75,50),
    "usdchf": ("pullback_reversal_rsi",50,50),
    "audusd": ("pullback_reversal_rsi",50,75),
    "audnzd": ("pullback_reversal",50,50),
}
STATE=ROOT/"reports/h1_live_positions.csv"
ALERTS=ROOT/"reports/h1_live_alerts.csv"
PIP=lambda pair: 0.01 if "jpy" in pair else 0.0001
POSCOL=["pair","direction","signal_time","entry_time","entry_price","tp","sl","status","last_checked"]
ALCOL=["alert_id","kind","pair","direction","signal_time","entry_time","price","tp","sl","message"]

def load(pair,tf):
    fp=ROOT/"data/market"/tf/f"{pair}.csv"
    if not fp.exists(): raise RuntimeError(f"missing {tf} data: {pair}")
    x=pd.read_csv(fp)
    x["timestamp"]=pd.to_datetime(x.timestamp,unit="ms",utc=True)
    x=x.drop_duplicates("timestamp").sort_values("timestamp").set_index("timestamp")
    for c in ["open","high","low","close"]: x[c]=pd.to_numeric(x[c],errors="coerce")
    return x.dropna(subset=["open","high","low","close"])

def rsi14(c):
    d=c.diff(); up=d.clip(lower=0); dn=-d.clip(upper=0)
    rs=up.ewm(alpha=1/14,adjust=False).mean()/dn.ewm(alpha=1/14,adjust=False).mean().replace(0,pd.NA)
    return 100-(100/(1+rs))

def completed_h1(pair):
    raw=load(pair,"h1")
    cutoff=pd.Timestamp.now(tz="UTC").floor("h")-pd.Timedelta(hours=1)
    h=raw[raw.index<=cutoff].copy()
    if len(h)<210: raise RuntimeError(f"insufficient completed H1 candles: {pair}")
    return raw,h

def prior_completed_context(htf, signal_ts):
    # Matches build_dataset.py: HTF series is shifted one bar before as-of merge.
    prior=htf[htf.index<=signal_ts]
    if len(prior)<2: return None
    row=prior.iloc[-2]
    return float(row.open),float(row.close)

def evaluate(pair):
    raw,h=completed_h1(pair)
    h4=load(pair,"h4"); d1=load(pair,"d1")
    c=h.close
    e20=c.ewm(span=20,adjust=False).mean()
    e50=c.ewm(span=50,adjust=False).mean()
    e200=c.ewm(span=200,adjust=False).mean()
    r=rsi14(c)
    i=len(h)-1; ts=h.index[i]
    h4ctx=prior_completed_context(h4,ts); d1ctx=prior_completed_context(d1,ts)
    if h4ctx is None or d1ctx is None: raise RuntimeError(f"missing MTF context: {pair}")
    h4bull=h4ctx[1]>h4ctx[0]; d1bull=d1ctx[1]>d1ctx[0]
    trend=bool(e20.iloc[i]<e50.iloc[i] and e50.iloc[i]<e200.iloc[i])
    rsiup=bool(pd.notna(r.iloc[i]) and pd.notna(r.iloc[i-6]) and (r.iloc[i]-r.iloc[i-6]>3))
    rule,tp,sl=PAIRS[pair]
    signal=bool(trend and d1bull and (h4bull if rule=="pullback_reversal" else rsiup))
    next_ts=ts+pd.Timedelta(hours=1)
    entry_price=float(raw.loc[next_ts,"open"]) if next_ts in raw.index else None
    return {
        "pair":pair,"rule":rule,"tp_pips":tp,"sl_pips":sl,"signal":signal,
        "signal_time":ts,"signal_close":float(h.close.iloc[i]),
        "entry_time":next_ts,"entry_price":entry_price,
        "latest_high":float(h.high.iloc[i]),"latest_low":float(h.low.iloc[i]),
        "latest_close":float(h.close.iloc[i]),
        "trend_down":trend,"h4_bull":h4bull,"d1_bull":d1bull,"rsi_up6":rsiup,
    }

def seen(alerts,aid):
    return len(alerts) and bool((alerts.alert_id==aid).any())

def main():
    STATE.parent.mkdir(parents=True,exist_ok=True)
    pos=pd.read_csv(STATE) if STATE.exists() else pd.DataFrame(columns=POSCOL)
    alerts=pd.read_csv(ALERTS) if ALERTS.exists() else pd.DataFrame(columns=ALCOL)
    new=[]; newpos=[]; touched=set()

    for pair in PAIRS:
        r=evaluate(pair); touched.add(pair)
        active=pos[(pos.pair==pair)&(pos.status.isin(["OPEN","PENDING"]))]

        if len(active):
            p=active.iloc[-1].copy()
            if p.status=="PENDING" and r["entry_price"] is not None:
                p.entry_price=float(r["entry_price"])
                p.entry_time=r["entry_time"].isoformat()
                p.status="OPEN"

            if p.status=="OPEN":
                hit_tp=r["latest_high"]>=float(p.tp)
                hit_sl=r["latest_low"]<=float(p.sl)
                if hit_tp or hit_sl:
                    kind="EXIT_SL" if hit_sl else "EXIT_TP"
                    price=float(p.sl if hit_sl else p.tp)
                    aid=f"{kind}|{pair}|{r['signal_time'].isoformat()}"
                    if not seen(alerts,aid):
                        new.append([
                            aid,kind,pair,p.direction,r["signal_time"].isoformat(),
                            p.entry_time,price,float(p.tp),float(p.sl),
                            f"{kind}: {pair} long; research position exit at {price}."
                        ])
                    p.status="CLOSED"

            p.last_checked=r["signal_time"].isoformat()
            newpos.append(p.to_dict())
            continue

        if r["signal"]:
            entry=r["entry_price"]
            aid=f"ENTRY|{pair}|{r['signal_time'].isoformat()}"
            if not seen(alerts,aid):
                if entry is None:
                    price=r["signal_close"]; status="PENDING"
                    tp=price+r["tp_pips"]*PIP(pair); sl=price-r["sl_pips"]*PIP(pair)
                    msg=f"ENTRY: {pair} long signal confirmed at H1 close {r['signal_close']}; next H1 open not yet available. Wait for next H1 open. TP/SL must be recalculated from actual entry."
                else:
                    price=float(entry); status="OPEN"
                    tp=price+r["tp_pips"]*PIP(pair); sl=price-r["sl_pips"]*PIP(pair)
                    msg=f"ENTRY: {pair} LONG at next H1 open {price:.5f}; rule={r['rule']}; TP={tp:.5f} (+{r['tp_pips']}p); SL={sl:.5f} (-{r['sl_pips']}p)."
                new.append([
                    aid,"ENTRY",pair,"long",r["signal_time"].isoformat(),
                    r["entry_time"].isoformat(),price,tp,sl,msg
                ])
                newpos.append({
                    "pair":pair,"direction":"long",
                    "signal_time":r["signal_time"].isoformat(),
                    "entry_time":r["entry_time"].isoformat(),
                    "entry_price":price,"tp":tp,"sl":sl,
                    "status":status,"last_checked":r["signal_time"].isoformat()
                })

    for _,p in pos.iterrows():
        if p.pair not in touched:
            newpos.append(p.to_dict())

    pd.DataFrame(newpos,columns=POSCOL).to_csv(STATE,index=False)
    if new:
        alerts=pd.concat([alerts,pd.DataFrame(new,columns=ALCOL)],ignore_index=True)
    alerts.to_csv(ALERTS,index=False)

    print("=== H1 ROUTED MONITOR ===")
    for pair in PAIRS:
        r=evaluate(pair)
        print(pair,r["signal"],r["rule"],r["signal_time"],"entry",r["entry_price"],
              "TP",r["tp_pips"],"SL",r["sl_pips"],
              "ctx",r["h4_bull"],r["d1_bull"],r["rsi_up6"])
    print("NEW ALERTS",len(new))

if __name__=="__main__":
    main()
