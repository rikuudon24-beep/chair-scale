# USDJPY Bear State Transition — OOS Failure Analysis (2026-10-07)

## Scope
Current causal event definition:
- H4 close below prior 20-bar low
- extension >= 0.10 ATR within 10 bars
- retest within 15 bars, tolerance <= 0.15 ATR
- retest close remains below breakout level
- compare retest entry vs first subsequent 2-consecutive-bear-close timing entry
- outcome: WIN if new 5-bar low and >=0.75 ATR favorable close before a 3-bar structure break; LOSS if structure breaks first; TIME otherwise.

## OOS timed sample
N=5:
- WIN: 1
- LOSS: 4
- TIME: 0
- nominal win rate: 20%
This is too small for a strategy conclusion.

## Case-level observation
The sole OOS WIN (2026-01-27) had:
- EMA20 distance: -2.27 ATR
- EMA20 slope: -0.56 ATR/3 bars
- breakout extension: 0.22 ATR
- retest depth: 1.19 ATR
- distance below breakout at entry: 0.62 ATR
- close position: 0.40

OOS LOSS cases:
- 2026-04-01: extension 0.91 ATR, retest depth 0.28 ATR, close position ~0.00
- 2026-04-09: extension 1.45 ATR, retest depth 0.47 ATR, EMA20 distance only -0.26 ATR, EMA20 slope -0.06
- 2026-08-04: extension 0.71 ATR, retest failed to reach breakout level cleanly (retest depth -0.11 ATR), close position 0.54
- 2026-09-08: extension 1.82 ATR, retest depth 0.54 ATR, close position 0.05

## Research interpretation
Potential failure modes:
1. Breakout has already extended too far before the timed entry.
2. EMA20 bearish separation is insufficient / momentum has flattened.
3. The retest does not genuinely test the broken level.
4. Entry candle closes too near its low, potentially representing late/chasing entry rather than a renewed structural break.

## Candidate filters — NOT validated
- Avoid entries after very large breakout extension.
- Require negative EMA20 slope with sufficient magnitude.
- Require a genuine retest of the broken level rather than a shallow/non-test.
- Avoid extremely low close-position entries unless accompanied by a fresh structural break.

These are hypotheses only. OOS N=5 is insufficient to adopt any filter.

## Next test
Use the full Discovery/Validation sample to derive thresholds without looking at OOS outcomes, then lock the rules and evaluate OOS once. Test single filters first, then 2-condition combinations, and require stability across periods.
