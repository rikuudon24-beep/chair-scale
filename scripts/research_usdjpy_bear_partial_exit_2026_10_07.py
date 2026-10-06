#!/usr/bin/env python3
from pathlib import Path
import pandas as pd,numpy as np
PATH="data/market/h4/usdjpy.csv"; PIP=.01; ATR_N=14; BREAK_N=20
def atr(df):
 p=df.close.shift(1); tr=pd.concat([df.high-df.low,(df.high-p).abs(),(df.low-p).abs()],axis=1).max(axis=1)
 return tr.rolling(ATR_N).mean()
def events(df):
 df=df.copy(); df["atr"]=atr(df); out=[]; i=BREAK_N+ATR_N+2
 while i<len(df)-25:
  hi=df.high.iloc[i-BREAK_N:i].max(); lo=df.low.iloc[i-BREAK_N:i].min()
  if df.close.iloc[i]>=hi: i+=1; continue
  level=lo; ba=df.atr.iloc[i]
  if not np.isfinite(ba): i+=1; continue
  ext=next((j for j in range(i+1,min(len(df),i+11)) if df.low.iloc[j]<=level-.25*ba),None)
  if ext is None: i+=1; continue
  ret=next((j for j in range(ext+1,min(len(df),ext+11)) if abs(df.close.iloc[j]-level)<=.10*df.atr.iloc[j]),None)
  if ret is None or df.close.iloc[ret]>=level: i+=1; continue
  ent=next((j for j in range(ret+1,min(len(df),ret+6)) if df.close.iloc[j]<df.open.iloc[j] and df.close.iloc[j-1]<df.open.iloc[j-1]),None)
  if ent is None: i+=1; continue
  out.append(dict(i=ent,date=df.timestamp.iloc[ent],entry=df.close.iloc[ent],atr=df.atr.iloc[ent],rh=df.high.iloc[ret]))
  i=ent+1
 return out
def run(df,e,slm,partial,trail=False):
 i=e["i"]; en=e["entry"]; sl=en+slm*e["atr"]; risk=sl-en
 qty1=.5 if partial else 1.; qty2=1-qty1
 p1=en-1.0; p2=en-2.0
 rem=qty2; realized=0.; hit1=False; exit_i=None
 for j in range(i+1,min(len(df),i+1+20)):
  hi,lo=df.high.iloc[j],df.low.iloc[j]
  # conservative: if SL and TP same bar, SL first
  if not hit1:
   if hi>=sl: return -1.0, j-i, "SL", False
   if lo<=p1:
    realized += qty1*(en-p1)/risk; hit1=True
    # after 100pips, move remaining to breakeven
    if qty2>0: sl2=en
   if hit1 and qty2>0:
    if hi>=sl2: return realized,j-i,"BE",True
    if lo<=p2:
     realized += qty2*(en-p2)/risk; return realized,j-i,"TP200",True
  else:
   # remaining half: BE then 200 target
   if hi>=en: return realized,j-i,"BE",True
   if lo<=p2:
    realized += qty2*(en-p2)/risk; return realized,j-i,"TP200",True
 # timeout mark-to-market
 px=df.close.iloc[min(len(df)-1,i+20)]
 return realized+(qty2*(en-px)/risk if hit1 else (en-px)/risk),20,"TIME",hit1
def main():
 df=pd.read_csv(PATH); df.timestamp=pd.to_datetime(df.timestamp,unit="ms"); df=df.sort_values("timestamp").reset_index(drop=True)
 es=events(df); rows=[]
 for slm in [.5,.75,1.0]:
  for partial in [True,False]:
   for e in es:
    r,b,o,p=run(df,e,slm,partial)
    rows.append([e["date"],slm,partial,o,r,b])
 out=pd.DataFrame(rows,columns=["date","sl_mult","partial","outcome","r","bars"]); out["year"]=out.date.dt.year
 sm=[]
 for (s,p),g in out.groupby(["sl_mult","partial"]):
  for name,h in [("discovery",g[g.year<=2024]),("validation",g[g.year==2025]),("oos",g[g.year>=2026])]:
   if len(h):
    gp=h.loc[h.r>0,"r"].sum(); gl=-h.loc[h.r<0,"r"].sum()
    sm.append([s,p,name,len(h),(h.r>0).mean(),h.r.mean(),gp/gl if gl else np.nan,h.r.sum()])
 pd.DataFrame(sm,columns=["sl_mult","partial","period","n","positive_rate","expectancy_r","pf","total_r"]).to_csv("reports/usdjpy_bear_partial_exit_2026-10-07.csv",index=False)
 out.to_csv("reports/usdjpy_bear_partial_exit_events_2026-10-07.csv",index=False)
 print(pd.DataFrame(sm,columns=["sl_mult","partial","period","n","positive_rate","expectancy_r","pf","total_r"]).to_string(index=False))
if __name__=="__main__":main()
