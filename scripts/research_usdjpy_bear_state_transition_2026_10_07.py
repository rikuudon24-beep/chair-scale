#!/usr/bin/env python3
import pandas as pd
import numpy as np

PATH = "data/market/h4/usdjpy.csv"
ATR_N = 14
BREAK_N = 20
HOLD = 20
EXT_MIN_ATR = 0.10
EXT_LOOKAHEAD = 10
RETEST_LOOKAHEAD = 15
RETEST_TOL_ATR = 0.15

def add_indicators(df):
    prev = df.close.shift(1)
    tr = pd.concat([df.high-df.low, (df.high-prev).abs(), (df.low-prev).abs()], axis=1).max(axis=1)
    df["atr"] = tr.rolling(ATR_N).mean()
    df["ema20"] = df.close.ewm(span=20, adjust=False).mean()
    df["ema20_slope_atr"] = (df.ema20-df.ema20.shift(3))/df.atr
    df["body_atr"] = (df.close-df.open).abs()/df.atr
    df["bear_body_atr"] = (df.open-df.close)/df.atr
    df["range_atr"] = (df.high-df.low)/df.atr
    df["close_pos"] = (df.close-df.low)/(df.high-df.low).replace(0,np.nan)
    return df

def extract_events(df):
    df=add_indicators(df.copy()); out=[]
    i=BREAK_N+ATR_N+2
    while i < len(df)-HOLD-2:
        level=float(df.low.iloc[i-BREAK_N:i].min())
        if df.close.iloc[i] >= level: i+=1; continue
        a=float(df.atr.iloc[i])
        if not np.isfinite(a): i+=1; continue
        ext=next((j for j in range(i+1,min(len(df),i+1+EXT_LOOKAHEAD))
                  if df.low.iloc[j] <= level-EXT_MIN_ATR*df.atr.iloc[j]),None)
        if ext is None: i+=1; continue
        ret=next((j for j in range(ext+1,min(len(df),ext+1+RETEST_LOOKAHEAD))
                  if np.isfinite(df.atr.iloc[j]) and abs(df.close.iloc[j]-level)<=RETEST_TOL_ATR*df.atr.iloc[j]),None)
        if ret is None or df.close.iloc[ret] >= level: i+=1; continue
        ent=next((j for j in range(ret+1,min(len(df),ret+6))
                  if df.close.iloc[j]<df.open.iloc[j] and df.close.iloc[j-1]<df.open.iloc[j-1]),None)
        def pack(idx,mode):
            if idx is None:return None
            lo5=float(df.low.iloc[max(0,idx-5):idx].min()); hi5=float(df.high.iloc[max(0,idx-5):idx].max())
            lo10=float(df.low.iloc[max(0,idx-10):idx].min()); hi10=float(df.high.iloc[max(0,idx-10):idx].max())
            return {"i":idx,"date":df.timestamp.iloc[idx],"entry":float(df.close.iloc[idx]),"atr":float(df.atr.iloc[idx]),
                    "breakout_level":level,"entry_mode":mode,
                    "ema20_dist_atr":(float(df.close.iloc[idx])-float(df.ema20.iloc[idx]))/float(df.atr.iloc[idx]),
                    "ema20_slope_atr":float(df.ema20_slope_atr.iloc[idx]),"body_atr":float(df.body_atr.iloc[idx]),
                    "bear_body_atr":float(df.bear_body_atr.iloc[idx]),"range_atr":float(df.range_atr.iloc[idx]),
                    "close_pos":float(df.close_pos.iloc[idx]),"breakout_ext_atr":(level-float(df.low.iloc[ext]))/float(df.atr.iloc[ext]),
                    "retest_depth_atr":(float(df.high.iloc[ret])-level)/float(df.atr.iloc[ret]),
                    "distance_from_breakout_atr":(level-float(df.close.iloc[idx]))/float(df.atr.iloc[idx]),
                    "recent5_low_dist_atr":(float(df.close.iloc[idx])-lo5)/float(df.atr.iloc[idx]),
                    "recent5_high_dist_atr":(hi5-float(df.close.iloc[idx]))/float(df.atr.iloc[idx]),
                    "recent10_low_dist_atr":(float(df.close.iloc[idx])-lo10)/float(df.atr.iloc[idx]),
                    "recent10_high_dist_atr":(hi10-float(df.close.iloc[idx]))/float(df.atr.iloc[idx])}
        out.append({"retest":pack(ret,"retest"),"timed":pack(ent,"timed")})
        i=(ent if ent is not None else ret)+1
    return df,out

