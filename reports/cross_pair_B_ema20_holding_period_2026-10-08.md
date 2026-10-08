# B + EMA20 exit holding-period check — 2026-10-08

Entry is frozen:
- signal_range_atr <= 1.151613
- bars_touch_to_signal <= 6

Exit is frozen except for maximum holding period:
- touch-candle extreme initial stop
- EMA20 cross against position
- timeout at 20, 30, or 40 H4 bars
- no fixed-pip TP

| Max hold | Period | N | Win rate | Mean pips | PF |
|---:|---|---:|---:|---:|---:|
| 20 | Discovery | 65 | 33.8% | +0.10 | 1.004 |
| 20 | Validation | 22 | 36.4% | +12.85 | 1.645 |
| 20 | OOS | 13 | 61.5% | +39.25 | 4.193 |
| 30 | Discovery | 65 | 32.3% | -2.24 | 0.912 |
| 30 | Validation | 22 | 36.4% | +4.37 | 1.219 |
| 30 | OOS | 13 | 53.8% | +38.39 | 3.730 |
| 40 | Discovery | 65 | 32.3% | -0.84 | 0.967 |
| 40 | Validation | 22 | 36.4% | +3.51 | 1.176 |
| 40 | OOS | 13 | 53.8% | +39.45 | 3.805 |

## Conclusion
20 H4 bars is currently the strongest holding cap across Validation and OOS, while longer caps reduce PF. Keep 20 as the frozen research candidate.

This is not a production approval because OOS N=13 remains small.
