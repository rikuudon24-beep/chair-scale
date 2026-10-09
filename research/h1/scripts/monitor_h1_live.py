#!/usr/bin/env python3
"""Frozen H1 v1 alert monitor. Research/alert only; never sends broker orders."""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
PAIRS={
    "eurjpy":{"structure":"eurjpy_v1","entry":"next_open","tp":100,"sl":40,"horizon":72},
    "usdchf":{"structure":"usdchf_v1","entry":"confirm_1bar","tp":40,"sl":40,"horizon":48},
    "audnzd":{"structure":"audnzd_v1","entry":"next_open","tp":60,"sl":75,"horizon":72},
}
STATE=ROOT/"reports/h1_live_positions.csv"; ALERTS=ROOT/"reports/h1_live_alerts.csv"
POSCOL=["pair","direction","signal_time","entry_time","entry_price","tp","sl","horizon","status","last_checked"]
ALCOL=["alert_id","kind","pair","direction","signal_time","entry_time","price","tp","sl","message"]

def pip(pair): return .01 if "jpy" in pair else .0001

def load(pair,tf):
    fp=ROOT/"data/market"/tf/f"{pair}.csv"
    if not fp.exists(): raise RuntimeError(f"missing {tf} data: {pair}")
    x=pd.read_csv(fp); x["timestamp"]=pd.to_datetime(x.timestamp,unit="ms",utc=True)
    x=x.drop_duplicates("timestamp").sort_values("timestamp").set_index("timestamp")
    for c in ["open","high","low","close"]: x[c]=pd.to_numeric(x[c],errors="coerce")
    return x.dropna(subset=["open","high","low","close"])

def rsi(c):
    d=c.diff(); up=d.clip(lower=0); dn=-d.clip(upper=0)
    au=up.ewm(alpha=1/14,adjust=False).mean(); ad=dn.ewm(alpha=1/14,adjust=False).mean()
    rs=au/ad.replace(0,np.nan); return 100-(100/(1+rs))

def adx14(x):
    hi=x.high; lo=x.low; cl=x.close
    tr=pd.concat([(hi-lo),(hi-cl.shift()).abs(),(lo-cl.shift()).abs()],axis=1).max(axis=1)
    up=hi.diff(); dn=-lo.diff()
    plus=np.where((up>dn)&(up>0),up,0.0); minus=np.where((dn>up)&(dn>0),dn,0.0)
    atr=tr.ewm(alpha=1/14,adjust=False).mean()
    pdi=100*pd.Series(plus,index=x.index).ewm(alpha=1/14,adjust=False).mean()/atr
    mdi=100*pd.Series(minus,index=x.index).ewm(alpha=1/14,adjust=False).mean()/atr
    dx=100*(pdi-mdi).abs()/(pdi+mdi).replace(0,np.nan)
    return dx.ewm(alpha=1/14,adjust=False).mean()

def htf_prior(x,ts,tf):
    # HTF indexes label candle OPEN. Select the latest candle whose CLOSE is
    # no later than the H1 signal candle timestamp. Do not assume a still-forming
    # HTF candle exists in the file: aggregation may omit it early in the period.
    duration = pd.Timedelta(hours=4 if tf == "h4" else 24)
    eligible = x.index + duration <= pd.Timestamp(ts)
    q = x.loc[eligible]
    return q.iloc[-1] if not q.empty else None

def market_closed_utc(now):
    now = pd.Timestamp(now)
    if now.tzinfo is None:
        now = now.tz_localize("UTC")
    else:
        now = now.tz_convert("UTC")
    return (now.weekday()==4 and now.hour>=21) or now.weekday()==5 or (now.weekday()==6 and now.hour<21)

def expected_last_completed_h1_open(now):
    now = pd.Timestamp(now)
    if now.tzinfo is None:
        now = now.tz_localize("UTC")
    else:
        now = now.tz_convert("UTC")
    days_since_friday=(now.weekday()-4)%7
    friday=now.normalize()-pd.Timedelta(days=days_since_friday)
    return friday+pd.Timedelta(hours=20)

def validate_h1_freshness(latest, now):
    latest=pd.Timestamp(latest)
    now=pd.Timestamp(now)
    if latest.tzinfo is None: latest=latest.tz_localize("UTC")
    else: latest=latest.tz_convert("UTC")
    if now.tzinfo is None: now=now.tz_localize("UTC")
    else: now=now.tz_convert("UTC")
    cutoff=now.floor("h")-pd.Timedelta(nanoseconds=1)
    if market_closed_utc(now):
        expected=expected_last_completed_h1_open(now)
        if latest < expected-pd.Timedelta(hours=1):
            raise RuntimeError(f"stale H1 data during market closure: latest_completed={latest.isoformat()} expected_last={expected.isoformat()}")
        return
    if latest < cutoff-pd.Timedelta(hours=2):
        raise RuntimeError(f"stale H1 data during open market: latest_completed={latest.isoformat()} cutoff={cutoff.isoformat()}")