def classify(df,e):
    i=e["i"]; fw=fl=None
    for k in range(1,HOLD+1):
        j=i+k
        if j>=len(df):break
        prev5=df.iloc[max(i,j-5):j]; prev3=df.iloc[max(i,j-3):j]
        low=float(df.low.iloc[j]); close=float(df.close.iloc[j])
        fav=(e["entry"]-close)/e["atr"]
        new_low=len(prev5)>0 and low<float(prev5.low.min())
        structure_break=len(prev3)>0 and close>float(prev3.high.max())
        if fw is None and new_low and fav>=0.75: fw=k
        if fl is None and structure_break: fl=k
        if fw is not None or fl is not None: break
    if fw is None and fl is None:return "TIME",HOLD,np.nan
    if fw is not None and (fl is None or fw<fl):
        return "WIN",fw,(e["entry"]-float(df.close.iloc[i+fw]))/e["atr"]
    return "LOSS",fl,(e["entry"]-float(df.close.iloc[i+fl]))/e["atr"]

def main():
    raw=pd.read_csv(PATH); raw["timestamp"]=pd.to_datetime(raw["timestamp"],unit="ms")
    raw=raw.sort_values("timestamp").reset_index(drop=True); df,events=extract_events(raw)
    rows=[]
    for item in events:
        for mode in ["retest","timed"]:
            e=item[mode]
            if e is None:continue
            label,bars,exc=classify(df,e); r=e.copy()
            r.update({"label":label,"label_bars":bars,"label_exc_atr":exc,"year":int(e["date"].year)}); rows.append(r)
    out=pd.DataFrame(rows); out.to_csv("reports/usdjpy_bear_state_transition_events_2026-10-07.csv",index=False)
    summary=[]
    features=["ema20_dist_atr","ema20_slope_atr","body_atr","bear_body_atr","range_atr","close_pos",
              "breakout_ext_atr","retest_depth_atr","distance_from_breakout_atr","recent5_low_dist_atr",
              "recent5_high_dist_atr","recent10_low_dist_atr","recent10_high_dist_atr"]
    for mode,g in out.groupby("entry_mode"):
        for period,h in [("discovery",g[g.year<=2024]),("validation",g[g.year==2025]),("oos",g[g.year>=2026])]:
            if h.empty:continue
            summary.append({"entry_mode":mode,"period":period,"n":len(h),"win_rate":(h.label=="WIN").mean(),
                            "loss_rate":(h.label=="LOSS").mean(),"time_rate":(h.label=="TIME").mean(),
                            "median_win_bars":h.loc[h.label=="WIN","label_bars"].median(),
                            "median_loss_bars":h.loc[h.label=="LOSS","label_bars"].median()})
            for f in features:
                if h[f].notna().sum()<10:continue
                med=h[f].median(); hi=h[h[f]>=med]
                summary.append({"entry_mode":mode,"period":period,"feature":f,"split":"median_high","n":len(hi),
                                "win_rate":(hi.label=="WIN").mean(),"loss_rate":(hi.label=="LOSS").mean(),
                                "time_rate":(hi.label=="TIME").mean(),"feature_mean":hi[f].mean(),
                                "other_feature_mean":h[h[f]<med][f].mean()})
    pd.DataFrame(summary).to_csv("reports/usdjpy_bear_state_transition_summary_2026-10-07.csv",index=False)
    print("EVENTS",len(events),"RETEST",sum(x["retest"] is not None for x in events),"TIMED",sum(x["timed"] is not None for x in events))
    print(out.groupby(["entry_mode","year","label"]).size().to_string())

if __name__=="__main__":main()
