# H1 Currency Routing / Adoption Matrix

## Purpose
Convert completed H1 cross-pair validation into a routing decision without re-running discovery.

## Routing gate
A structure becomes a pair-specific research candidate when the same frozen structure/TP/SL is positive in both chronological OOS halves, PF > 1 in both halves, and total OOS trades >= 20.

This is a research-candidate gate, not production approval.

## Pair-specific candidates surviving the OOS gate

| Pair | Structure | TP | SL | OOS n | OOS first ExpR | OOS second ExpR | PF first | PF second | OOS cost @3p | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| USDJPY | pullback_reversal_rsi | 50 | 75 | 30 | +0.289 | +0.467 | 2.44 | 8.00 | +0.380R | candidate |
| EURJPY | pullback_reversal_rsi | 50 | 75 | 30 | +0.296 | +0.365 | 2.33 | 3.56 | +0.329R | candidate |
| GBPJPY | pullback_reversal | 75 | 50 | 26 | +0.615 | +0.538 | 3.00 | 2.40 | +0.540R | candidate |
| USDCHF | pullback_reversal_rsi | 50 | 50 | 35 | +0.105 | +0.125 | 1.50 | 2.00 | +0.190R | candidate |
| AUDUSD | pullback_reversal_rsi | 50 | 75 | 26 | +0.111 | +0.273 | 2.67 | 4.00 | +0.370R | candidate |
| AUDNZD | pullback_reversal | 50 | 50 | 21 | +0.300 | +0.364 | 4.00 | 3.00 | +0.478R | candidate |

The cost column is the combined OOS expectancy at a modeled 3-pip round-trip cost. The detailed cost sweep is stored separately.

## Pairs not promoted by this gate
EURUSD, GBPUSD, NZDUSD, USDCAD, EURGBP, AUDJPY.

These are not declared unusable. They are explicitly routed to separate structure research rather than being forced to use the JPY-derived architecture.

## Important caution
The six candidates are **not production-ready**. Some have weak/negative validation performance despite strong OOS performance. That is a robustness warning, not a reason to force universalization.

The next promotion gate therefore requires:
- OOS stability;
- realistic cost sensitivity;
- entry-timing validation;
- exit validation;
- notification replay / no-missed-signal audit;
- comparison against the existing production strategy.

## Interpretation
The JPY-derived pullback/reversal architecture does generalize, but not uniformly.

The correct architecture is:
1. retain a structure where OOS evidence supports it;
2. attach it only to the pairs that pass the routing gate;
3. send every other pair to its own structure-discovery track;
4. keep numeric TP/SL pair-specific when evidence supports different risk geometry;
5. never replace the existing production rule from an OOS result alone.

## Sources
- research/h1/results/cross_pair_validation.csv
- research/h1/results/cross_pair_regime_stability.csv
- research/h1/results/H1_CANDIDATE_COST_SENSITIVITY.md
- research/h1/results/H1_EDGE_SYNTHESIS.md

## Next research
- Entry timing validation for the six candidates.
- Exit-layer validation and cost robustness beyond the current fixed TP/SL test.
- Independent structure discovery for EURUSD, GBPUSD, NZDUSD, USDCAD, EURGBP, and AUDJPY.
- Promotion only after the final operational gate.
