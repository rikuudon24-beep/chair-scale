# Directional A/B structural candidate — 2026-10-08

This candidate combines the two previously frozen entry filters without creating new thresholds:

- Long: Filter B = signal_range_atr <= 1.151613 AND bars_touch_to_signal <= 6
- Short: Filter A = ema20_distance_atr <= 1.365379 AND bars_touch_to_signal <= 6

The same structural replay is used:
- next H4 open entry
- touch-candle extreme as initial invalidation stop
- opposite 3-bar structure close
- EMA20 cross against position
- 20-bar timeout
- no fixed-pip take-profit

| Period | N | Win rate | Mean pips | Total pips | PF | Long | Short |
|---|---:|---:|---:|---:|---:|---:|---:|
| Discovery | 82 | 36.59% | +0.45 | +36.6 | 1.022 | 36 | 46 |
| Validation | 23 | 34.78% | +15.55 | +357.6 | 1.813 | 7 | 16 |
| OOS | 14 | 57.14% | +23.44 | +328.2 | 2.880 | 7 | 7 |

Interpretation:
- The directional combination improves OOS PF versus either all-direction filter alone.
- Validation is also positive.
- Discovery is approximately flat, so this is not a uniformly strong historical edge.
- OOS sample size is small (14), therefore this is a research candidate, not a production rule.
- Next check: contribution by currency pair and whether the OOS result is concentrated in one or two pairs.
