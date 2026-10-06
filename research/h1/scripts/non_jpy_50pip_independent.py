#!/usr/bin/env python3
"""Independent H1 research for the six pairs that failed the prior 100pip gate.
Uses a different target architecture: 50-pip movement + H4 context + H1 structural/momentum states.
No reuse of the six routed pair-specific rules.
"""
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[3]; DATA=ROOT/"research/h1/results/datasets"; OUT=ROOT/"research/h1/results"
PAIRS=["eurusd","gbpusd","nzdusd","usdcad","eurgbp","audjpy"]

def split(x):
 n=len(x); a=int(n*.6); b=int(n*.2); return x.iloc[:a],x.iloc[a:a+b],x.iloc[a+b:]
def ps(pair): return .01 if "jpy" in pair else .0001
def hit50(x,pair,direction,h=24):
 p=ps(pair); idx=np.arange(len(x)); c=x.close.to_numpy(); hi=x.high.to_numpy(); lo=x.low.to_numpy()
 out=np.full(len(x),np.nan)
 for i in idx[:-h]:
  if direction=="long": out[i]=1.0 if np.max(hi[i+1:i+h+1])>=c[i]+50*p else 0.0
  else: out[i]=1.0 if np.min(lo[i+1:i+h+1])<=c[i]-50*p else 0.0
 return pd.Series(out,index=x.index)
def main():
 rows=[]
 for pair in PAIRS:
  fp=DATA/f"{pair}.parquet"
  if not fp.exists(): continue
  x=pd.read_parquet(fp).sort_index()
  for sn,part in zip(["discovery","validation","oos"],split(x)):
   states={
    "h4_bull+break20_down":(part.h4_close>part.h4_open)&part.break20_down,
    "h4_bull+rsi_up3+break20_down":(part.h4_close>part.h4_open)&(part.rsi14-part.rsi14.shift(3)>2)&part.break20_down,
    "h4_bull+adx20+rsi_up6":(part.h4_close>part.h4_open)&(part.adx14>=20)&(part.rsi14-part.rsi14.shift(6)>3),
    "h4_bull+atr_expand+break20_down":(part.h4_close>part.h4_open)&(part.atr14>part.atr14.rolling(20).mean())&part.break20_down,
    "d1_bull+break20_down":(part.d1_close>part.d1_open)&part.break20_down,
    "h4_bull+trend_down+rsi_up6":(part.h4_close>part.h4_open)&part.trend_down&(part.rsi14-part.rsi14.shift(6)>3),
   }
   for name,m in states.items():
    for direction in ["long","short"]:
     h=hit50(part,pair,direction,24)
     mm=m.fillna(False)
     vals=h[mm].dropna()
     if len(vals):
      rows.append({"pair":pair,"split":sn,"state":name,"direction":direction,"n":len(vals),"hit":float(vals.mean())})
 df=pd.DataFrame(rows); df.to_csv(OUT/"NONJPY_50PIP_INDEPENDENT.csv",index=False)
 # Discovery gate: n>=50, hit>=55%, Wilson lower bound >=45%.
 def lcb(k,n):
  if n==0:return 0
  z=1.959963984540054; ph=k/n; den=1+z*z/n
  return (ph+z*z/(2*n)-z*np.sqrt(ph*(1-ph)/n+z*z/(4*n*n)))/den
 d=df[df.split=="discovery"].copy(); d["lcb"]=[lcb(int(r.n*r.hit),int(r.n)) for _,r in d.iterrows()]
 cand=d[(d.n>=50)&(d.hit>=.55)&(d.lcb>=.45)].copy()
 cand.to_csv(OUT/"NONJPY_50PIP_CANDIDATES.csv",index=False)
 (OUT/"NONJPY_50PIP_INDEPENDENT.md").write_text("# Independent non-JPY H1 research — 50 pip architecture\n\nThis is a separate research family from the routed six candidates. Target: +50 pips within 24 H1 bars. Discovery gate remains n>=50, hit>=55%, Wilson 95% LCB>=45%. No gate weakening is allowed.\n\nCandidates passing discovery:\n\n"+(cand.to_string(index=False) if len(cand) else "NONE")+"\n")
 print(cand.to_string(index=False) if len(cand) else "NONE")
if __name__=="__main__":main()
