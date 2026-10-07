# Cross-Pair Entry Quality Research — 2026-10-07

## Purpose
Find entry-state features that improve notification entry quality across multiple H4 FX pairs. This is entry research only; no fixed-pip TP/exit rule is adopted.

## Data
- Source: `reports/notification_entry_quality_signals.csv`
- 387 frozen notification signals
- 12 pairs
- Directions: long / short / combined
- Discovery: <=2024
- Validation: 2025
- OOS: >=2026
- Outcome proxy: 100-pip reach from the existing frozen-entry replay. This is used only as a standardized entry-quality label; it is NOT a final exit rule.
- Thresholds are learned from Discovery only.

## Baseline 100-pip hit rate
| Direction | Validation | OOS |
|---|---:|---:|
| Long | 23.33% | 20.69% |
| Short | 27.27% | 26.09% |
| Combined | 25.40% | 23.08% |

## Stable candidate conditions
The following survived the strict screen: >=8 trades in both Validation/OOS, >=5 pairs in both, and hit rate >= the corresponding base rate in BOTH periods.

| Direction | Condition | Discovery-learned threshold | Validation | OOS | OOS mean P/L |
|---|---|---|---:|---:|---:|
| All | EMA20 distance ATR <= 1.365 & touch→signal bars <= 6 | 1.365 / 6 | 33.3% (21) | 30.8% (13) | +18.0 pips |
| All | touch→signal ATR <= 1.690 & pre6 move ATR >= 1.009 | 1.690 / 1.009 | 45.5% (11) | 30.0% (10) | +41.8 pips |
| All | signal range ATR <= 1.152 & touch→signal bars <= 6 | 1.152 / 6 | 31.8% (22) | 38.5% (13) | +23.0 pips |
| All | touch→signal ATR <= 1.690 & touch→signal bars <= 6 | 1.690 / 6 | 33.3% (27) | 29.4% (17) | +16.1 pips |
| All | signal body ratio >= 0.658 & EMA20 distance ATR <= 1.365 | 0.658 / 1.365 | 31.3% (16) | 33.3% (12) | +22.0 pips |

## Interpretation
The most interesting result is not a single high OOS hit rate. It is the repeated appearance of **timing/extension control**:

1. Do not enter when the signal is excessively far from the EMA20.
2. Do not let the EMA20-touch-to-trigger interval become too long.
3. Prefer a signal whose H4 range is not excessively expanded.
4. A moderate amount of movement before the signal can be useful when the time from touch to signal remains short.

The strongest practical candidate at this stage is:
**EMA20 distance not excessively expanded + trigger within 6 H4 bars of the touch.**

A second promising state is:
**moderate touch→signal displacement + short touch→signal timing.**

## Important rejection
Several conditions produced attractive OOS numbers but failed Validation, including combinations involving very large signal bodies, large EMA20 separation, or large pre6 movement. They are not adopted.

The apparent 60% OOS result for `pre6_move_atr high + bars_touch_to_signal low` is explicitly rejected because its OOS sample is only 10 and its Validation lift is weak. It is treated as a candidate for further testing, not a rule.

## Next research step
1. Rebuild the notification state machine with the stable entry-quality filters above.
2. Re-run the actual entry sequence across all pairs.
3. Evaluate structural/dynamic exits separately.
4. Require OOS improvement in expectancy/PF, not merely hit rate.
5. Only then promote a condition to notification status.

**Status: research candidate, not production notification rule.**
