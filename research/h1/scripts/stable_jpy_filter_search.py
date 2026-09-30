#!/usr/bin/env python3
from pathlib import Path
import itertools, math, pandas as pd, numpy as np

ROOT=Path(__file__).resolve().parents[3]
DATA=ROOT/"research/h1/results/datasets"
OUT=ROOT/"research/h1/results"
PAIRS=["usdjpy","eurjpy","gbpjpy"]

def split(x):
    n=len(x); a=int(n*.6); b=int(n*.2)
    return x.iloc[:a],x.iloc[a:a+b],x.iloc[a+b:]

def ps(pair): return .01 if "jpy" in pair else .0001

def wilson(k,n,z=1.96):
    if n==0:return 0.0
    p=k/n; d=1+z*z/n
    return (p+z*z/(2*n)-z*math.sqrt((p*(1-p)+z*z/(4*n))/n))/d

def atoms(x):
    r=x.rsi14
    a={
      "adx20+":x.adx14>=20,"adx25+":x.adx14>=25,
      "rsi<40":r<40,"rsi40_45":r.between(40,45),"rsi45_55":r.between(45,55),
      "rsi55_60":r.between(55,60),"rsi>60":r>60,
      "macd_pos":x.macd_hist>0,"macd_neg":x.macd_hist<0,
      "atr_above_med":x.atr14>x.atr14.rolling(200,min_periods=100).median(),
      "bb_narrow":x.bb_width<x.bb_width.rolling(200,min_periods=100).median(),
      "near_ema20":x.dist_ema20_atr.abs()<=.5,
      "far_ema200":x.dist_ema200_atr.abs()>=1.0,
      "rsi_up6":r-r.shift(6)>3,"adx_up6":x.adx14-x.adx14.shift(6)>2,
      "break20_up":x.break20_up,"break20_down":x.break20_down,
      "w1_bull":x.w1_close>x.w1_open,"w1_bear":x.w1_close<x.w1_open,
    }
    return {k:v.fillna(False) for k,v in a.items()}

def signal_indices(x, mask):
    idx=np.flatnonzero(mask.fillna(False).to_numpy())
    chosen=[]; nxt=-1
    for i in idx:
        if i<nxt or i+48>=len(x): continue
        chosen.append(i); nxt=i+49
    return chosen

def trade_result(x,pair,i,tp,sl):
    p=ps(pair); entry=float(x.open.iloc[i+1])
    end=min(i+49,len(x))
    hi=x.high.to_numpy(); lo=x.low.to_numpy()
    for j in range(i+1,end):
        hit_tp=hi[j] >= entry+tp*p
        hit_sl=lo[j] <= entry-sl*p
        if hit_tp and hit_sl: return -1.0
        if hit_sl: return -1.0
        if hit_tp: return 1.0
    return 0.0

def eval_part(x,pair,mask,tp=50,sl=75):
    ids=signal_indices(x,mask)
    vals=[trade_result(x,pair,i,tp,sl) for i in ids]
    n=len(vals); w=sum(v>0 for v in vals)
    gp=sum(v for v in vals if v>0); gl=-sum(v for v in vals if v<0)
    pf=(gp/gl) if gl else (float("inf") if gp else 0.0)
    return n,w/n if n else np.nan,wilson(w,n),pf,sum(vals)/n if n else np.nan

def pooled_eval(parts, masks, tp=50, sl=75):
    allvals=[]
    for x,pair,mask in zip(parts[0],parts[1],parts[2]):
        ids=signal_indices(x,mask)
        allvals.extend(trade_result(x,pair,i,tp,sl) for i in ids)
    n=len(allvals); w=sum(v>0 for v in allvals)
    gp=sum(v for v in allvals if v>0); gl=-sum(v for v in allvals if v<0)
    return n,w/n if n else np.nan,wilson(w,n),(gp/gl if gl else float("inf")),sum(allvals)/n if n else np.nan

def main():
    data={p:pd.read_parquet(DATA/f"{p}.parquet").sort_index() for p in PAIRS}
    # Freeze the already-discovered JPY-cross structure; only search simple additional filters.
    base=lambda x: x.trend_down & (x.h4_close>x.h4_open) & (x.d1_close>x.d1_open)
    discovered=[]
    names=None
    for size in [1,2]:
        for combo in itertools.combinations(sorted(atoms(data[PAIRS[0]].iloc[:int(len(data[PAIRS[0]])*.6)])),size):
            parts=[]; total_n=total_w=0
            for pair in PAIRS:
                x=data[pair]; disc,_,_=split(x); aa=atoms(disc)
                m=base(disc)
                for c in combo:m &= aa[c]
                ids=signal_indices(disc,m)
                vals=[trade_result(disc,pair,i,50,75) for i in ids]
                total_n += len(vals); total_w += sum(v>0 for v in vals)
            if total_n>=80:
                hit=total_w/total_n; lcb=wilson(total_w,total_n)
                if hit>=.55 and lcb>=.45:
                    discovered.append((combo,total_n,hit,lcb))
    discovered=sorted(discovered,key=lambda z:(z[3],z[2],z[1]),reverse=True)[:30]

    rows=[]
    for combo,dn,dh,dl in discovered:
        for split_name,ix in [("discovery",0),("validation",1),("oos",2)]:
            vals=[]
            for pair in PAIRS:
                parts=split(data[pair]); x=parts[ix]; aa=atoms(x); m=base(x)
                for c in combo:m &= aa[c]
                ids=signal_indices(x,m)
                vals.extend(trade_result(x,pair,i,50,75) for i in ids)
            n=len(vals); w=sum(v>0 for v in vals)
            gp=sum(v for v in vals if v>0); gl=-sum(v for v in vals if v<0)
            rows.append({
              "conditions":"trend_down & h4_bull & d1_bull & "+" & ".join(combo),
              "split":split_name,"trades":n,"win":w/n if n else np.nan,
              "lcb95":wilson(w,n),"pf":(gp/gl if gl else (float("inf") if gp else 0.0)),
              "exp_r":sum(vals)/n if n else np.nan
            })
    df=pd.DataFrame(rows)
    df.to_csv(OUT/"stable_jpy_filter_search.csv",index=False)
    lines=["# Stable JPY filter search","",
      "Universe: USDJPY/EURJPY/GBPJPY. Base structure is frozen as trend_down & h4_bull & d1_bull.",
      "Only simple 1-2 additional filters were selected on pooled Discovery. TP50/SL75, next-open, non-overlapping 48-H1 window.",
      "Validation and OOS are evaluation only.","",
      "|Conditions|Split|Trades|Win|LCB95|PF|ExpR|","|---|---|---:|---:|---:|---:|---:|"]
    for _,r in df.iterrows():
        lines.append(f"|{r.conditions}|{r.split}|{int(r.trades)}|{r.win:.3f}|{r.lcb95:.3f}|{r.pf:.3f}|{r.exp_r:.3f}|")
    (OUT/"stable_jpy_filter_search.md").write_text("\n".join(lines)+"\n")
    print(f"[OK] {len(discovered)} pooled JPY filter candidates")

if __name__=="__main__": main()
