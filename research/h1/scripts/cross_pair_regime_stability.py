import json, os
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
res = os.path.join(ROOT, "research/h1/results")
inp = os.path.join(res, "cross_pair_validation.csv")
out_csv = os.path.join(res, "cross_pair_regime_stability.csv")
out_md = os.path.join(res, "cross_pair_regime_stability.md")

df = pd.read_csv(inp)
# Only fixed structures/TP-SL combinations from the prior cross-pair test.
# Split each pair's OOS trades chronologically into two halves by trade count.
# This is a stability diagnostic, not a new rule-selection stage.
oos = df[df["split"] == "oos"].copy()
rows = []
for (pair, structure, tp, sl), g in oos.groupby(["pair","structure","tp","sl"], sort=False):
    # cross_pair_validation.csv contains aggregate metrics only, so this diagnostic
    # can only operate at pair level from the available output. Mark as unavailable.
    rows.append({
        "pair": pair, "structure": structure, "tp": tp, "sl": sl,
        "status": "requires_trade_level_oos_log"
    })
pd.DataFrame(rows).to_csv(out_csv, index=False)
with open(out_md, "w", encoding="utf-8") as f:
    f.write("# Cross-pair regime stability\n\n")
    f.write("The current cross-pair result stores only aggregate OOS metrics per pair/structure/TP/SL. ")
    f.write("A chronological first-half/second-half OOS stability test requires trade-level OOS records. ")
    f.write("No rule is selected or frozen by this diagnostic.\n")
