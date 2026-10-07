#!/usr/bin/env python3
import pandas as pd, numpy as np
from itertools import combinations
PATH="data/market/h4/usdjpy.csv"; ATR_N=14; BREAK_N=20; HOLD=20
EXT_MIN_ATR=.10; EXT_LOOKAHEAD=10; RETEST_LOOKAHEAD=15; RETEST_TOL_ATR=.15

def add_indicators(df):
    prev=df.close.shift(1); tr=pd.concat([df.high-df.low,(df.high-prev).abs(),(df.low-prev).abs()],axis=1).max(axis=1)
    df["atr"]=tr.rolling(ATR_N).mean(); df["ema20"]=df.close.ewm(span=20,adjust=False).mean()
    df["ema20_slope_atr"]=(df.ema20-df.ema20.shift(3))/df.atr
    df["body_atr"]=(df.close-df.open).abs()/df.atr; df["bear_body_atr"]=(df.open-df.close)/df.atr
    df["range_atr"]=(df.high-df.low)/df.atr; df["close_pos"]=(df.close-df.low)/(df.high-df.low).replace(0,np.nan)
    return df

def extract(df):
    df=add_indicators(df.copy()); out=[]; i=BREAK_N+ATR_N+2
    while i<len(df)-HOLD-2:
        level=float(df.low.iloc[i-BREAK_N:i].min())
        if df.close.iloc[i]>=level: i+=1; continue
        if not np.isfinite(df.atr.iloc[i]): i+=1; continue
        ext=next((j for j in range(i+1,min(len(df),i+1+EXT_LOOKAHEAD)) if df.low.iloc[j]<=level-EXT_MIN_ATR*df.atr.iloc[j]),None)
        if ext is None:i+=1;continue
        ret=next((j for j in range(ext+1,min(len(df),ext+1+RETEST_LOOKAHEAD)) if np.isfinite(df.atr.iloc[j]) and abs(df.close.iloc[j]-level)<=RETEST_TOL_ATR*df.atr.iloc[j]),None)
        if ret is None or df.close.iloc[ret]>=level:i+=1;continue
        ent=next((j for j in range(ret+1,min(len(df),ret+6)) if df.close.iloc[j]<df.open.iloc[j] and df.close.iloc[j-1]<df.open.iloc[j-1]),None)
        for idx,mode in [(ret,"retest"),(ent,"timed")]:
            if idx is None:continue
            lo5=df.low.iloc[max(0,idx-5):idx].min(); hi5=df.high.iloc[max(0,idx-5):idx].max()
            lo10=df.low.iloc[max(0,idx-10):idx].min(); hi10=df.high.iloc[max(0,idx-10):idx].max()
            out.append({"i":idx,"date":df.timestamp.iloc[idx],"entry":float(df.close.iloc[idx]),"atr":float(df.atr.iloc[idx]),
                "entry_mode":mode,"ema20_dist_atr":(df.close.iloc[idx]-df.ema20.iloc[idx])/df.atr.iloc[idx],
                "ema20_slope_atr":df.ema20_slope_atr.iloc[idx],"body_atr":df.body_atr.iloc[idx],
                "bear_body_atr":df.bear_body_atr.iloc[idx],"range_atr":df.range_atr.iloc[idx],"close_pos":df.close_pos.iloc[idx],
                "breakout_ext_atr":(level-df.low.iloc[ext])/df.atr.iloc[ext],"retest_depth_atr":(df.high.iloc[ret]-level)/df.atr.iloc[ret],
                "distance_from_breakout_atr":(level-df.close.iloc[idx])/df.atr.iloc[idx],
                "recent5_low_dist_atr":(df.close.iloc[idx]-lo5)/df.atr.iloc[idx],"recent5_high_dist_atr":(hi5-df.close.iloc[idx])/df.atr.iloc[idx],
                "recent10_low_dist_atr":(df.close.iloc[idx]-lo10)/df.atr.iloc[idx],"recent10_high_dist_atr":(hi10-df.close.iloc[idx])/df.atr.iloc[idx]})
        i=(ent if ent is not None else ret)+1
    return df,pd.DataFrame(out)

def classify(df,e):
    i=int(e.i); fw=fl=None
    for k in range(1,HOLD+1):
        j=i+k
        if j>=len(df):break
        prev5=df.iloc[max(i,j-5):j]; prev3=df.iloc[max(i,j-3):j]
        fav=(e.entry-float(df.close.iloc[j]))/e.atr.iloc[i]
        new_low=float(df.low.iloc[j])<float(prev5.low.min()) if len(prev5) else False
        br=float(df.close.iloc[j])>float(prev3.high.max()) if len(prev3) else False
        if fw is None and new_low and fav>=.75:fw=k
        if fl is None and br:fl=k
        if fw is not None or fl is not None:break
    if fw is None and fl is None:return "TIME"
    return "WIN" if fw is not None and (fl is None or fw<fl) else "LOSS"

def main():
    raw=pd.read_csv(PATH); raw["timestamp"]=pd.to_datetime(raw.timestamp,unit="ms"); raw=raw.sort_values("timestamp").reset_index(drop=True)
    df,out=extract(raw); out["label"]=out.apply(lambda r:classify(df,r),axis=1); out["year"]=out.date.dt.year
    out.to_csv("reports/usdjpy_bear_state_transition_events_2026-10-07.csv",index=False)
    feats=["ema20_dist_atr","ema20_slope_atr","body_atr","bear_body_atr","range_atr","close_pos","breakout_ext_atr","retest_depth_atr","distance_from_breakout_atr","recent5_low_dist_atr","recent5_high_dist_atr","recent10_low_dist_atr","recent10_high_dist_atr"]
    rows=[]
    for mode,g in out.groupby("entry_mode"):
      for period,h in [("discovery",g[g.year<=2024]),("validation",g[g.year==2025]),("oos",g[g.year>=2026])]:
        if len(h)<5:continue
        rows.append({"entry_mode":mode,"period":period,"n":len(h),"win_rate":(h.label=="WIN").mean(),"loss_rate":(h.label=="LOSS").mean(),"time_rate":(h.label=="TIME").mean()})
        for f in feats:
          if h[f].notna().sum()>=10:
            med=h[f].median(); z=h[h[f]>=med]
            rows.append({"entry_mode":mode,"period":period,"feature":f,"split":"median_high","n":len(z),"win_rate":(z.label=="WIN").mean(),"loss_rate":(z.label=="LOSS").mean(),"time_rate":(z.label=="TIME").mean(),"feature_mean":z[f].mean()})
        # 2-condition combinations: median split, retain only cells with >=5
        for a,b in combinations(feats,2):
          if h[[a,b]].notna().all(axis=1).sum()<10:continue
          ma,mb=h[a].median(),h[b].median(); z=h[(h[a]>=ma)&(h[b]>=mb)]
          if len(z)>=5:
            rows.append({"entry_mode":mode,"period":period,"feature":a+"&"+b,"split":"both_median_high","n":len(z),"win_rate":(z.label=="WIN").mean(),"loss_rate":(z.label=="LOSS").mean(),"time_rate":(z.label=="TIME").mean()})
    pd.DataFrame(rows).to_csv("reports/usdjpy_bear_state_transition_summary_2026-10-07.csv",index=False)
    print(out.groupby(["entry_mode","year","label"]).size().to_string())
if __name__=="__main__":main()
