#!/usr/bin/env python3
from pathlib import Path
import itertools, math, pandas as pd, numpy as np
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"research/h1/results/datasets"; OUT=ROOT/"research/h1/results"
PAIRS=["eurusd","gbpusd","nzdusd","usdcad","eurgbp","audjpy"]
def split(x):
 n=len(x);a=int(n*.6);b=int(n*.2);return x.iloc[:a],x.iloc[a:a+b],x.iloc[a+b:]
def ps(p): return .01 if "jpy" in p else .0001
def wilson(k,n):
 if not n:return 0
 z=1.96;p=k/n;d=1+z*z/n
 return (p+z*z/(2*n)-z*math.sqrt((p*(1-p)+z*z/(4*n))/n))/d
def atoms(x):
 r=x.rsi14
 return {
 "break20_up":x.break20_up,"break20_down":x.break20_down,"trend_up":x.trend_up,"trend_down":x.trend_down,
 "adx20+":x.adx14>=20,"adx25+":x.adx14>=25,"rsi<40":r<40,"rsi40_45":r.between(40,45),
 "rsi45_55":r.between(45,55),"rsi55_60":r.between(55,60),"rsi>60":r>60,
 "macd_pos":x.macd_hist>0,"macd_neg":x.macd_hist<0,"atr_above_med":x.atr14>x.atr14.rolling(200,min_periods=100).median(),
 "bb_narrow":x.bb_width<x.bb_width.rolling(200,min_periods=100).median(),"near_ema20":x.dist_ema20_atr.abs()<=.5,
 "far_ema200":x.dist_ema200_atr.abs()>=1.0,"h4_bull":x.h4_close>x.h4_open,"h4_bear":x.h4_close<x.h4_open,
 "d1_bull":x.d1_close>x.d1_open,"d1_bear":x.d1_close<x.d1_open,"w1_bull":x.w1_close>x.w1_open,"w1_bear":x.w1_close<x.w1_open,
 "rsi_up6":r-r.shift(6)>3,"rsi_down6":r-r.shift(6)<-3,"adx_up6":x.adx14-x.adx14.shift(6)>2}
def eval(x,p,m,d):
 idx=np.flatnonzero(m.fillna(False).to_numpy());op=x.open.to_numpy();hi=x.high.to_numpy();lo=x.low.to_numpy();sel=[];nxt=-1
 for i in idx:
  if i<nxt or i+48>=len(x):continue
  sel.append(i);nxt=i+49
 k=0;pip=ps(p)
 for i in sel:
  e=op[i+1]
  k += (np.max(hi[i+1:i+49])-e>=100*pip) if d=="long" else (e-np.min(lo[i+1:i+49])>=100*pip)
 n=len(sel);return n,k,k/n if n else np.nan,wilson(k,n)
discrows=[];follow=[]
for p in PAIRS:
 x=pd.read_parquet(DATA/f"{p}.parquet").sort_index();disc,val,oos=split(x);aa=atoms(disc)
 for d in ["long","short"]:
  names=list(aa)
  for z in [1,2,3]:
   for comb in itertools.combinations(names,z):
    m=pd.Series(True,index=disc.index)
    for q in comb:m &= aa[q]
    n,k,hr,lcb=eval(disc,p,m,d)
    if n>=50 and hr>=.55 and lcb>=.45:
     discrows.append((p,d," & ".join(comb),n,hr,lcb))
# top candidates per pair/direction by discovery LCB, then test on validation/OOS
D=pd.DataFrame(discrows,columns=["pair","direction","conditions","discovery_trades","discovery_hit","discovery_lcb"])
D=D.sort_values(["pair","direction","discovery_lcb","discovery_hit"],ascending=[True,True,False,False]).groupby(["pair","direction"]).head(20)
for _,r in D.iterrows():
 x=pd.read_parquet(DATA/f'{r.pair}.parquet').sort_index()
 for sn,part in [("validation",split(x)[1]),("oos",split(x)[2])]:
  aa=atoms(part);m=pd.Series(True,index=part.index)
  for q in r.conditions.split(" & "):m &= aa[q]
  n,k,hr,lcb=eval(part,r.pair,m,r.direction)
  follow.append({**r.to_dict(),"split":sn,"trades":n,"hit_rate":hr,"lcb95":lcb})
D.to_csv(OUT/"NONJPY_DISCOVERY.csv",index=False);F=pd.DataFrame(follow);F.to_csv(OUT/"NONJPY_FOLLOWUP.csv",index=False)
lines=["# Non-JPY independent H1 research","","Pairs are researched independently because the JPY-derived architecture did not pass the routing gate.","Discovery gate is unchanged: n >= 50, hit >= 55%, Wilson LCB >= 45%. Selection uses discovery only.","","|Pair|Dir|Conditions|Disc n|Disc hit|Disc LCB|Split|n|Hit|LCB|","|---|---|---|---:|---:|---:|---|---:|---:|---:|"]
for _,r in F.iterrows():lines.append(f"|{r.pair}|{r.direction}|{r.conditions}|{int(r.discovery_trades)}|{r.discovery_hit:.3f}|{r.discovery_lcb:.3f}|{r.split}|{int(r.trades)}|{r.hit_rate:.3f}|{r.lcb95:.3f}|")
(OUT/"NONJPY_INDEPENDENT_RESEARCH.md").write_text("\n".join(lines)+"\n")
