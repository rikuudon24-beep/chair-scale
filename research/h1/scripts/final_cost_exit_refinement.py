#!/usr/bin/env python3
"""Cost-aware H1 entry/exit refinement for the six already-routed pairs."""
from pathlib import Path
import numpy as np, pandas as pd
ROOT=Path(__file__).resolve().parents[3]; DATA=ROOT/"research/h1/results/datasets"; OUT=ROOT/"research/h1/results"
CANDS={"usdjpy":"pullback_reversal_rsi","eurjpy":"pullback_reversal_rsi","gbpjpy":"pullback_reversal","usdchf":"pullback_reversal_rsi","audusd":"pullback_reversal_rsi","audnzd":"pullback_reversal"}
STRUCT={"pullback_reversal":"trend_down & h4_bull & d1_bull","pullback_reversal_rsi":"trend_down & d1_bull & rsi_up6"}
ENTRIES=["next_open","break_signal_high","confirm_1bar"]; TP=[40,50,60,75,100,125]; SL=[40,50,60,75,100,125]; H=[24,48,72]; COST=3.0
def ps(pair): return .01 if "jpy" in pair else .0001
def split(x):
 n=len(x); a=int(n*.6); b=int(n*.2); return x.iloc[:a],x.iloc[a:a+b],x.iloc[a+b:]
def mask(x,name):
 d={"trend_down":x.trend_down,"d1_bull":x.d1_close>x.d1_open,"h4_bull":x.h4_close>x.h4_open,"rsi_up6":x.rsi14-x.rsi14.shift(6)>3}
 m=pd.Series(True,index=x.index)
 for q in STRUCT[name].split("&"): m &= d[q.strip()].fillna(False)
 return m
def entries(x,idx,pair,v):
 hi=x.high.to_numpy(); cl=x.close.to_numpy(); op=x.open.to_numpy(); p=ps(pair); out=[]
 for i in idx:
  if i+2>=len(x): continue
  if v=="next_open": out.append((i+1,op[i+1]))
  elif v=="break_signal_high":
   level=hi[i]+p*.5
   if hi[i+1]>=level: out.append((i+1,max(op[i+1],level)))
  elif v=="confirm_1bar" and cl[i+1]>hi[i]: out.append((i+2,op[i+2]))
 return out
def sim(x,pair,m,v,tp,sl,h):
 p=ps(pair); raw=entries(x,np.flatnonzero(m.fillna(False).to_numpy()),pair,v); op=x.open.to_numpy(); hi=x.high.to_numpy(); lo=x.low.to_numpy(); cl=x.close.to_numpy(); chosen=[]; last=-1
 for i,e in raw:
  if i<=last: continue
  chosen.append((i,e)); last=i+h
 rr=[]; kinds=[]
 for i,e in chosen:
  th=e+tp*p; st=e-sl*p; end=min(i+h,len(x)-1); res=None
  for j in range(i,end+1):
   ht=hi[j]>=th; hs=lo[j]<=st
   if ht and hs: res=-1.; kinds.append("SL"); break
   if ht: res=tp/sl; kinds.append("TP"); break
   if hs: res=-1.; kinds.append("SL"); break
  else: res=(cl[end]-e)/p/sl; kinds.append("TIME")
  res-=COST/sl; rr.append(res)
 if not rr:return None
 z=np.array(rr); gp=z[z>0].sum(); gl=-z[z<0].sum()
 return len(z),float((z>0).mean()),float(gp/gl) if gl else np.inf,float(z.mean()),float(z.sum()),kinds.count("TP"),kinds.count("SL"),kinds.count("TIME")
def main():
 rows=[]
 for pair,name in CANDS.items():
  fp=DATA/f"{pair}.parquet"
  if not fp.exists(): continue
  x=pd.read_parquet(fp).sort_index()
  for sn,part in zip(["discovery","validation","oos"],split(x)):
   m=mask(part,name)
   for v in ENTRIES:
    for tp in TP:
     for sl in SL:
      for h in H:
       q=sim(part,pair,m,v,tp,sl,h)
       if q: rows.append({"pair":pair,"structure":name,"split":sn,"entry":v,"tp":tp,"sl":sl,"horizon":h,"trades":q[0],"win_rate":q[1],"pf":q[2],"expectancy_R":q[3],"net_R":q[4],"tp_count":q[5],"sl_count":q[6],"time_count":q[7]})
 df=pd.DataFrame(rows); df.to_csv(OUT/"H1_FINAL_COST_EXIT_GRID.csv",index=False); selected=[]
 for pair in CANDS:
  d=df[(df.pair==pair)&(df.split=="discovery")].query("trades>=20 and pf>1 and expectancy_R>0")
  v=df[(df.pair==pair)&(df.split=="validation")]
  if d.empty or v.empty: continue
  keys=["entry","tp","sl","horizon"]; c=v.merge(d[keys],on=keys,how="inner").query("trades>=15")
  if c.empty: continue
  c=c.sort_values(["expectancy_R","pf","trades"],ascending=[False,False,False]).iloc[0]
  o=df[(df.pair==pair)&(df.split=="oos")&(df.entry==c.entry)&(df.tp==c.tp)&(df.sl==c.sl)&(df.horizon==c.horizon)]
  for _,r in o.iterrows(): selected.append({"pair":pair,"structure":c.structure,"entry":c.entry,"tp":int(c.tp),"sl":int(c.sl),"horizon":int(c.horizon),"validation_trades":int(c.trades),"validation_pf":float(c.pf),"validation_expR":float(c.expectancy_R),"oos_trades":int(r.trades),"oos_win":float(r.win_rate),"oos_pf":float(r.pf),"oos_expR":float(r.expectancy_R),"oos_netR":float(r.net_R),"oos_tp":int(r.tp_count),"oos_sl":int(r.sl_count),"oos_time":int(r.time_count)})
 out=pd.DataFrame(selected); out.to_csv(OUT/"H1_FINAL_COST_EXIT_SELECTED.csv",index=False)
 lines=["# H1 final cost/exit refinement","","Assumption: 3-pip round-trip cost per trade; TIME exits settle at the horizon-bar close. Validation selects entry/TP/SL/horizon; OOS is evaluated after freezing the rule. Because the six pairs were previously routed using OOS evidence, this is not a pristine untouched holdout.","","|Pair|Entry|TP|SL|H|Val n|Val PF|Val ExpR|OOS n|OOS Win|OOS PF|OOS ExpR|OOS NetR|TP/SL/TIME|","|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
 for _,r in out.iterrows(): lines.append(f"|{r.pair}|{r.entry}|{int(r.tp)}|{int(r.sl)}|{int(r.horizon)}|{int(r.validation_trades)}|{r.validation_pf:.3f}|{r.validation_expR:.3f}|{int(r.oos_trades)}|{r.oos_win:.3f}|{r.oos_pf:.3f}|{r.oos_expR:.3f}|{r.oos_netR:.2f}|{int(r.oos_tp)}/{int(r.oos_sl)}/{int(r.oos_time)}|")
 (OUT/"H1_FINAL_COST_EXIT_SELECTED.md").write_text("\n".join(lines)+"\n"); print(out.to_string(index=False))
if __name__=="__main__": main()
