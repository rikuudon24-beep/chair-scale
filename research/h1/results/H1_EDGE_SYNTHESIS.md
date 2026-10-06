# H1 Edge Synthesis

## Purpose
Consolidate already-completed H1 research into the next non-duplicative research target: a robust, notification-ready entry/exit framework. This file is a synthesis, not a replacement for the underlying result files.

## Source-of-truth
- Repository: rikuudon24-beep/chair-scale
- Branch: fx-h1-research
- H1 protocol: signal at confirmed H1 close; entry at next H1 open; non-overlapping trades; same-candle TP/SL is treated conservatively as SL.
- Split: chronological discovery -> validation -> OOS. Discovery nominates candidates; validation/OOS are not used for selection.

## Findings that survive existing research

### 1. H1 generic candidates are not robust enough by themselves
The main H1 candidate study shows substantial validation/OOS instability. Examples include momentum_long TP75/SL35/H48 (validation PF 1.369, OOS PF 0.585) and trend_breakout_long TP100/SL50/H72 (validation PF 0.805, OOS PF 0.866). Therefore a simple generic momentum/breakout alert should not be frozen as a production rule.

### 2. Price-structure state changes are a strong precursor family
The precursor study repeatedly finds 20-period structural breaks before +100-pip moves. Examples:
- USDCAD short break20_up: lift +0.405
- EURUSD short break20_up: +0.396
- GBPUSD long break20_down: +0.351
- EURJPY long break20_down: +0.304
- GBPJPY long break20_down: +0.267
- USDJPY long break20_down: +0.241
This is evidence for using structural transition as the trigger layer rather than treating trend state alone as an entry.

### 3. Momentum regime change adds information
Before large moves, RSI14 differs materially from baseline. Long examples commonly show RSI below baseline (e.g. GBPJPY -8.93, EURJPY -12.31, USDJPY -9.27 median points), while short examples often show RSI above baseline. The existing stable-JPY work specifically uses RSI14 change over 6 H1 bars > 3 as a momentum-recovery filter.

### 4. H4/D1 context matters, but exact EMA definitions can overfit
The stable-JPY context robustness study shows the simple candle-based H4/D1 context is more stable than exact EMA relationships in that experiment. The EMA20>EMA200 context failed OOS for EURJPY and GBPJPY despite strong discovery/validation values. Do not hard-code EMA alignment as mandatory without revalidation.

### 5. JPY long pullback-reversal is the strongest existing H1 trade-quality branch
For USDJPY/EURJPY/GBPJPY, pullback_reversal_rsi with TP50/SL75/H48 produced OOS PF 4.60/4.60/5.00 and win rates 74.2%/76.7%/80.0%, with OOS samples of 31/30/25 trades respectively. These are promising but still too small to call proven.

### 6. Frozen stable-JPY filter is promising but sample-limited
Condition:
trend_down & h4_bull & d1_bull & ADX>=20 & RSI14 change over 6 H1 bars > 3.

With TP40/SL100/H48, existing OOS win rates are USDJPY 70.6%, EURJPY 100.0%, GBPJPY 89.5%; however OOS samples are only 17/18/19 trades. The OOS-first/second-half stability study remains positive across both halves, but each half contains only 7-11 trades. Treat as hypothesis-level evidence.

## Working research hypothesis
The strongest common architecture currently supported by the repository is:

1. Higher-timeframe context establishes directional permission.
2. H1 enters a pullback/structural-down state.
3. A structural reversal/break occurs.
4. RSI/ADX confirm momentum regime change.
5. Entry is taken only after the reversal is confirmed, not merely because trend state exists.
6. Exit is based on empirically observed MFE/MAE and should be tested as a separate layer.

This should be generalized beyond JPY before being frozen.

## Next non-duplicative tests
1. Extract exact feature definitions from the existing H1 scripts and lock them into a notification specification.
2. Cross-pair test the common architecture across the existing universe, keeping discovery/validation/OOS separation.
3. Require positive OOS in both chronological halves and a minimum OOS trade count before promotion.
4. Test entry timing variants: next-open versus confirmed structural-break entry, without look-ahead.
5. Test exit variants separately: fixed TP/SL, ATR-scaled stop, and MFE/MAE-derived targets.
6. Add transaction-cost sensitivity and spread/slippage assumptions.
7. Promote only rules that remain positive across multiple pairs/regimes; pair-specific rules remain research candidates.
8. Convert the promoted rule into a state machine: WATCH -> SETUP -> ENTRY -> POSITION -> EXIT/INVALIDATED, so entry and exit notifications are managed by one monitor.

## Status
This synthesis does not declare a production-ready trading edge. The existing repository itself states that verified trading performance is not yet established. The purpose here is to narrow the next research to robustness, generalization, execution timing, and notification conversion without repeating completed discovery work.


## 2026-10-06 routing update
- The JPY-derived H1 pullback/reversal architecture was tested across the remaining pairs rather than being forced universal.
- Six pair-specific candidates passed the frozen OOS routing gate: USDJPY, EURJPY, GBPJPY, USDCHF, AUDUSD, AUDNZD.
- A modeled 3-pip round-trip cost still left positive combined OOS expectancy for all six candidates.
- EURUSD, GBPUSD, NZDUSD, USDCAD, EURGBP, and AUDJPY did not pass that gate and are now explicitly routed to independent research.
- The first independent non-JPY discovery run found no candidates meeting the strict 100-pip/48H1 gate (n>=50, hit>=55%, Wilson LCB>=45%). This is a negative result, not a failure of the project: the next branch must search different structures/targets rather than loosen the gate after seeing results.