def features(pair):
    raw=load(pair,"h1")
    cutoff=pd.Timestamp.now(tz="UTC").floor("h")-pd.Timedelta(nanoseconds=1)
    h=raw[raw.index<=cutoff].copy()
    if len(h)<210: raise RuntimeError(f"insufficient completed H1 candles: {pair}")
    validate_h1_freshness(h.index[-1], pd.Timestamp.now(tz="UTC"))
    c=h.close; e20=c.ewm(span=20,adjust=False).mean(); e50=c.ewm(span=50,adjust=False).mean(); e200=c.ewm(span=200,adjust=False).mean()
    atr=(pd.concat([(h.high-h.low),(h.high-c.shift()).abs(),(h.low-c.shift()).abs()],axis=1).max(axis=1).ewm(alpha=1/14,adjust=False).mean())
    rr=rsi(c); ad=adx14(h); slope=e20.pct_change()
    i=len(h)-1; ts=h.index[i]
    h4=htf_prior(load(pair,"h4"),ts,"h4"); d1=htf_prior(load(pair,"d1"),ts,"d1")
    if h4 is None or d1 is None: raise RuntimeError(f"missing HTF context: {pair}")
    body_range=abs(h.open-h.close)/(h.high-h.low).replace(0,np.nan)
    dist=(c-e20)/atr
    base={"raw":raw,"h":h,"ts":ts,"e20":e20,"rsi":rr,"adx":ad,"slope":slope,"dist":dist,"body_range":body_range,
          "trend":bool(e20.iloc[i]<e50.iloc[i]<e200.iloc[i]),
          "h4bull":bool(h4.close>h4.open),"d1bull":bool(d1.close>d1.open),
          "rsiup6":bool(pd.notna(rr.iloc[i]) and pd.notna(rr.iloc[i-6]) and rr.iloc[i]-rr.iloc[i-6]>3)}
    return base

def signal(pair,f):
    i=len(f["h"])-1
    common=f["trend"] and f["d1bull"] and f["rsiup6"]
    if pair=="eurjpy": return common and f["dist"].iloc[i]<=0 and f["body_range"].iloc[i]>=.6
    if pair=="usdchf": return common and f["adx"].iloc[i]>=25 and f["slope"].iloc[i]>=0
    return f["trend"] and f["h4bull"] and f["d1bull"]

def seen(alerts,aid): return not alerts.empty and bool((alerts.alert_id==aid).any())

