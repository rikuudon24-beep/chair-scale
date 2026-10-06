# H1 Routed Live Operation

## Scope

This is the operational alert layer for the six H1 candidates that passed the frozen OOS routing gate:

| Pair | Rule | TP | SL | OOS n | 3-pip modeled OOS ExpR |
|---|---|---:|---:|---:|---:|
| USDJPY | pullback_reversal_rsi | 50p | 75p | 30 | +0.380R |
| EURJPY | pullback_reversal_rsi | 50p | 75p | 30 | +0.329R |
| GBPJPY | pullback_reversal | 75p | 50p | 26 | +0.540R |
| USDCHF | pullback_reversal_rsi | 50p | 50p | 35 | +0.190R |
| AUDUSD | pullback_reversal_rsi | 50p | 75p | 26 | +0.370R |
| AUDNZD | pullback_reversal | 50p | 50p | 21 | +0.478R |

These values come from the frozen routing matrix and are research evidence, not a guarantee of live profitability.

## Frozen H1 signal definitions

trend_down:
- H1 EMA20 < EMA50 < EMA200.

pullback_reversal:
- trend_down
- completed higher-timeframe H4 candle bullish
- completed higher-timeframe D1 candle bullish

pullback_reversal_rsi:
- trend_down
- completed higher-timeframe D1 candle bullish
- RSI14 change over the last 6 H1 bars > +3

Higher-timeframe context follows the same one-bar causal shift used by research/h1/scripts/build_dataset.py.

## Execution/notification protocol

1. Evaluate only the latest completed H1 candle.
2. Alert only when the frozen condition transitions from false to true; persistent condition bars do not create repeated entry alerts.
3. Entry candidate is the next H1 open.
4. TP/SL are calculated from the actual next-H1-open entry price.
5. Position state is persisted in reports/h1_live_positions.csv.
6. Exit monitoring uses completed H1 candles.
7. If TP and SL are both touched in the same completed candle, SL is treated as first/conservative.
8. Alerts are persisted in reports/h1_live_alerts.csv.
9. GitHub Actions runs hourly at minute 11 UTC and can also be run manually.
10. Durable GitHub Issues are created for new ENTRY / EXIT_TP / EXIT_SL events.
11. A ChatGPT hourly condition-watch checks the alert ledger and notifies the user when a new alert appears.

## Safety boundary

This is an alert/monitoring system only. It does not place broker orders.

The six pairs are research candidates, not production-proven strategies. The repository's promotion gate still requires ongoing live/replay validation, execution-quality checks, and comparison against the existing production H4 rule.

## Canonical implementation

- research/h1/scripts/monitor_h1_live.py
- .github/workflows/fx-h1-routed-live.yml
- reports/h1_live_positions.csv
- reports/h1_live_alerts.csv
- research/h1/results/H1_CURRENCY_ROUTING_MATRIX.md
- research/h1/results/H1_CANDIDATE_COST_SENSITIVITY.md
