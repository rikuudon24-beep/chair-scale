# H1 Currency Routing / Adoption Matrix

## Purpose
Convert already-completed H1 cross-pair validation into a routing decision without re-running discovery.

## Rule
A structure is eligible for promotion to a pair-specific research candidate when the same frozen structure/TP/SL is positive in both chronological OOS halves, PF > 1 in both halves, and total OOS trades >= 20.

This is a routing gate, not a production approval. Final promotion still requires cost sensitivity, entry-timing validation, and operational notification replay.

## Pair-specific candidates surviving the gate

| Pair | Structure | TP | SL | OOS n | OOS first ExpR | OOS second ExpR | PF first | PF second | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| USDJPY | pullback_reversal_rsi | 50 | 75 | 30 | +0.289 | +0.467 | 2.44 | 8.00 | candidate |
| EURJPY | pullback_reversal_rsi | 50 | 75 | 30 | +0.296 | +0.365 | 2.33 | 3.56 | candidate |
| GBPJPY | pullback_reversal | 75 | 50 | 26 | +0.615 | +0.538 | 3.00 | 2.40 | candidate |
| USDCHF | pullback_reversal_rsi | 50 | 50 | 35 | +0.105 | +0.125 | 1.50 | 2.00 | candidate |
| AUDUSD | pullback_reversal_rsi | 50 | 75 | 26 | +0.111 | +0.273 | 2.67 | 4.00 | candidate |
| AUDNZD | pullback_reversal | 50 | 50 | 21 | +0.300 | +0.364 | 4.00 | 3.00 | candidate |

## Pairs not promoted by this gate
EURUSD, GBPUSD, NZDUSD, USDCAD, EURGBP, AUDJPY.

These are not declared unusable. They are explicitly routed to separate research rather than being forced to use the JPY-derived structure.

## Interpretation
The JPY-derived pullback/reversal architecture does generalize, but not uniformly. It is therefore incorrect to require universal cross-pair performance before moving forward.

The correct architecture is:
1. retain a structure where OOS evidence supports it;
2. attach it only to the pairs that pass the routing gate;
3. send all other pairs to their own structure-discovery track;
4. keep numeric TP/SL pair-specific when the evidence supports different risk geometry.

## Source
- research/h1/results/cross_pair_validation.csv
- research/h1/results/cross_pair_regime_stability.csv
- research/h1/results/H1_EDGE_SYNTHESIS.md

## Next research
- Run cost sensitivity on the six surviving pair-specific candidates.
- Validate entry timing and notification state transitions.
- Search independent structures for the six non-promoted pairs.
- Do not replace the existing production rule until the candidate passes the final promotion gate.
