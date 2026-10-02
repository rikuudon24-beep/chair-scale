#!/usr/bin/env python3
"""Causal MTF price-structure confluence research.

Research only. H4 is the decision timeframe. W1/D1/H1 features are aligned by
their candle CLOSE time, so only completed candles can influence an H4 signal.
No future H1 confirmation is used.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scripts.research_price_structure_transition import build_features, add_labels

ROOT = Path(__file__).resolve().parents[1]
PAIRS = ["usdjpy","eurjpy","gbpjpy","audjpy","eurusd","gbpusd","audusd","nzdusd","usdcad","usdchf","audnzd","eurgbp"]
PIP = {p:(0.01 if "jpy" in p else 0.0001) for p in PAIRS}
TARGETS = [50,100,150,200]

def load(tf,pair):
    f=ROOT/"data"/"market"/tf/f"{pair}.csv"
    if not f.exists(): return None
    d=pd.read_csv(f)
    d["timestamp"]=pd.to_datetime(d["timestamp"],unit="s",utc=True)
    return d.sort_values("timestamp").drop_duplicates("timestamp").reset_index(drop=True)

def prep(tf,pair):
    d=load(tf,pair)
    if d is None: return None
    z=build_features(d,pair)
    labs=add_labels(d,pair)
    keep=["timestamp","open","high","low","close"]
    feats=["descending_line_break_up_event","bull_structure_shift","bull_trendline_confirmation","bull_full_structure",
           "ascending_line_break_down_event","bear_structure_shift","bear_trendline_confirmation","bear_full_structure"]
    z=pd.concat([d[keep],z[feats],labs],axis=1)
    hours={"h1":1,"h4":4,"d1":24,"w1":168}[tf]
    z["available_at"]=z.timestamp+pd.to_timedelta(hours,unit="h")
    return z

def main():
    Path("reports").mkdir(exist_ok=True)
    rows=[]; missing=[]
    for pair in PAIRS:
        h4=prep("h4",pair); d1=prep("d1",pair); w1=prep("w1",pair); h1=prep("h1",pair)
        if any(x is None for x in [h4,d1,w1,h1]):
            missing.append(pair); continue
        # Rename HTF/H1 columns and causally merge only candles already closed.
        base=h4.copy()
        base["signal_time"]=base.available_at
        for name,src in [("d1",d1),("w1",w1),("h1",h1)]:
            cols=["available_at"]+[c for c in src.columns if c not in {"timestamp","open","high","low","close","available_at"}]
            q=src[cols].rename(columns={c:f"{name}_{c}" for c in cols if c!="available_at"})
            base=pd.merge_asof(base.sort_values("signal_time"),q.sort_values("available_at"),
                               left_on="signal_time",right_on="available_at",direction="backward")
        # H4's own signal features.
        for direction,evt in [("bull","descending_line_break_up_event"),("bear","ascending_line_break_down_event")]:
            m4=base[evt].fillna(False)
            for combo_name,mask in [
                ("h4_break",m4),
                ("d1_h4",m4 & base[f"d1_{evt}"].fillna(False)),
                ("w1_d1_h4",m4 & base[f"d1_{evt}"].fillna(False) & base[f"w1_{evt}"].fillna(False)),
                ("h1_d1_h4",m4 & base[f"d1_{evt}"].fillna(False) & base[f"h1_{evt}"].fillna(False)),
                ("w1_d1_h1_h4",m4 & base[f"d1_{evt}"].fillna(False) & base[f"w1_{evt}"].fillna(False) & base[f"h1_{evt}"].fillna(False)),
                ("structure_stack",m4 & base[f"d1_{'bull_structure_shift' if direction=='bull' else 'bear_structure_shift'}"].fillna(False) & base[f"w1_{'bull_structure_shift' if direction=='bull' else 'bear_structure_shift'}"].fillna(False)),
            ]:
                for target in TARGETS:
                    lab=f"hit_{'up' if direction=='bull' else 'dn'}_{target}"
                    a=base.loc[mask,lab]
                    if len(a)==0: continue
                    b=base.loc[~mask,lab]
                    ar=float(a.mean()); br=float(b.mean()) if len(b) else np.nan
                    period=np.where(base.loc[mask,"signal_time"].dt.year<=2024,"discovery",
                                    np.where(base.loc[mask,"signal_time"].dt.year==2025,"validation","oos"))
                    for per in ["discovery","validation","oos"]:
                        vals=a[period==per]
                        if len(vals):
                            base_rate=float(b[base.loc[~mask,"signal_time"].dt.year.map(lambda y: ("discovery" if y<=2024 else "validation" if y==2025 else "oos"))==per].mean()) if len(b) else np.nan
                            rows.append([per,pair,direction,combo_name,target,int(len(vals)),float(vals.mean()),base_rate,
                                         float(vals.mean()/base_rate) if np.isfinite(base_rate) and base_rate else np.nan])
    out=pd.DataFrame(rows,columns=["period","pair","direction","combo","target_pips","samples","hit_rate","baseline","lift"])
    out.to_csv("reports/mtf_structure_confluence_effects.csv",index=False,float_format="%.8f")

    # OOS pair robustness: keep only combinations with >=5 occurrences per pair.
    rob=[]
    if len(out):
        oos=out[out.period=="oos"].copy()
        for _,r in oos.iterrows():
            if int(r.samples) >= 5:
                rob.append([r.pair,r.direction,r.combo,int(r.target_pips),int(r.samples),float(r.hit_rate)])
    pd.DataFrame(rob,columns=["pair","direction","combo","target_pips","samples","oos_hit_rate"]).to_csv(
        "reports/mtf_structure_confluence_pair_robustness.csv",index=False,float_format="%.8f")
    summary=pd.DataFrame([{"pairs_with_all_tf":len(PAIRS)-len(missing),"missing_pairs":",".join(missing),"rows":len(out),"status":"PASS" if len(out) else "FAIL"}])
    summary.to_csv("reports/mtf_structure_confluence_summary.csv",index=False)
    print(summary.to_string(index=False))
    if len(out):
        print(out[out.period=="oos"].sort_values(["lift","samples"],ascending=[False,False]).head(40).to_string(index=False))

if __name__=="__main__":
    main()
