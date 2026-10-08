# Cross-pair structural replay — 2026-10-08

## Method
Frozen notification signals were replayed against the repository H4 data for 12 pairs.

Entry is the next H4 open after the frozen signal.
Initial invalidation stop is the EMA20-touch candle extreme.
Exits are NOT fixed-pip:
- opposite 3-bar structural close
- EMA20 cross against the position
- market close after 20 H4 bars

Periods:
- Discovery: <= 2024
- Validation: 2025
- OOS: >= 2026

Entry filters were frozen from the prior cross-pair Discovery study:
- A: ema20_distance_atr <= 1.365379 AND bars_touch_to_signal <= 6
- B: signal_range_atr <= 1.151613 AND bars_touch_to_signal <= 6

## Results

| Filter | Period | Direction | N | Win rate | Mean pips | Total pips | PF | Pairs |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| A | Discovery | All | 79 | 39.24% | +0.71 | +56.2 | 1.034 | 12 |
| A | Validation | All | 21 | 33.33% | +18.21 | +382.5 | 2.009 | 10 |
| A | OOS | All | 13 | 53.85% | +18.45 | +239.8 | 2.609 | 8 |
| A | OOS | Long | 6 | 16.67% | -3.90 | -23.4 | 0.809 | 6 |
| A | OOS | Short | 7 | 85.71% | +37.60 | +263.2 | 10.895 | 5 |
| B | Discovery | All | 65 | 33.85% | -0.81 | -52.8 | 0.964 | 12 |
| B | Validation | All | 22 | 36.36% | +8.44 | +185.7 | 1.418 | 10 |
| B | OOS | All | 13 | 46.15% | +18.90 | +245.7 | 2.325 | 9 |
| B | OOS | Long | 7 | 28.57% | +9.29 | +65.0 | 1.439 | 6 |
| B | OOS | Short | 6 | 66.67% | +30.12 | +180.7 | 5.832 | 5 |

## Exit-reason distribution

A:
- Discovery: touch_stop 23, structure3_opposite 42, timeout 6, EMA20 8
- Validation: structure3_opposite 8, timeout 2, touch_stop 6, EMA20 5
- OOS: structure3_opposite 9, touch_stop 3, timeout 1

B:
- Discovery: touch_stop 17, structure3_opposite 35, timeout 7, EMA20 6
- Validation: structure3_opposite 8, timeout 2, touch_stop 7, EMA20 5
- OOS: structure3_opposite 10, touch_stop 2, timeout 1

## Interpretation
A and B both produce positive OOS expectancy under this structural replay. A is stronger on the aggregate OOS PF, but its OOS long side is weak while the short side is unusually strong. B is more balanced because its OOS long side remains profitable, while shorts are also strong.

The current OOS sample is only 13 trades per filter, so neither is production-approved. The next validation should therefore focus on whether the apparent short-side advantage is a reproducible market-regime/direction effect rather than a small-sample artifact.

No fixed-pip take-profit rule is used in this study.
