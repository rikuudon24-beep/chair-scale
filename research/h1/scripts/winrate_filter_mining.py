#!/usr/bin/env python3
"""Mine historical entry filters that improve the frozen H1 candidates.

This is an optimization/research pass over the existing historical sample.
It never changes the frozen candidate definition; it tests additional entry
filters and ranks them by win-rate lift while requiring positive expectancy,
PF>1 and a minimum trade count.
"""
from pathlib import Path
import itertools, json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "research/h1/results/datasets"
OUT = ROOT / "research/h1/results"

CANDIDATES = {
    "USDJPY": ("pullback_reversal_rsi", "break_signal_high", 40, 40, 72),
    "EURJPY": ("pullback_reversal_rsi", "next_open", 100, 40, 72),
    "GBPJPY": ("pullback_reversal", "break_signal_high", 40, 50, 24),
    "USDCHF": ("pullback_reversal_rsi", "confirm_1bar", 40, 40, 48),
    "AUDNZD": ("pullback_reversal", "next_open", 60, 75, 72),
}

PIP = lambda p: 0.01 if "JPY" in p else 0.0001

def base_mask(d, structure):
    if structure == "pullback_reversal":
        return d.trend_down & (d.h4_close > d.h4_open) & (d.d1_close > d.d1_open)
    return d.trend_down & (d.d1_close > d.d1_open) & (d.rsi14.diff(6) > 3)

def trade_returns(d, mask, entry_mode, tp, sl, horizon, pair):
    idx = np.flatnonzero(mask.to_numpy())
    ps = PIP(pair)
    out = []
    last_exit = -1
    for i in idx:
        if i <= last_exit or i + horizon >= len(d):
            continue
        if entry_mode == "next_open":
            entry = float(d.open.iloc[i+1]); start = i+1
        elif entry_mode == "break_signal_high":
            entry = None; start = i+1
            for j in range(i+1, min(i+2, len(d))):
                if d.close.iloc[j] > d.high.iloc[i]:
                    entry = float(d.close.iloc[j]); start = j; break
            if entry is None: continue
        else:
            entry = float(d.open.iloc[i+1]); start = i+1
        end = min(start + horizon, len(d)-1)
        ret = None; exit_i = end; reason = "TIME"
        for j in range(start, end+1):
            hi = float(d.high.iloc[j]); lo = float(d.low.iloc[j])
            if lo <= entry - sl*ps:
                ret = -sl; exit_i = j; reason = "SL"; break
            if hi >= entry + tp*ps:
                ret = tp; exit_i = j; reason = "TP"; break
        if ret is None:
            ret = (float(d.close.iloc[end]) - entry) / ps
        out.append((i, ret - 3.0, reason))
        last_exit = exit_i
    return pd.DataFrame(out, columns=["signal_i","r","reason"])

def stats(tr):
    if tr.empty: return {"n":0,"win":np.nan,"pf":np.nan,"expr":np.nan,"net":0.0}
    r=tr.r
    wins=r[r>0].sum(); losses=-r[r<0].sum()
    return {"n":len(r),"win":float((r>0).mean()),"pf":float(wins/losses) if losses else np.inf,
            "expr":float(r.mean()),"net":float(r.sum())}

