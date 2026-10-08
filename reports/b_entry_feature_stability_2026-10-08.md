# B条件 勝敗特徴の再現性チェック — 2026-10-08

## Scope
B entry filter was kept frozen:
- signal_range_atr <= 1.151613
- bars_touch_to_signal <= 6

No new threshold was introduced.

This pass analyzes the existing notification signal dataset across Discovery (<=2024), Validation (2025), and OOS (>=2026).

## Important limitation
The win/loss feature comparison below uses the existing `pnl_50 / hit_50` labels in notification_entry_quality_signals.csv. It is a diagnostic for entry-quality characteristics, not the final EMA20-only exit result. Therefore these findings do NOT justify changing the live/production exit rule.

## Overall B sample
- Discovery: N=65
- Validation: N=22
- OOS: N=13

## Key result
No single entry feature showed a stable winner-vs-loser separation with the same direction across all three periods.

### Overall win/loss feature means

| Period | Feature | Winners | Losers |
|---|---|---:|---:|
| Discovery | signal_body_ratio | 0.599 | 0.601 |
| Discovery | ema20_distance_atr | 1.264 | 0.965 |
| Discovery | touch_to_signal_atr | 1.335 | 0.798 |
| Discovery | pre6_move_atr | 0.700 | 0.073 |
| Validation | signal_body_ratio | 0.511 | 0.563 |
| Validation | ema20_distance_atr | 0.974 | 1.109 |
| Validation | touch_to_signal_atr | 0.903 | 0.970 |
| Validation | pre6_move_atr | 0.173 | 0.570 |
| OOS | signal_body_ratio | 0.716 | 0.366 |
| OOS | ema20_distance_atr | 1.269 | 1.319 |
| OOS | touch_to_signal_atr | 1.222 | 0.751 |
| OOS | pre6_move_atr | 0.955 | 0.776 |
| OOS | bars_touch_to_signal | 2.375 | 3.600 |

## Interpretation
1. Discovery suggested that stronger prior movement and larger EMA/touch separation helped winners.
2. Validation reversed several of those relationships.
3. OOS again showed stronger body ratio, larger touch-to-signal distance, and fewer bars among winners.
4. Because the direction is not stable from Discovery -> Validation -> OOS, these are not yet robust filters.

## Directional check
Short-side OOS winners were characterized by:
- body ratio: 0.845 vs 0.656 for losses
- body ATR: 0.800 vs 0.729
- bars: 2.2 vs 3.0

However, Discovery/Validation do not reproduce all of these relationships consistently. Therefore no short-only filter is adopted.

## Decision
- Keep B entry filter unchanged.
- Keep EMA20-only exit candidate unchanged.
- Do NOT add body-ratio, EMA-distance, touch-distance, pre6-move, or bars thresholds yet.
- Do NOT switch to short-only entries.
- Next research target: test whether the existing B+EMA20 exit result remains robust under rolling time windows / walk-forward evaluation, rather than optimizing thresholds on the current OOS sample.

## Status
B remains the leading generalized research candidate, but it is not production-approved.
