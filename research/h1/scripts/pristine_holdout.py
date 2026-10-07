#!/usr/bin/env python3
"""Locked forward holdout for frozen H1 candidates.

No parameter selection is performed here. The holdout starts strictly after the
research-data cutoff (2026-09-30 22:00 UTC), and only frozen rules are evaluated.
Signals in the final 72h are excluded because their outcomes are not complete.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from final_cost_exit_refinement import DATA, OUT, mask, sim

CUTOFF = pd.Timestamp("2026-09-30 22:00:00+00:00")
CANDS = {
    "eurjpy": ("pullback_reversal_rsi", "next_open", 100, 40, 72),
    "audnzd": ("pullback_reversal", "next_open", 60, 75, 72),
}
MIN_TRADES = 10

def main():
    rows = []
    for pair, (structure, entry, tp, sl, horizon) in CANDS.items():
        x = pd.read_parquet(DATA / f"{pair}.parquet").sort_index()
        latest = x.index.max()
        eval_end = latest - pd.Timedelta(hours=horizon)
        hold = x.loc[(x.index > CUTOFF) & (x.index <= eval_end)].copy()
        m = mask(hold, structure)
        for cost in (3.0, 5.0):
            import final_cost_exit_refinement as f
            old = f.COST
            f.COST = cost
            q = sim(hold, pair, m, entry, tp, sl, horizon)
            f.COST = old
            if q:
                n, win, pf, exp, net, tp_n, sl_n, time_n = q
            else:
                n = 0; win = pf = exp = net = float("nan")
                tp_n = sl_n = time_n = 0
            eligible = n >= MIN_TRADES
            passed = bool(eligible and pf > 1.0 and exp > 0.0)
            rows.append({
                "pair": pair, "structure": structure, "entry": entry,
                "tp": tp, "sl": sl, "horizon": horizon,
                "cost_pips": cost, "trades": n, "win_rate": win,
                "pf": pf, "expectancy_R": exp, "net_R": net,
                "tp_count": tp_n, "sl_count": sl_n, "time_count": time_n,
                "status": "PASS" if passed else ("INSUFFICIENT_SAMPLE" if not eligible else "FAIL"),
                "holdout_cutoff": str(CUTOFF),
                "evaluation_end": str(eval_end),
            })
    out = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT / "H1_PRISTINE_HOLDOUT.csv", index=False)
    lines = [
        "# H1 pristine forward holdout",
        "",
        f"Frozen rules only. No parameter selection or optimization is performed. Holdout starts strictly after {CUTOFF} and excludes the final 72 hours so every evaluated trade has a complete outcome window.",
        "",
        f"Minimum sample gate: {MIN_TRADES} trades per pair and positive PF/expectancy at both 3p and 5p costs.",
        "",
        "|Pair|Cost|N|Win|PF|ExpR|NetR|TP/SL/TIME|Status|",
        "|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for _, r in out.iterrows():
        lines.append(
            f"|{r.pair}|{int(r.cost_pips)}|{int(r.trades)}|"
            f"{r.win_rate:.3f}|{r.pf:.3f}|{r.expectancy_R:.3f}|{r.net_R:.2f}|"
            f"{int(r.tp_count)}/{int(r.sl_count)}/{int(r.time_count)}|{r.status}|"
        )
    (OUT / "H1_PRISTINE_HOLDOUT.md").write_text("\n".join(lines) + "\n")
    print(out.to_string(index=False))

if __name__ == "__main__":
    main()
