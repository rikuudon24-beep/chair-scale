#!/usr/bin/env python3
"""Validate historically mined H1 win-rate filters on chronological splits.

The mining pass may inspect the full historical sample. This gate does not
re-optimize parameters: it evaluates a fixed shortlist with the exact final
entry/exit simulator at 3p and 5p costs across discovery/validation/OOS.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/"research/h1/results/datasets"
OUT=ROOT/"research/h1/results"

SHORTLIST={
 "USDJPY":[("bb_pct<=0.5 + utc_00_06",["bb_pct<=0.5","utc_00_06"])],
 "EURJPY":[("dist_ema20<=0 + body_range>=0.6",["dist_ema20<=0","body_range>=0.6"]),
           ("rsi<=45 + body_range>=0.6",["rsi<=45","body_range>=0.6"]),
           ("bb_pct<=0.5 + body_range>=0.6",["bb_pct<=0.5","body_range>=0.6"])],
 "GBPJPY":[("ema20_slope>=0",["ema20_slope>=0"])],
 "USDCHF":[("adx>=25 + rsi>=50",["adx>=25","rsi>=50"]),
           ("adx>=25 + ema20_slope>=0",["adx>=25","ema20_slope>=0"])],
 "AUDNZD":[("adx>=20 + ema50_slope>=0",["adx>=20","ema50_slope>=0"]),
           ("adx>=25 + ema50_slope>=0",["adx>=25","ema50_slope>=0"])],
}
BASE={
 "USDJPY":("pullback_reversal_rsi","break_signal_high",40,40,72),
 "EURJPY":("pullback_reversal_rsi","next_open",100,40,72),
 "GBPJPY":("pullback_reversal","break_signal_high",40,50,24),
 "USDCHF":("pullback_reversal_rsi","confirm_1bar",40,40,48),
 "AUDNZD":("pullback_reversal","next_open",60,75,72),
}
def pip(pair): return .01 if "JPY" in pair else .0001
def base_mask(d,s):
 if s=="pullback_reversal": return d.trend_down & (d.h4_close>d.h4_open) & (d.d1_close>d.d1_open)
 return d.trend_down & (d.d1_close>d.d1_open) & ((d.rsi14-d.rsi14.shift(6))>3)
def filters(d):
 h=d.index.hour
 return {
  "bb_pct<=0.5":d.bb_pct<=.5,"utc_00_06":pd.Series(h<6,index=d.index),
  "dist_ema20<=0":d.dist_ema20_atr<=0,"body_range>=0.6":d.body_range>=.6,
  "rsi<=45":d.rsi14<=45,"adx>=25":d.adx14>=25,"rsi>=50":d.rsi14>=50,
  "ema20_slope>=0":d.ema20_slope>=0,"ema50_slope>=0":d.ema50_slope>=0,
 }
def sim(d,m,pair,entry_mode,tp,sl,h,cost):
 ps=pip(pair); hi=d.high.to_numpy(); lo=d.low.to_numpy(); cl=d.close.to_numpy(); op=d.open.to_numpy()
 raw=[]
 for sig in np.flatnonzero(m.fillna(False).to_numpy()):
  if sig+2>=len(d): continue
  if entry_mode=="next_open": raw.append((sig+1,float(op[sig+1])))
  elif entry_mode=="break_signal_high":
   level=float(hi[sig])+ps*.5
   if hi[sig+1]>=level: raw.append((sig+1,max(float(op[sig+1]),level)))
  elif entry_mode=="confirm_1bar" and cl[sig+1]>hi[sig]: raw.append((sig+2,float(op[sig+2])))
 chosen=[]; last=-1
 for st,e in raw:
  if st<=last: continue
  chosen.append((st,e)); last=st+h
 rs=[]
 for st,e in chosen:
  end=min(st+h,len(d)-1); r=None
  for j in range(st,end+1):
   ht=hi[j]>=e+tp*ps; hs=lo[j]<=e-sl*ps
   if ht and hs: r=-sl; break
   if ht: r=tp; break
   if hs: r=-sl; break
  if r is None: r=(cl[end]-e)/ps
  rs.append(r-cost)
 if not rs:return None
 z=np.array(rs); win=float((z>0).mean()); gp=z[z>0].sum(); gl=-z[z<0].sum()
 return {"n":len(z),"win":win,"pf":float(gp/gl) if gl else np.inf,"exp":float(z.mean()),"net":float(z.sum())}
def fmt(x):
 return "N/A" if x is None else f"N={x['n']} Win={x['win']:.3f} PF={x['pf']:.3f} ExpR={x['exp']:.3f} NetR={x['net']:.2f}"
rows=[]; report=["# H1 mined filter chronological validation","","Fixed shortlist from historical mining. Exact final entry/exit mechanics. Costs tested at 3p and 5p."]
for pair,(structure,entry,tp,sl,h) in BASE.items():
 fp=DATA/f"{pair.lower()}.parquet"
 if not fp.exists(): continue
 d=pd.read_parquet(fp).sort_index(); n=len(d); cuts=[int(n*.6),int(n*.8)]
 parts=[("discovery",d.iloc[:cuts[0]]),("validation",d.iloc[cuts[0]:cuts[1]]),("oos",d.iloc[cuts[1]:])]
 report += [f"","## {pair}"]
 fdict=filters(d)
 for name,fs in [("BASE",[])]+SHORTLIST[pair]:
  for cost in (3.0,5.0):
   vals=[]
   for split,part in parts:
    bm=base_mask(part,structure)
    m=bm.copy()
    for f in fs: m &= filters(part)[f].fillna(False)
    q=sim(part,m,pair,entry,tp,sl,h,cost); vals.append(q)
    rows.append({"pair":pair,"candidate":name,"cost_pips":cost,"split":split,**({k:v for k,v in q.items()} if q else {"n":0,"win":np.nan,"pf":np.nan,"exp":np.nan,"net":0})})
   report.append(f"- {name} @ {cost:.0f}p: " + " | ".join(f"{s}: {fmt(q)}" for s,q in zip(["D","V","O"],vals)))
df=pd.DataFrame(rows); df.to_csv(OUT/"H1_MINED_FILTER_VALIDATION.csv",index=False)
(OUT/"H1_MINED_FILTER_VALIDATION.md").write_text("\n".join(report)+"\n",encoding="utf-8")
print("\n".join(report))
