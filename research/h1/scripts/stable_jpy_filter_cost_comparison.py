#!/usr/bin/env python3
from pathlib import Path
import pandas as pd, numpy as np

ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/"research/h1/results/datasets"
OUT=ROOT/"research/h1/results"
PAIRS=["usdjpy","eurjpy","gbpjpy"]
COSTS=[0.5,1,2,3,5]
CONFIGS=[(40,75,48),(40,90,48),(40,100,48),(50,75,48),(50,100,48)]
CONDS={
"w1_bull":lambda x:x.trend_down&(x.h4_close>x.h4_open)&(x.d1_close>x.d1_open)&(x.w1_close>x.w1_open),
"adx20_w1_bull":lambda x:x.trend_down&(x.h4_close>x.h4_open)&(x.d1_close>x.d1_open)&(x.adx14>=20)&(x.w1_close>x.w1_open),
"macd_pos_rsi_up6":lambda x:x.trend_down&(x.h4_close>x.h4_open)&(x.d1_close>x.d1_open)&(x.macd_hist>0)&((x.rsi14-x.rsi14.shift(6))>3),
"base":lambda x:x.trend_down&(x.h4_close>x.h4_open)&(x.d1_close>x.d1_open),
}
def split(x):
 n=len(x); a=int(n*.6); b=int(n*.2); return x.iloc[:a],x.iloc[a:a+b],x.iloc[a+b:]
def ids(x,m):
 raw=np.flatnonzero(m.fillna(False).to_numpy()); out=[]; nxt=-1
 for i in raw:
  if i<nxt or i+48>=len(x): continue
  out.append(i); nxt=i+49
 return out
def result(x,i,pair,tp,sl,cost):
 p=.01; e=float(x.open.iloc[i+1]); hi=x.high.to_numpy(); lo=x.low.to_numpy()
 for j in range(i+1,min(i+49,len(x))):
  ht=hi[j]>=e+(tp+cost)*p; hs=lo[j]<=e-(sl+cost)*p
  if ht and hs:return -1.0
  if hs:return -1.0
  if ht:return 1.0
 return 0.0
def ev(x,pair,m,tp,sl,cost):
 v=[result(x,i,pair,tp,sl,cost) for i in ids(x,m)]
 n=len(v); w=sum(z>0 for z in v); gp=sum(z for z in v if z>0); gl=-sum(z for z in v if z<0)
 return n,w/n if n else np.nan,gp/gl if gl else (float("inf") if gp else 0),sum(v)/n if n else np.nan
def main():
 data={p:pd.read_parquet(DATA/f"{p}.parquet").sort_index() for p in PAIRS}
 rows=[]
 for name,fn in CONDS.items():
  for tp,sl,h in CONFIGS:
   for cost in COSTS:
    for sp,ix in [("validation",1),("oos",2)]:
     vals=[]
     for pair in PAIRS:
      x=split(data[pair])[ix]; vals.append((pair,ev(x,pair,fn(x),tp,sl,cost)))
     for pair,(n,w,pf,ex) in vals:
      rows.append({"condition":name,"tp":tp,"sl":sl,"horizon":h,"cost_pips":cost,"split":sp,"pair":pair,"trades":n,"win":w,"pf":pf,"exp_r":ex})
 df=pd.DataFrame(rows); df.to_csv(OUT/"stable_jpy_filter_cost_comparison.csv",index=False)
 s=[]
 for (name,tp,sl,h,cost,sp),g in df.groupby(["condition","tp","sl","horizon","cost_pips","split"]):
  s.append({"condition":name,"tp":tp,"sl":sl,"horizon":h,"cost_pips":cost,"split":sp,
            "min_trades":int(g.trades.min()),"min_win":float(g.win.min()),"min_pf":float(g.pf.replace(np.inf,np.nan).min(skipna=True)),
            "all_positive":bool((g.exp_r>0).all())})
 sm=pd.DataFrame(s); sm.to_csv(OUT/"stable_jpy_filter_cost_summary.csv",index=False)
 lines=["# Stable JPY filter cost comparison","","Frozen candidates: w1_bull, adx20_w1_bull, macd_pos_rsi_up6, plus base. USDJPY/EURJPY/GBPJPY. Validation/OOS only; no selection. Costs are stress-test round-trip pip assumptions applied to TP/SL thresholds.","","|Condition|TP/SL|Cost|Split|Min n|Min win|Min PF|All +|","|---|---:|---:|---|---:|---:|---:|:---:|"]
 for _,r in sm.iterrows():
  lines.append(f"|{r.condition}|{int(r.tp)}/{int(r.sl)}|{r.cost_pips:g}|{r.split}|{int(r.min_trades)}|{r.min_win:.3f}|{r.min_pf:.3f}|{r.all_positive}|")
 (OUT/"stable_jpy_filter_cost_comparison.md").write_text("\n".join(lines)+"\n")
 print("[OK] stable JPY filter cost comparison")
if __name__=="__main__": main()
