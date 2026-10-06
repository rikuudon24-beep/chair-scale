#!/usr/bin/env python3
"""Independent non-JPY structural mining.

Searches symmetric pullback/reversal and breakout states for the six non-promoted
pairs. This is discovery only: strict Wilson gate, then any survivor must be
trade-backtested separately before promotion.
"""
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[3]; DATA=ROOT/"research/h1/results/datasets"; OUT=ROOT/"research/h1/results"
PAIRS=["eurusd","gbpusd","nzdusd","usdcad","eurgbp","audjpy"]
def split(x):
 n=len(x); a=int(n*.6); b=int(n*.2); return x.iloc[:a],x.iloc[a:a+b],x.iloc[a+b:]
def ps(pair): return .01 if "jpy" in pair else .0001
def hit(x,pair,d,h=24,t=50):
 p=ps(pair); c=x.close.to_numpy(); hi=x.high.to_numpy(); lo=x.low.to_numpy(); out=[]
 for i in range(len(x)-h):
  out.append(1 if (np.max(hi[i+1:i+h+1])>=c[i]+t*p if d=="long" else np.min(lo[i+1:i+h+1])<=c[i]-t*p) else 0)
 return np.array(out,dtype=float)
def lcb(k,n):
 z=1.959963984540054; ph=k/n; den=1+z*z/n
 return (ph+z*z/(2*n)-z*np.sqrt(ph*(1-ph)/n+z*z/(4*n*n)))/den
def main():
 rows=[]
 for pair in PAIRS:
  fp=DATA/f"{pair}.parquet"
  if not fp.exists(): continue
  x=pd.read_parquet(fp).sort_index()
  for sn,part in zip(["discovery","validation","oos"],split(x)):
   bull=(part.h4_close>part.h4_open); bear=(part.h4_close<part.h4_open)
   d1bull=(part.d1_close>part.d1_open); d1bear=(part.d1_close<part.d1_open)
   r3=part.rsi14-part.rsi14.shift(3); r6=part.rsi14-part.rsi14.shift(6)
   atrx=part.atr14>part.atr14.rolling(20).mean()
   states={
    "long_h4pull":bull&part.break20_down,
    "short_h4pull":bear&part.break20_up,
    "long_d1pull":d1bull&part.break20_down,
    "short_d1pull":d1bear&part.break20_up,
    "long_h4pull_rsi3":bull&part.break20_down&(r3>2),
    "short_h4pull_rsi3":bear&part.break20_up&(r3<-2),
    "long_h4pull_rsi6":bull&part.break20_down&(r6>3),
    "short_h4pull_rsi6":bear&part.break20_up&(r6<-3),
    "long_h4pull_adx":bull&part.break20_down&(part.adx14>=20),
    "short_h4pull_adx":bear&part.break20_up&(part.adx14>=20),
    "long_h4pull_atr":bull&part.break20_down&atrx,
    "short_h4pull_atr":bear&part.break20_up&atrx,
    "long_reversal":part.trend_down&(r6>3)&bull,
    "short_reversal":part.trend_up&(r6<-3)&bear,
    "long_reversal_d1":part.trend_down&(r6>3)&d1bull,
    "short_reversal_d1":part.trend_up&(r6<-3)&d1bear,
    "long_breakout":bull&part.break20_down==False&(part.close>part.prior20_high),
    "short_breakout":bear&part.break20_up==False&(part.close<part.prior20_low),
   }
   for state,m in states.items():
    direction="short" if state.startswith("short") else "long"
    vals=hit(part,pair,direction)[m.fillna(False).to_numpy()]
    if len(vals): rows.append({"pair":pair,"split":sn,"state":state,"direction":direction,"n":len(vals),"hit":float(vals.mean()),"lcb":lcb(int(vals.sum()),len(vals))})
 df=pd.DataFrame(rows); df.to_csv(OUT/"NONJPY_STRUCTURAL_MINING.csv",index=False)
 cand=df[(df.split=="discovery")&(df.n>=50)&(df.hit>=.55)&(df.lcb>=.45)].copy()
 cand.to_csv(OUT/"NONJPY_STRUCTURAL_CANDIDATES.csv",index=False)
 lines=["# Independent non-JPY structural mining","","Strict discovery gate: n>=50, hit>=55%, Wilson 95% LCB>=45%. No gate weakening. Survivors are event candidates only and require causal trade backtesting.","",cand.to_string(index=False) if len(cand) else "NONE"]
 (OUT/"NONJPY_STRUCTURAL_MINING.md").write_text("\n".join(lines)+"\n")
 print(cand.to_string(index=False) if len(cand) else "NONE")
if __name__=="__main__": main()
