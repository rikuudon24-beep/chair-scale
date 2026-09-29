#!/usr/bin/env python3
from pathlib import Path
import itertools, numpy as np, pandas as pd, math

ROOT=Path(__file__).resolve().parents[3]; DATA=ROOT/"research/h1/results/datasets"; OUT=ROOT/"research/h1/results"

def split(x):
    n=len(x); a=int(n*.6); b=int(n*.2); return x.iloc[:a],x.iloc[a:a+b],x.iloc[a+b:]
def ps(pair): return .01 if "jpy" in pair else .0001
def wilson(k,n):
    if n==0:return 0
    z=1.96;p=k/n;d=1+z*z/n
    return (p+z*z/(2*n)-z*math.sqrt((p*(1-p)+z*z/(4*n))/n))/d

def outcome(x,pair,idx,direction):
    p=ps(pair); op=x.open.to_numpy();hi=x.high.to_numpy();lo=x.low.to_numpy()
    entry=op[idx+1]
    if direction=="long": return np.max(hi[idx+1:idx+49])-entry >= 100*p
    return entry-np.min(lo[idx+1:idx+49]) >= 100*p

def evalmask(x,pair,mask,direction):
    idx=np.flatnonzero(mask.fillna(False).to_numpy()); chosen=[]; nxt=-1
    for i in idx:
        if i<nxt or i+48>=len(x): continue
        chosen.append(i);nxt=i+49
    n=len(chosen); k=sum(outcome(x,pair,i,direction) for i in chosen)
    return n,k,(k/n if n else np.nan),wilson(k,n)

def atoms(x,direction):
    r=x.rsi14
    a={
      "break20_up":x.break20_up,"break20_down":x.break20_down,
      "trend_up":x.trend_up,"trend_down":x.trend_down,
      "adx20+":x.adx14>=20,"adx25+":x.adx14>=25,
      "rsi<40":r<40,"rsi40_45":r.between(40,45),"rsi45_55":r.between(45,55),
      "rsi55_60":r.between(55,60),"rsi>60":r>60,
      "macd_pos":x.macd_hist>0,"macd_neg":x.macd_hist<0,
      "atr_above_med":x.atr14>x.atr14.rolling(200,min_periods=100).median(),
      "bb_narrow":x.bb_width<x.bb_width.rolling(200,min_periods=100).median(),
      "near_ema20":x.dist_ema20_atr.abs()<=.5,
      "far_ema200":x.dist_ema200_atr.abs()>=1.0,
      "h4_bull":x.h4_close>x.h4_open,"h4_bear":x.h4_close<x.h4_open,
      "d1_bull":x.d1_close>x.d1_open,"d1_bear":x.d1_close<x.d1_open,
      "w1_bull":x.w1_close>x.w1_open,"w1_bear":x.w1_close<x.w1_open,
      "rsi_up6":r-r.shift(6)>3,"rsi_down6":r-r.shift(6)<-3,
      "adx_up6":x.adx14-x.adx14.shift(6)>2,
    }
    return {k:v.fillna(False) for k,v in a.items()}

def main():
    discovered=[]
    for fp in sorted(DATA.glob("*.parquet")):
        pair=fp.stem;x=pd.read_parquet(fp).sort_index();disc,_,_=split(x)
        for direction in ["long","short"]:
            aa=atoms(disc,direction)
            for size in [1,2,3]:
                for names in itertools.combinations(aa,size):
                    m=pd.Series(True,index=disc.index)
                    for name in names:m &= aa[name]
                    n,k,hr,lcb=evalmask(disc,pair,m,direction)
                    if n>=50 and hr>=.55 and lcb>=.45:
                        discovered.append({"pair":pair,"direction":direction,"conditions":" & ".join(names),"discovery_trades":n,"discovery_hit":hr,"discovery_lcb":lcb})
    d=pd.DataFrame(discovered)
    if d.empty:
        (OUT/"precursor_candidates.md").write_text("# H1 precursor candidates\n\nNo candidates passed the discovery gate.\n"); return
    d=d.sort_values(["discovery_lcb","discovery_hit","discovery_trades"],ascending=False).drop_duplicates(["pair","direction","conditions"]).head(100)
    rows=[]
    for _,r in d.iterrows():
        x=pd.read_parquet(DATA/f"{r.pair}.parquet").sort_index(); disc,val,oos=split(x)
        for sn,part in [("validation",val),("oos",oos)]:
            aa=atoms(part,r.direction);m=pd.Series(True,index=part.index)
            for name in r.conditions.split(" & "):m &= aa[name]
            n,k,hr,lcb=evalmask(part,r.pair,m,r.direction)
            rows.append({**r.to_dict(),"split":sn,"trades":n,"hit_rate":hr,"lcb95":lcb})
    f=pd.DataFrame(rows); f.to_csv(OUT/"precursor_candidates_followup.csv",index=False)
    lines=["# H1 precursor candidates","","Discovery gate: n >= 50, hit rate >= 55%, Wilson 95% lower bound >= 45%.","Validation/OOS were not used for selection.","","|Pair|Dir|Conditions|Split|Trades|Hit rate|LCB95|","|---|---|---|---:|---:|---:|---:|"]
    for _,r in f.iterrows():lines.append(f"|{r.pair}|{r.direction}|{r.conditions}|{r.split}|{int(r.trades)}|{r.hit_rate:.3f}|{r.lcb95:.3f}|")
    (OUT/"precursor_candidates.md").write_text("\n".join(lines)+"\n")

if __name__=="__main__":main()