def main():
    STATE.parent.mkdir(parents=True,exist_ok=True)
    pos=pd.read_csv(STATE) if STATE.exists() else pd.DataFrame(columns=POSCOL)
    alerts=pd.read_csv(ALERTS) if ALERTS.exists() else pd.DataFrame(columns=ALCOL)
    new=[]; out=[]; touched=set()

    for pair,cfg in PAIRS.items():
        f=features(pair); h=f["h"]; raw=f["raw"]; ts=f["ts"]; touched.add(pair)
        active=pos[(pos.pair==pair)&(pos.status.isin(["OPEN","PENDING","CONFIRMING"]))]
        if len(active):
            p=active.iloc[-1].copy()
            entry_time=pd.Timestamp(p.entry_time)
            if p.status=="PENDING" and entry_time in raw.index:
                p.entry_price=float(raw.loc[entry_time,"open"]); p.tp=p.entry_price+cfg["tp"]*pip(pair); p.sl=p.entry_price-cfg["sl"]*pip(pair); p.status="OPEN"
                aid=f"ENTRY|{pair}|{p.signal_time}"
                if not seen(alerts,aid):
                    new.append([aid,"ENTRY",pair,"long",p.signal_time,p.entry_time,p.entry_price,p.tp,p.sl,f"ENTRY {pair} LONG at next H1 open {p.entry_price:.5f}; TP {p.tp:.5f}; SL {p.sl:.5f}."])
            if p.status=="CONFIRMING":
                sig=pd.Timestamp(p.signal_time)
                if ts>=sig+pd.Timedelta(hours=1):
                    conf=raw[raw.index==sig+pd.Timedelta(hours=1)]
                    if len(conf) and float(conf.close.iloc[0])>float(raw.loc[sig,"high"]):
                        et=sig+pd.Timedelta(hours=2)
                        p.entry_time=et.isoformat()
                        if et in raw.index:
                            p.entry_price=float(raw.loc[et,"open"]); p.tp=p.entry_price+cfg["tp"]*pip(pair); p.sl=p.entry_price-cfg["sl"]*pip(pair); p.status="OPEN"
                            aid=f"ENTRY|{pair}|{p.signal_time}"
                            if not seen(alerts,aid): new.append([aid,"ENTRY",pair,"long",p.signal_time,p.entry_time,p.entry_price,p.tp,p.sl,f"ENTRY {pair} LONG after 1-bar confirmation at {p.entry_price:.5f}; TP {p.tp:.5f}; SL {p.sl:.5f}."])
                        else: p.status="PENDING"
                    else: p.status="CLOSED"
            if p.status=="OPEN":
                # Process every completed H1 candle since the last checkpoint.
                # This prevents a missed scheduler run from losing an intermediate TP/SL hit.
                last_checked=pd.Timestamp(p.last_checked) if pd.notna(p.last_checked) and str(p.last_checked)!="nan" else entry_time-pd.Timedelta(hours=1)
                start=max(entry_time,last_checked+pd.Timedelta(hours=1))
                bars=h[(h.index>=start)&(h.index<=ts)]
                end=entry_time+pd.Timedelta(hours=int(p.horizon))
                for bar_ts,bar in bars.iterrows():
                    hit_tp=float(bar.high)>=float(p.tp); hit_sl=float(bar.low)<=float(p.sl)
                    kind=None; price=None
                    if hit_tp or hit_sl:
                        kind="EXIT_SL" if hit_sl else "EXIT_TP"
                        price=float(p.sl if hit_sl else p.tp)  # same-candle TP+SL => SL first
                    elif bar_ts>=end:
                        kind="EXIT_TIME"; price=float(bar.close)
                    p.last_checked=bar_ts.isoformat()
                    if kind:
                        aid=f"{kind}|{pair}|{p.signal_time}"
                        if not seen(alerts,aid):
                            new.append([aid,kind,pair,"long",p.signal_time,p.entry_time,price,float(p.tp),float(p.sl),f"{kind} {pair} LONG at {price:.5f}."])
                        p.status="CLOSED"
                        break
                if p.status=="OPEN":
                    p.last_checked=ts.isoformat()
            p.last_checked=ts.isoformat() if p.status!="CLOSED" else p.last_checked
            out.append(p.to_dict()); continue

        # Signal on the latest completed candle. next_open can be entered immediately;
        # confirm_1bar stores the signal until the following candle confirms.
        if signal(pair,f):
            cfg=PAIRS[pair]; aid=f"ENTRY|{pair}|{ts.isoformat()}"
            if not seen(alerts,aid):
                if cfg["entry"]=="next_open":
                    et=ts+pd.Timedelta(hours=1); price=float(raw.loc[et,"open"]) if et in raw.index else float(h.close.iloc[-1])
                    status="OPEN" if et in raw.index else "PENDING"
                    tp=price+cfg["tp"]*pip(pair); sl=price-cfg["sl"]*pip(pair)
                    if status=="OPEN":
                        new.append([aid,"ENTRY",pair,"long",ts.isoformat(),et.isoformat(),price,tp,sl,f"ENTRY {pair} LONG at next H1 open {price:.5f}; TP {tp:.5f}; SL {sl:.5f}."])
                    out.append({"pair":pair,"direction":"long","signal_time":ts.isoformat(),"entry_time":et.isoformat(),"entry_price":price,"tp":tp,"sl":sl,"horizon":cfg["horizon"],"status":status,"last_checked":ts.isoformat()})
                else:
                    out.append({"pair":pair,"direction":"long","signal_time":ts.isoformat(),"entry_time":(ts+pd.Timedelta(hours=2)).isoformat(),"entry_price":np.nan,"tp":np.nan,"sl":np.nan,"horizon":cfg["horizon"],"status":"CONFIRMING","last_checked":ts.isoformat()})
        else:
            pass

    # Keep closed lifecycle rows permanently in the state ledger. The alert ledger
    # is the notification audit trail; this positions ledger must also retain the
    # completed trade state instead of silently dropping it on the next hourly run.
    for _,p in pos.iterrows():
        if p.pair not in touched or p.status == "CLOSED":
            out.append(p.to_dict())
    pd.DataFrame(out,columns=POSCOL).to_csv(STATE,index=False)
    if new: alerts=pd.concat([alerts,pd.DataFrame(new,columns=ALCOL)],ignore_index=True)
    alerts.to_csv(ALERTS,index=False)
    print("=== H1 V1 MONITOR ===")
    for pair in PAIRS:
        f=features(pair); print(pair,"signal=",signal(pair,f),"time=",f["ts"],"trend=",f["trend"],"h4=",f["h4bull"],"d1=",f["d1bull"],"rsiup6=",f["rsiup6"])
    print("NEW ALERTS",len(new))

if __name__=="__main__": main()