def filter_defs(d):
    q={}
    q["adx>=20"]=d.adx14>=20
    q["adx>=25"]=d.adx14>=25
    q["adx>=30"]=d.adx14>=30
    q["rsi<=40"]=d.rsi14<=40
    q["rsi<=45"]=d.rsi14<=45
    q["rsi>=45"]=d.rsi14>=45
    q["rsi>=50"]=d.rsi14>=50
    q["rsi_change6>=2"]=d.rsi14.diff(6)>=2
    q["rsi_change6>=3"]=d.rsi14.diff(6)>=3
    q["atr_pct>=0.002"]=d.atr_pct>=0.002
    q["atr_pct>=0.003"]=d.atr_pct>=0.003
    q["atr_pct<=0.006"]=d.atr_pct<=0.006
    q["ema20_slope>=0"]=d.ema20_slope>=0
    q["ema20_slope>=0.001"]=d.ema20_slope>=0.001
    q["ema50_slope>=0"]=d.ema50_slope>=0
    q["macd_hist>=0"]=d.macd_hist>=0
    q["macd_hist>prev"]=d.macd_hist>d.macd_hist.shift(1)
    q["bb_pct<=0.5"]=d.bb_pct<=0.5
    q["bb_pct<=0.4"]=d.bb_pct<=0.4
    q["dist_ema20>=-0.75"]=d.dist_ema20_atr>=-0.75
    q["dist_ema20>=-0.5"]=d.dist_ema20_atr>=-0.5
    q["dist_ema20<=0"]=d.dist_ema20_atr<=0
    q["body_range>=0.4"]=d.body_range>=0.4
    q["body_range>=0.6"]=d.body_range>=0.6
    q["lower_wick>=body"]=d.lower_wick>=d.body.abs()
    q["close_above_ema20"]=d.close>=d.ema20
    q["h4_bull"]=d.h4_close>d.h4_open
    q["d1_bull"]=d.d1_close>d.d1_open
    q["w1_bull"]=d.w1_close>d.w1_open
    # UTC session filters are deliberately broad and interpretable.
    hour=d.index.hour
    q["utc_00_06"]=pd.Series((hour<6),index=d.index)
    q["utc_06_12"]=pd.Series((hour>=6)&(hour<12),index=d.index)
    q["utc_12_18"]=pd.Series((hour>=12)&(hour<18),index=d.index)
    q["utc_18_24"]=pd.Series((hour>=18),index=d.index)
    return q

rows=[]
for pair,(structure,entry,tp,sl,h) in CANDIDATES.items():
    fp=DATA/f"{pair.lower()}.parquet"
    if not fp.exists():
        continue
    d=pd.read_parquet(fp).sort_index()
    base=base_mask(d,structure).fillna(False)
    base_tr=trade_returns(d,base,entry,tp,sl,h,pair)
    b=stats(base_tr)
    rows.append({"pair":pair,"kind":"BASE","filter":"none",**b})
    defs=filter_defs(d)
    singles=[]
    for name,f in defs.items():
        m=(base & f.fillna(False))
        tr=trade_returns(d,m,entry,tp,sl,h,pair); s=stats(tr)
        if s["n"]>=15 and s["pf"]>1 and s["expr"]>0:
            s.update(pair=pair,kind="SINGLE",filter=name,win_lift=s["win"]-b["win"])
            singles.append((name,f,s)); rows.append(s)
    # Test pairwise combinations only among useful single filters.
    for (n1,f1,s1),(n2,f2,s2) in itertools.combinations(singles,2):
        m=base & f1.fillna(False) & f2.fillna(False)
        tr=trade_returns(d,m,entry,tp,sl,h,pair); s=stats(tr)
        if s["n"]>=15 and s["pf"]>1 and s["expr"]>0 and s["win"]>=b["win"]+0.05:
            s.update(pair=pair,kind="PAIR",filter=f"{n1} + {n2}",win_lift=s["win"]-b["win"])
            rows.append(s)

res=pd.DataFrame(rows)
if res.empty:
    print("No results")
    raise SystemExit(0)
res.to_csv(OUT/"H1_WINRATE_FILTER_MINING.csv",index=False)
lines=["# H1 win-rate filter mining","",
       "Historical optimization of the existing frozen H1 candidates. Base rules are not replaced automatically.",
       "3-pip cost per trade. Minimum 15 trades; candidates require PF>1 and positive expectancy.",
       ""]
for pair in CANDIDATES:
    x=res[res.pair==pair]
    if x.empty: continue
    base=x[x.kind=="BASE"].iloc[0]
    lines += [f"## {pair}",f"Base: N={int(base.n)}, Win={base.win:.3f}, PF={base.pf:.3f}, ExpR={base.expr:.3f}"]
    top=x[x.kind!="BASE"].sort_values(["win_lift","expr"],ascending=False).head(10)
    if top.empty: lines += ["No filter passed the minimum gate.",""]; continue
    for _,r in top.iterrows():
        lines.append(f"- {r['kind']}: {r['filter']} | N={int(r.n)} Win={r.win:.3f} (+{r.win_lift:.3f}) PF={r.pf:.3f} ExpR={r.expr:.3f} Net={r.net:.1f}")
    lines.append("")
(OUT/"H1_WINRATE_FILTER_MINING.md").write_text("\n".join(lines),encoding="utf-8")
print("\n".join(lines))
