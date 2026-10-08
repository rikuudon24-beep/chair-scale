# Structural exit comparison — 2026-10-08

Entry filters are unchanged:
- A: ema20_distance_atr <= 1.365379 AND bars_touch_to_signal <= 6
- B: signal_range_atr <= 1.151613 AND bars_touch_to_signal <= 6

Common:
- next H4 open entry
- touch-candle extreme initial stop
- 20 H4 bar timeout
- no fixed-pip TP

Exit variants:
1. both = opposite 3-bar structure break OR EMA20 cross
2. structure = opposite 3-bar structure break only
3. ema = EMA20 cross only

| Filter | Exit | Validation N | Validation WR | Validation mean | Validation PF | OOS N | OOS WR | OOS mean | OOS PF |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | both | 21 | 33.3% | +18.21 | 2.009 | 13 | 53.8% | +18.45 | 2.609 |
| A | structure | 21 | 38.1% | +24.02 | 2.292 | 13 | 53.8% | +18.45 | 2.609 |
| A | EMA20 | 21 | 33.3% | +18.28 | 1.920 | 13 | 53.8% | +32.72 | 3.359 |
| B | both | 22 | 36.4% | +8.44 | 1.418 | 13 | 46.2% | +18.90 | 2.325 |
| B | structure | 22 | 40.9% | +13.98 | 1.675 | 13 | 46.2% | +18.90 | 2.325 |
| B | EMA20 | 22 | 36.4% | +12.85 | 1.645 | 13 | 61.5% | +39.25 | 4.193 |

## Current interpretation
EMA20-only is currently the strongest exit candidate on OOS for both frozen entry filters.

However, the OOS sample is only 13 trades per filter. The result is therefore a candidate, not a production rule.

Next validation should test pair concentration and whether EMA20-only remains positive when individual high-contribution pairs are removed. No new entry threshold should be introduced until that robustness check is completed.
