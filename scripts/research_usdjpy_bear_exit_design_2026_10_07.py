#!/usr/bin/env python3
from pathlib import Path
import pandas as pd, numpy as np

PAIR="usdjpy"
PATH="data/market/h4/usdjpy.csv"
PIP=0.01
HORIZON=20
RETEST_MAX=10
ATR_N=14
BREAK_N=20

def atr(df):
    prev=df.close.shift(1)
    tr=pd.concat([df.high-df.low,(df.high-prev).abs(),(df.low-prev).abs()],axis=1).max(axis=1)
    return tr.rolling(ATR_N).mean()

def find_events(df):
    df=df.copy()
    df["atr"]=atr(df)
    events=[]
    i=BREAK_N+ATR_N+2
    while i < len(df)-HORIZON-5:
        prior_hi=df.high.iloc[i-BREAK_N:i].max()
        prior_lo=df.low.iloc[i-BREAK_N:i].min()
        direction=None; level=None
        if df.close.iloc[i] > prior_hi: direction="bull"; level=prior_hi
        elif df.close.iloc[i] < prior_lo: direction="bear"; level=prior_lo
        if direction!="bear":
            i+=1; continue
        br_atr=float(df.atr.iloc[i])
        if not np.isfinite(br_atr) or br_atr<=0:
            i+=1; continue
        # first extension >= 0.25 ATR, then first return within 0.10 ATR of broken level
        ext=None; ret=None
        for j in range(i+1,min(len(df),i+RETEST_MAX+1)):
            if float(df.low.iloc[j]) <= level-0.25*br_atr:
                ext=j; break
        if ext is None:
            i+=1; continue
        for j in range(ext+1,min(len(df),ext+RETEST_MAX+1)):
            if abs(float(df.close.iloc[j])-level) <= 0.10*float(df.atr.iloc[j]):
                ret=j; break
        if ret is None:
            i+=1; continue
        # success = retest candle closes below broken level
        if float(df.close.iloc[ret]) >= level:
            i=ret+1; continue
        # entry timing D: first point after retest with two consecutive down closes
        entry=None
        for j in range(ret+1,min(len(df),ret+6)):
            if float(df.close.iloc[j]) < float(df.open.iloc[j]) and float(df.close.iloc[j-1]) < float(df.open.iloc[j-1]):
                entry=j; break
        if entry is None:
            i=ret+1; continue
        events.append({
            "break_i":i,"ret_i":ret,"entry_i":entry,"break_level":level,
            "entry":float(df.close.iloc[entry]),"entry_atr":float(df.atr.iloc[entry]),
            "retest_high":float(df.high.iloc[ret]),
            "struct_high_5":float(df.high.iloc[max(0,entry-5):entry].max()),
            "struct_high_10":float(df.high.iloc[max(0,entry-10):entry].max()),
            "date":df.timestamp.iloc[entry]
        })
        i=entry+1
    return events

def sim(df,e,sl_name,sl_mult,tp,window=20):
    i=e["entry_i"]; entry=e["entry"]; atr0=e["entry_atr"]
    if sl_name=="atr":
        sl=entry+sl_mult*atr0
    elif sl_name=="retest_high":
        sl=e["retest_high"]+sl_mult*atr0
    elif sl_name=="struct5":
        sl=e["struct_high_5"]+sl_mult*atr0
    elif sl_name=="struct10":
        sl=e["struct_high_10"]+sl_mult*atr0
    else: raise ValueError(sl_name)
    tp_px=entry-tp*PIP
    end=min(len(df),i+1+window)
    outcome="TIME"; exit_px=float(df.close.iloc[end-1]); bars=window
    for j in range(i+1,end):
        hi=float(df.high.iloc[j]); lo=float(df.low.iloc[j])
        hit_sl=hi>=sl; hit_tp=lo<=tp_px
        if hit_sl and hit_tp:
            outcome="SL"; exit_px=sl; bars=j-i; break
        if hit_sl:
            outcome="SL"; exit_px=sl; bars=j-i; break
        if hit_tp:
            outcome="TP"; exit_px=tp_px; bars=j-i; break
    r=(entry-exit_px)/(sl-entry) if sl>entry else np.nan
    mae=(float(df.high.iloc[i+1:end].max())-entry)/(sl-entry) if end>i+1 else 0
    mfe=(entry-float(df.low.iloc[i+1:end].min()))/(sl-entry) if end>i+1 else 0
    return outcome,r,bars,mae,mfe

def main():
    Path("reports").mkdir(exist_ok=True)
    df=pd.read_csv(PATH)
    df["timestamp"]=pd.to_datetime(df["timestamp"],unit="ms")
    df=df.sort_values("timestamp").reset_index(drop=True)
    events=find_events(df)
    rows=[]
    # fixed candidates; buffer is expressed as ATR for structural stops
    for e in events:
        for sl_name, mults in [
            ("atr",[0.5,0.75,1.0,1.25]),
            ("retest_high",[0.0,0.10,0.25]),
            ("struct5",[0.0,0.10,0.25]),
            ("struct10",[0.0,0.10,0.25]),
        ]:
            for m in mults:
                for tp in [100,150,200]:
                    out,r,bars,mae,mfe=sim(df,e,sl_name,m,tp)
                    rows.append([e["date"],sl_name,m,tp,out,r,bars,mae,mfe,e["entry"],e["entry_atr"],e["break_level"],e["retest_high"],e["struct_high_5"],e["struct_high_10"]])
    ev=pd.DataFrame(rows,columns=["entry_date","sl_type","sl_mult","tp_pips","outcome","r","bars","mae_r","mfe_r","entry","entry_atr","break_level","retest_high","struct_high_5","struct_high_10"])
    ev["year"]=ev.entry_date.dt.year
    summaries=[]
    for (sl_type,sl_mult,tp),g in ev.groupby(["sl_type","sl_mult","tp_pips"],sort=False):
        for period,name in [(g[g.year<=2024],"discovery"),(g[g.year==2025],"validation"),(g[g.year>=2026],"oos")]:
            if len(period)==0: continue
            wins=(period.outcome=="TP").sum(); losses=(period.outcome=="SL").sum()
            gross_win=period.loc[period.r>0,"r"].sum(); gross_loss=-period.loc[period.r<0,"r"].sum()
            pf=gross_win/gross_loss if gross_loss>0 else np.nan
            summaries.append([sl_type,sl_mult,tp,name,len(period),wins,losses,(period.outcome=="TIME").sum(),
                wins/len(period),period.r.mean(),pf,period.r.sum(),period.bars.mean(),period.mae_r.median(),period.mfe_r.median()])
    sm=pd.DataFrame(summaries,columns=["sl_type","sl_mult","tp_pips","period","n","tp","sl","time","win_rate","expectancy_r","pf","total_r","avg_bars","median_mae_r","median_mfe_r"])
    ev.to_csv("reports/usdjpy_bear_exit_design_events_2026-10-07.csv",index=False,float_format="%.8f")
    sm.to_csv("reports/usdjpy_bear_exit_design_2026-10-07.csv",index=False,float_format="%.8f")
    print("EVENTS",len(events),"ROWS",len(ev))
    print(sm[sm.period=="oos"].sort_values(["expectancy_r","pf"],ascending=False).head(20).to_string(index=False))
if __name__=="__main__": main()
