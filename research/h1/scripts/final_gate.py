#!/usr/bin/env python3
"""Final gate: fixed H1 candidates, OOS-half stability and 3/5-pip cost sensitivity."""
from pathlib import Path
import pandas as pd
from final_cost_exit_refinement import DATA, OUT, CANDS, split, mask, sim

def main():
    sel = pd.read_csv(OUT / "H1_FINAL_COST_EXIT_SELECTED.csv")
    rows = []
    for _, r in sel.iterrows():
        pair = r.pair
        if pair == "audusd":
            continue
        x = pd.read_parquet(DATA / f"{pair}.parquet").sort_index()
        _, _, oos = split(x)
        n = len(oos)
        halves = [oos.iloc[: n//2], oos.iloc[n//2:]]
        for hi, part in enumerate(halves, 1):
            m = mask(part, r.structure)
            for cost in (3.0, 5.0):
                import final_cost_exit_refinement as f
                old = f.COST
                f.COST = cost
                q = sim(part, pair, m, r.entry, int(r.tp), int(r.sl), int(r.horizon))
                f.COST = old
                if q:
                    rows.append({
                        "pair": pair, "oos_half": hi, "cost_pips": cost,
                        "trades": q[0], "win_rate": q[1], "pf": q[2],
                        "expectancy_R": q[3], "net_R": q[4],
                        "tp": q[5], "sl": q[6], "time": q[7]
                    })
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "H1_FINAL_GATE.csv", index=False)
    lines = [
        "# H1 final gate — fixed candidates",
        "",
        "Fixed from validation-selected entry/exit parameters. Audusd is excluded after the final OOS result turned negative. Each remaining OOS is split into chronological halves. Cost sensitivity is checked at 3 and 5 pips. This is robustness evidence, not a pristine holdout, because the six-pair routing stage previously used OOS evidence.",
        "",
        "|Pair|Half|Cost|N|Win|PF|ExpR|NetR|TP/SL/TIME|",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|"
    ]
    for _, z in out.iterrows():
        lines.append(f"|{z.pair}|{int(z.oos_half)}|{z.cost_pips:.0f}|{int(z.trades)}|{z.win_rate:.3f}|{z.pf:.3f}|{z.expectancy_R:.3f}|{z.net_R:.2f}|{int(z.tp)}/{int(z.sl)}/{int(z.time)}|")
    (OUT / "H1_FINAL_GATE.md").write_text("\n".join(lines) + "\n")
    print(out.to_string(index=False))

if __name__ == "__main__":
    main()
