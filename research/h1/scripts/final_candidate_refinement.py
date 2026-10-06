#!/usr/bin/env python3
"""Final-stage H1 candidate refinement: entry timing + exit grid.

Selection protocol:
- Candidate structure is frozen from the routing matrix.
- Discovery is used as a screen.
- Validation selects entry/exit/horizon among survivors.
- OOS is evaluated only after the rule is frozen.
- Signal is always known at a completed H1 close.
- Entries are causal: next-open, next-bar high break, or one-bar close confirmation.
- Same-bar TP/SL resolves conservatively to SL.
"""
from pathlib import Path
import numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/"research/h1/results/datasets"
OUT=ROOT/"research/h1/results"

CANDS={
 "usdjpy":("pullback_reversal_rsi",50,75),
 "eurjpy":("pullback_reversal_rsi",50,75),
 "gbpjpy":("pullback_reversal",75,50),
 "usdchf":("pullback_reversal_rsi",50,50),
 "audusd":("pullback_reversal_rsi",50,75),
 "audnzd":("pullback_reversal",50,50),
}
STRUCT={
 "pullback_reversal":"trend_down & h4_bull & d1_bull",
 "pullback_reversal_rsi":"trend_down & d1_bull & rsi_up6",
}
ENTRIES=["next_open","break_signal_high","confirm_1bar"]
TP=[40,50,60,75,100,125]
SL=[40,50,60,75,100,125]
H=[24,48,72]

def ps(pair): return .01 if "jpy" in pair else .0001

def split(x):
 n=len(x); a=int(n*.6); b=int(n*.2)
 return x.iloc[:a],x.iloc[a:a+b],x.iloc[a+b:]

def signal_mask(x, name):
 aa={
  "trend_down":x.trend_down,
  "d1_bull":x.d1_close>x.d1_open,
  "h4_bull":x.h4_close>x.h4_open,
  "rsi_up6":x.rsi14-x.rsi14.shift(6)>3,
 }
 m=pd.Series(True,index=x.index)
 for q in STRUCT[name].split("&"): m &= aa[q.strip()].fillna(False)
 return m

def entries(x, idx, pair, variant):
 hi=x.high.to_numpy(); cl=x.close.to_numpy(); op=x.open.to_numpy()
 p=ps(pair); out=[]
 for i in idx:
  if i+2>=len(x): continue
  if variant=="next_open":
   out.append((i+1,op[i+1]))
  elif variant=="break_signal_high":
   level=hi[i]+p*0.5
   if hi[i+1]>=level:
    out.append((i+1,max(op[i+1],level)))
  elif variant=="confirm_1bar":
   if cl[i+1]>hi[i]:
    out.append((i+2,op[i+2]))
 return out

def simulate(x,pair,mask,variant,tp,sl,horizon):
 p=ps(pair); idx=np.flatnonzero(mask.fillna(False).to_numpy())
 raw=entries(x,idx,pair,variant)
 op=x.open.to_numpy(); hi=x.high.to_numpy(); lo=x.low.to_numpy()
 chosen=[]; last=-1
 for sig,entry in raw:
  if sig<=last: continue
  chosen.append((sig,entry)); last=sig+horizon
 rr=[]
 for i,entry in chosen:
  th=entry+tp*p; st=entry-sl*p
  r=0.0
  for j in range(i,min(i+horizon+1,len(x))):
   ht=hi[j]>=th; hs=lo[j]<=st
   if ht and hs: r=-1.0; break
   if ht: r=tp/sl; break
   if hs: r=-1.0; break
  rr.append(r)
 if not rr:return None
 z=np.array(rr); wins=z>0; gp=z[z>0].sum(); gl=-z[z<0].sum()
 return len(z),float(wins.mean()),float(gp/gl) if gl else np.inf,float(z.mean()),float(z.sum())

def main():
 rows=[]
 for pair,(name,base_tp,base_sl) in CANDS.items():
  fp=DATA/f"{pair}.parquet"
  if not fp.exists(): continue
  x=pd.read_parquet(fp).sort_index()
  parts=split(x)
  for sn,part in zip(["discovery","validation","oos"],parts):
   m=signal_mask(part,name)
   for ev in ENTRIES:
    for tp in TP:
     for sl in SL:
      for h in H:
       q=simulate(part,pair,m,ev,tp,sl,h)
       if q:
        rows.append({"pair":pair,"structure":name,"split":sn,"entry":ev,"tp":tp,"sl":sl,"horizon":h,
                     "trades":q[0],"win_rate":q[1],"pf":q[2],"expectancy_R":q[3],"net_R":q[4]})
 df=pd.DataFrame(rows)
 df.to_csv(OUT/"H1_FINAL_REFINEMENT_GRID.csv",index=False)
 # Screen on discovery, select on validation. Require >=20 discovery and validation trades,
 # positive discovery expectancy and PF>1; then maximize validation expectancy, tie-break PF/trades.
 selected=[]
 for pair in CANDS:
  z=df[(df.pair==pair)&(df.split=="discovery")].copy()
  z=z[(z.trades>=20)&(z.pf>1)&(z.expectancy_R>0)]
  v=df[(df.pair==pair)&(df.split=="validation")].copy()
  if z.empty or v.empty: continue
  keys=["entry","tp","sl","horizon"]
  cand=v.merge(z[keys],on=keys,how="inner")
  cand=cand[(cand.trades>=15)]
  if cand.empty: continue
  cand=cand.sort_values(["expectancy_R","pf","trades"],ascending=[False,False,False]).iloc[0]
  o=df[(df.pair==pair)&(df.split=="oos")&
       (df.entry==cand.entry)&(df.tp==cand.tp)&(df.sl==cand.sl)&(df.horizon==cand.horizon)]
  for _,r in o.iterrows():
   selected.append({"pair":pair,"structure":cand.structure,"entry":cand.entry,"tp":int(cand.tp),
                    "sl":int(cand.sl),"horizon":int(cand.horizon),
                    "validation_trades":int(cand.trades),"validation_pf":float(cand.pf),
                    "validation_expR":float(cand.expectancy_R),
                    "oos_trades":int(r.trades),"oos_win":float(r.win_rate),
                    "oos_pf":float(r.pf),"oos_expR":float(r.expectancy_R),"oos_netR":float(r.net_R)})
 out=pd.DataFrame(selected)
 out.to_csv(OUT/"H1_FINAL_REFINEMENT_SELECTED.csv",index=False)
 lines=["# H1 final refinement — entry/exit selection","","Protocol: discovery screens; validation selects; OOS is evaluated after freezing the rule. This does not erase the earlier routing-stage OOS usage; therefore OOS here is evidence, not a pristine untouched final holdout.","",
        "|Pair|Structure|Entry|TP|SL|H|Val n|Val PF|Val ExpR|OOS n|OOS Win|OOS PF|OOS ExpR|OOS NetR|",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
 for _,r in out.iterrows():
  lines.append(f"|{r.pair}|{r.structure}|{r.entry}|{int(r.tp)}|{int(r.sl)}|{int(r.horizon)}|{int(r.validation_trades)}|{r.validation_pf:.3f}|{r.validation_expR:.3f}|{int(r.oos_trades)}|{r.oos_win:.3f}|{r.oos_pf:.3f}|{r.oos_expR:.3f}|{r.oos_netR:.2f}|")
 (OUT/"H1_FINAL_REFINEMENT_SELECTED.md").write_text("\n".join(lines)+"\n")
 print(out.to_string(index=False))

if __name__=="__main__": main()
