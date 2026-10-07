#!/usr/bin/env python3
import pandas as pd
import numpy as np

PATH = "data/market/h4/usdjpy.csv"
ATR_N = 14
BREAK_N = 20
HOLD = 20

def add_indicators(df):
    prev = df.close.shift(1)
    tr = pd.concat([
        df.high-df.low, (df.high-prev).abs(), (df.low-prev).abs()
    ], axis=1).max(axis=1)
    df["atr"] = tr.rolling(ATR_N).mean()
    df["ema20"] = df.close.ewm(span=20, adjust=False).mean()
    return df

def extract_events(df):
    df = add_indicators(df.copy())
    out = []
    i = BREAK_N + ATR_N + 2
    while i < len(df)-HOLD-2:
        level = float(df.low.iloc[i-BREAK_N:i].min())
        if df.close.iloc[i] >= level:
            i += 1
            continue
        a = float(df.atr.iloc[i])
        if not np.isfinite(a):
            i += 1
            continue

        ext = next((j for j in range(i+1,min(len(df),i+11))
                    if df.low.iloc[j] <= level-0.25*a), None)
        if ext is None:
            i += 1
            continue

        ret = next((j for j in range(ext+1,min(len(df),ext+11))
                    if np.isfinite(df.atr.iloc[j])
                    and abs(df.close.iloc[j]-level) <= 0.10*df.atr.iloc[j]), None)
        if ret is None or df.close.iloc[ret] >= level:
            i += 1
            continue

        ent = next((j for j in range(ret+1,min(len(df),ret+6))
                    if df.close.iloc[j] < df.open.iloc[j]
                    and df.close.iloc[j-1] < df.open.iloc[j-1]), None)

        def pack(idx):
            return {
                "i": idx,
                "date": df.timestamp.iloc[idx],
                "entry": float(df.close.iloc[idx]),
                "atr": float(df.atr.iloc[idx]),
                "breakout_level": level,
                "retest_high": float(df.high.iloc[ret]),
                "structure5_high": float(df.high.iloc[idx-5:idx].max()),
                "structure10_high": float(df.high.iloc[idx-10:idx].max()),
                "breakout_i": i, "retest_i": ret
            }

        out.append({"retest": pack(ret), "timed": pack(ent) if ent is not None else None})
        i = (ent if ent is not None else ret) + 1
    return df, out

def stop_price(e, mode):
    en,a=e["entry"],e["atr"]
    if mode=="atr05": return en+0.50*a
    if mode=="atr075": return en+0.75*a
    if mode=="atr10": return en+1.00*a
    if mode=="retest": return e["retest_high"]
    if mode=="struct5": return e["structure5_high"]
    if mode=="struct10": return e["structure10_high"]
    raise ValueError(mode)

def simulate(df,e,sl_mode,exit_mode):
    i=e["i"]; en=e["entry"]; sl=stop_price(e,sl_mode); risk=sl-en
    if risk<=0 or not np.isfinite(risk):
        return np.nan,0,"INVALID"
    level=e["breakout_level"]
    for j in range(i+1,min(len(df),i+1+HOLD)):
        hi=float(df.high.iloc[j]); cl=float(df.close.iloc[j])
        if hi>=sl:
            return -1.0,j-i,"SL"

        if exit_mode=="chandelier15":
            trail=df.low.iloc[i:j+1].min()+1.5*df.atr.iloc[j]
            if cl>trail: return (cl-en)/risk,j-i,"CH15"
        elif exit_mode=="chandelier20":
            trail=df.low.iloc[i:j+1].min()+2.0*df.atr.iloc[j]
            if cl>trail: return (cl-en)/risk,j-i,"CH20"
        elif exit_mode=="chandelier25":
            trail=df.low.iloc[i:j+1].min()+2.5*df.atr.iloc[j]
            if cl>trail: return (cl-en)/risk,j-i,"CH25"
        elif exit_mode=="swing5trail" and j>=i+5:
            if cl>df.high.iloc[j-5:j].max():
                return (cl-en)/risk,j-i,"SW5"
        elif exit_mode=="ema20":
            if cl>df.ema20.iloc[j] and df.close.iloc[j-1]<=df.ema20.iloc[j-1]:
                return (cl-en)/risk,j-i,"EMA20"
        elif exit_mode=="range_reentry":
            if cl>=level:
                return (cl-en)/risk,j-i,"REENTRY"

    px=float(df.close.iloc[min(len(df)-1,i+HOLD)])
    return (px-en)/risk,HOLD,"TIME"

def summarize(out):
    rows=[]
    for (entry_mode,sl_mode,exit_mode),g in out.groupby(["entry_mode","sl_mode","exit_mode"]):
        for period,h in [("discovery",g[g.year<=2024]),("validation",g[g.year==2025]),("oos",g[g.year>=2026])]:
            if len(h)==0: continue
            gp=h.loc[h.r>0,"r"].sum(); gl=-h.loc[h.r<0,"r"].sum()
            rows.append([
                entry_mode,sl_mode,exit_mode,len(h),float((h.r>0).mean()),
                float(h.r.mean()),float(gp/gl) if gl>0 else np.nan,
                float(h.r.sum()),float(h.r.min()),float(h.bars.median())
            ])
    return pd.DataFrame(rows,columns=[
        "entry_mode","sl_mode","exit_mode","n","positive_rate",
        "expectancy_r","pf","total_r","worst_r","median_bars"
    ])

def main():
    df,events=extract_events(df_raw)
    sl_modes=["atr05","atr075","atr10","retest","struct5","struct10"]
    exit_modes=["chandelier15","chandelier20","chandelier25","swing5trail","ema20","range_reentry"]
    rows=[]
    for item in events:
        for entry_mode in ["retest","timed"]:
            e=item[entry_mode]
            if e is None: continue
            for sl in sl_modes:
                for ex in exit_modes:
                    r,b,o=simulate(df,e,sl,ex)
                    rows.append([e["date"],entry_mode,sl,ex,o,r,b])
    out=pd.DataFrame(rows,columns=["date","entry_mode","sl_mode","exit_mode","outcome","r","bars"])
    out["year"]=out.date.dt.year
    summary=summarize(out)
    summary.to_csv("reports/usdjpy_bear_dynamic_exit_2026-10-07.csv",index=False)
    out.to_csv("reports/usdjpy_bear_dynamic_exit_events_2026-10-07.csv",index=False)
    print("RETEST_EVENTS",len(events))
    print("TIMED_EVENTS",sum(x["timed"] is not None for x in events))
    print(summary.to_string(index=False))

if __name__=="__main__":
    df_raw=pd.read_csv(PATH)
    df_raw["timestamp"]=pd.to_datetime(df_raw["timestamp"],unit="ms")
    df_raw=df_raw.sort_values("timestamp").reset_index(drop=True)
    main()
