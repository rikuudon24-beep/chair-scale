#!/usr/bin/env python3
"""H1 event study + conservative trade simulation across multiple candidate families."""
import json,math
from pathlib import Path
import numpy as np,pandas as pd

ROOT=Path(__file__).resolve().parents[3]
CFG=json.loads((ROOT/"research/h1/config.json").read_text())
DATA=ROOT/"research/h1/results/datasets"; OUT=ROOT/"research/h1/results"; OUT.mkdir(parents=True,exist_ok=True)
PIP=lambda p:0.01 if "jpy" in p else 0.0001

def candidates(x):
    return {
      "trend_pullback_long": x.trend_up & (x.adx14>=20) & x.rsi14.between(45,65) & x.dist_ema20_atr.between(-0.75,0.25) & (x.macd_hist>0) & (x.body>0),
      "trend_pullback_short": x.trend_down & (x.adx14>=20) & x.rsi14.between(35,55) & x.dist_ema20_atr.between(-0.25,0.75) & (x.macd_hist<0) & (x.body<0),
      "trend_breakout_long": x.trend_up & x.break20_up & (x.body_range>=0.55) & (x.atr_pct>x.atr_pct.rolling(200).median()),
      "trend_breakout_short": x.trend_down & x.break20_down & (x.body_range>=0.55) & (x.atr_pct>x.atr_pct.rolling(200).median()),
      "momentum_long": (x.ema20>x.ema50)&(x.ema50>x.ema200)&(x.adx14>=20)&x.rsi14.between(55,72)&(x.macd_hist>0)&(x.roc12>0),
      "momentum_short": (x.ema20<x.ema50)&(x.ema50<x.ema200)&(x.adx14>=20)&x.rsi14.between(28,45)&(x.macd_hist<0)&(x.roc12<0),
      "meanrev_long": (x.rsi14<30)&(x.close<x.bb_lower)&(x.bb_pct<0)&(x.dist_ema20_atr<-1.0)&(x.adx14<25),
      "meanrev_short": (x.rsi14>70)&(x.close>x.bb_upper)&(x.bb_pct>1)&(x.dist_ema20_atr>1.0)&(x.adx14<25),
      "h4_aligned_long": (x.h4_close>x.h4_open)&x.trend_up&(x.d1_close>x.d1_open),
      "h4_aligned_short": (x.h4_close<x.h4_open)&x.trend_down&(x.d1_close<x.d1_open)
    }

def split(df):
    n=len(df); a=int(n*0.60); b=int(n*0.20)
    return df.iloc[:a],df.iloc[a:a+b],df.iloc[a+b:]

def simulate(x,signal,long,sl,tp,H,spread=1.5,pair=None):
    idx=np.flatnonzero(signal.to_numpy())
    rows=[]
    hi=x.high.to_numpy(); lo=x.low.to_numpy(); op=x.open.to_numpy(); cl=x.close.to_numpy(); times=x.index
    ps=PIP(pair) if pair else 0.0001
    for i in idx:
        if i+1>=len(x) or i+H>=len(x): continue
        entry=op[i+1]
        if long: stop=entry-sl*ps; target=entry+tp*ps
        else: stop=entry+sl*ps; target=entry-tp*ps
        outcome=None; exit_price=None; exit_i=None
        for j in range(i+1,min(len(x),i+1+H)):
            hit_sl=(lo[j]<=stop) if long else (hi[j]>=stop)
            hit_tp=(hi[j]>=target) if long else (lo[j]<=target)
            if hit_sl and hit_tp:
                outcome="loss_conservative"; exit_price=stop; exit_i=j; break
            if hit_sl: outcome="loss"; exit_price=stop; exit_i=j; break
            if hit_tp: outcome="win"; exit_price=target; exit_i=j; break
        if outcome is None:
            exit_i=min(len(x)-1,i+H); exit_price=cl[exit_i]; outcome="time"
        pips=((exit_price-entry)/ps if long else (entry-exit_price)/ps)-spread
        rows.append((times[i],times[exit_i],pips,outcome))
    return pd.DataFrame(rows,columns=["signal_time","exit_time","pips","outcome"])

