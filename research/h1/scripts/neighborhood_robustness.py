#!/usr/bin/env python3
"""Neighborhood robustness around the two strongest H1 candidates.
No parameter is re-selected here; this report only tests whether the frozen
candidate sits inside a locally robust region across discovery/validation/OOS.
"""
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/"research/h1/results/datasets"
OUT=ROOT/"research/h1/results"
CANDS={
 "eurjpy":("pullback_reversal_rsi","next_open",100,40,72),
 "audnzd":("pullback_reversal","next_open",75,75,72),
}
def ps(pair): return .01 if "jpy" in pair else .0001
def split(x):
 n=len(x); a=int(n*.6); b=int(n*.2)
 return x.iloc[:a],x.iloc[a:a+b],x.iloc[a+b:]
def mask(x,name):
 d={"trend_down":x.trend_down,"d1_bull":x.d1_close>x.d1_open,
    "h4_bull":x.h4_close>x.h4_open,
    "rsi_up6":x.rsi14-x.rsi14.shift(6)>3}
 rules={"pullback_reversal":"trend_down & h4_bull & d1_bull",
        "pullback_reversal_rsi":"trend_down & d1_bull & rsi_up6"}
 m=pd.Series(True,index=x.index)
 for q in rules[name].split("&"): m &= d[q.strip()].fillna(False)
 return m
def entries(x,idx,pair,v):
 hi=x.high.to_numpy();cl=x.close.to_numpy();op=x.open.to_numpy();p=ps(pair);out=[]
 for i in idx:
  if i+2>=len(x): continue
  if v=="next_open": out.append((i+1,op[i+1]))
  elif v=="break_signal_high":
   level=hi[i]+p*.5
   if hi[i+1]>=level: out.append((i+1,max(op[i+1],level)))
  elif v=="confirm_1bar" and cl[i+1]>hi[i]: out.append((i+2,op[i+2]))
 return out
def sim(x,pair,m,v,tp,sl,h,cost):
 p=ps(pair); raw=entries(x,np.flatnonzero(m.fillna(False).to_numpy()),pair,v)
 op=x.open.to_numpy();hi=x.high.to_numpy();lo=x.low.to_numpy();cl=x.close.to_numpy()
 chosen=[];last=-1
 for i,e in raw:
  if i<=last: continue
  chosen.append((i,e));last=i+h
 rr=[]
 for i,e in chosen:
  th=e+tp*p;st=e-sl*p;end=min(i+h,len(x)-1);res=None
  for j in range(i,end+1):
   ht=hi[j]>=th;hs=lo[j]<=st
   if ht and hs:res=-1.;break
   if ht:res=tp/sl;break
   if hs:res=-1.;break
  else:res=(cl[end]-e)/p/sl
  rr.append(res-cost/sl)
 if not rr:return None
 z=np.array(rr);gp=z[z>0].sum();gl=-z[z<0].sum()
 return len(z),float((z>0).mean()),float(gp/gl) if gl else np.inf,float(z.mean()),float(z.sum())
def main():
 rows=[]
 for pair,(structure,base_entry,base_tp,base_sl,base_h) in CANDS.items():
  fp=DATA/f"{pair}.parquet"
  if not fp.exists(): continue
  x=pd.read_parquet(fp).sort_index()
  for sn,part in zip(["discovery","validation","oos"],split(x)):
   m=mask(part,structure)
   for entry in ["next_open","break_signal_high","confirm_1bar"]:
    for tp in sorted(set([max(20,base_tp-25),base_tp,base_tp+25])):
     for sl in sorted(set([max(20,base_sl-25),base_sl,base_sl+25])):
      for h in sorted(set([max(24,base_h-24),base_h,base_h+24])):
       q3=sim(part,pair,m,entry,tp,sl,h,3.0);q5=sim(part,pair,m,entry,tp,sl,h,5.0)
       if q3:
        rows.append({"pair":pair,"split":sn,"entry":entry,"tp":tp,"sl":sl,"horizon":h,
          "trades":q3[0],"win_rate":q3[1],"pf_3p":q3[2],"expR_3p":q3[3],"netR_3p":q3[4],
          "pf_5p":q5[2],"expR_5p":q5[3],"netR_5p":q5[4],
          "is_frozen":int(entry==base_entry and tp==base_tp and sl==base_sl and h==base_h)})
 df=pd.DataFrame(rows);df.to_csv(OUT/"H1_NEIGHBORHOOD_ROBUSTNESS.csv",index=False)
 lines=["# H1 neighborhood robustness","","Frozen candidates are not re-selected. The purpose is local stability only. Positive-neighborhood counts are descriptive, not a new selection gate.",""]
 for pair in CANDS:
  d=df[df.pair==pair]
  lines.append(f"## {pair}")
  for sn in ["validation","oos"]:
   z=d[d.split==sn]
   base=z[z.is_frozen==1].iloc[0]
   robust=((z.trades>=10)&(z.pf_3p>1)&(z.expR_3p>0)&(z.pf_5p>1)&(z.expR_5p>0)).sum()
   lines.append(f"- {sn}: frozen PF/ExpR at 3p = {base.pf_3p:.3f}/{base.expR_3p:.3f}; 5p = {base.pf_5p:.3f}/{base.expR_5p:.3f}; robust neighbors = {int(robust)}/{len(z)}")
  lines.append("")
 (OUT/"H1_NEIGHBORHOOD_ROBUSTNESS.md").write_text("\n".join(lines)+"\n")
if __name__=="__main__":main()
