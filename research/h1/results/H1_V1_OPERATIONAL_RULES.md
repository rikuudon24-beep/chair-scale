# H1 v1 operational rules

Frozen after chronological mining/validation. This is an alert-only system, not broker execution.

## Active pairs

| Pair | Signal rule | Entry | TP | SL | Horizon |
|---|---|---|---:|---:|---:|
| EURJPY | trend_down & d1_bull & rsi_up6 & dist_ema20<=0 & body_range>=0.6 | next H1 open | 100p | 40p | 72h |
| USDCHF | trend_down & d1_bull & rsi_up6 & adx>=25 & ema20_slope>=0 | confirm_1bar | 40p | 40p | 48h |
| AUDNZD | trend_down & h4_bull & d1_bull | next H1 open | 60p | 75p | 72h |

Definitions:
- trend_down = H1 EMA20 < EMA50 < EMA200.
- d1_bull / h4_bull use the prior completed HTF candle, matching dataset construction.
- rsi_up6 = RSI14 current value - RSI14 six H1 bars earlier > 3.
- dist_ema20 = (close - EMA20) / ATR14.
- body_range = abs(close-open) / (high-low).
- adx is H1 ADX14.
- ema20_slope is the H1 EMA20 percentage change over one bar.
- next_open = next H1 candle open.
- confirm_1bar = if the next H1 close is above the signal candle high, enter at the following H1 open.
- TP/SL are measured from actual entry.
- Same-candle TP+SL is treated as SL first, matching backtests.
- Non-overlapping lifecycle per pair.
- TIME exit is evaluated at the horizon-bar close.

## Excluded
USDJPY: mined filter OOS sample was only 2 trades; insufficient to promote.
GBPJPY: mined filter remained only marginal after 5-pip cost; excluded from v1.
AUDUSD: prior frozen candidate failed OOS and remains excluded.

## Holdout policy
The pristine holdout is not used to optimize these rules. It will accumulate prospectively after the 2026-09-30 cutoff. Its current state is insufficient sample, not pass/fail.

## Promotion policy
Do not alter these rules based on live outcomes. Any change creates v1.1 and requires a new chronological research cycle.