def stats(t):
    if t.empty: return {"trades":0}
    wins=t.pips>0; gross_win=t.loc[wins,"pips"].sum(); gross_loss=-t.loc[~wins,"pips"].sum()
    eq=t.pips.cumsum(); peak=eq.cummax(); dd=(eq-peak).min()
    return {"trades":int(len(t)),"win_rate":float(wins.mean()),"profit_factor":float(gross_win/gross_loss) if gross_loss>0 else None,"expectancy_pips":float(t.pips.mean()),"total_pips":float(t.pips.sum()),"max_drawdown_pips":float(-dd)}

def main():
    records=[]; trade_store={}
    for fp in sorted(DATA.glob("*.parquet")):
        pair=fp.stem
        x=pd.read_parquet(fp).sort_index()
        cs=candidates(x)
        for name,s in cs.items():
            long=name.endswith("long")
            # Discover a compact TP/SL grid; do not select by win rate alone.
            for tp,sl,H in [(50,25,24),(75,35,48),(100,50,72),(150,75,120)]:
                tr=simulate(x,s,long,sl,tp,H,1.5); tr["pair"]=pair; tr["rule"]=name; tr["tp"]=tp; tr["sl"]=sl; tr["H"]=H
                for split_name,part in zip(["discovery","validation","oos"],split(tr)):
                    st=stats(part); st.update({"pair":pair,"rule":name,"tp":tp,"sl":sl,"H":H,"split":split_name}); records.append(st)
    res=pd.DataFrame(records)
    res.to_csv(OUT/"candidate_results.csv",index=False)
    # Freeze candidates only after discovery: require sample size and PF/expectancy, then inspect validation/OOS.
    d=res[res.split=="discovery"].copy()
    eligible=d[(d.trades>=30)&(d.profit_factor.fillna(0)>=1.10)&(d.expectancy_pips>0)].sort_values(["expectancy_pips","profit_factor"],ascending=False).head(30)
    val=res[res.split.isin(["validation","oos"])].merge(eligible[["pair","rule","tp","sl","H"]],on=["pair","rule","tp","sl","H"],how="inner")
    val.to_csv(OUT/"frozen_candidate_followup.csv",index=False)
    summary=val.groupby(["rule","tp","sl","H","split"],dropna=False).agg(trades=("trades","sum"),win_rate=("win_rate","mean"),pf=("profit_factor","mean"),expectancy=("expectancy_pips","mean"),total_pips=("total_pips","sum")).reset_index()
    summary.to_csv(OUT/"frozen_candidate_summary.csv",index=False)
    lines=["# H1 Research Results","",f"- candidate rows: {len(res)}",f"- discovery-eligible rows: {len(eligible)}",f"- follow-up rows: {len(val)}","", "Selection rule: discovery only; minimum 30 trades, PF >= 1.10 and positive expectancy. Validation/OOS are not used to select rules.","","## Validation/OOS follow-up",""]
    if summary.empty: lines.append("No discovery candidate passed the pre-registered gate.")
    else: lines += ["|Rule|TP|SL|H|Split|Trades|Win rate|PF|Expectancy pips|Total pips|","|---|---:|---:|---:|---|---:|---:|---:|---:|---:|"] + [
      f"|{r.rule}|{r.tp}|{r.sl}|{r.H}|{r.split}|{int(r.trades)}|{r.win_rate:.3f}|{r.pf if pd.notna(r.pf) else 'NA'}|{r.expectancy:.2f}|{r.total_pips:.1f}|" for _,r in summary.iterrows()]
    (OUT/"RESEARCH_RESULTS.md").write_text("\n".join(lines)+"\n")
    print("\n".join(lines))
if __name__=="__main__": main()
