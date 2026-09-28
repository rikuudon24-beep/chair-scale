# H1 Research Status

- Repository: `rikuudon24-beep/chair-scale`
- Branch: `fx-h1-research`
- H4 mainline: unchanged; H4/D1 source files are read-only inputs.
- H1 acquisition: implemented with full CSV consolidation and OHLC audit.
- Feature pipeline: implemented for EMA/SMA, RSI, ATR, ADX, MACD, Bollinger Bands, ROC, price structure and H4/D1/W1 context.
- Forward labels: 50/100/150/200/300 pips over 24/48/72/120 H1 bars.
- Backtest: next-bar-open entry, conservative same-bar TP/SL handling, non-overlapping trades, TP/SL/time-stop grid.
- Research split: discovery -> validation -> OOS; discovery is the only stage used to nominate candidates.
- Automated workflow: added on the research branch; it downloads H1 data, audits it, builds datasets, runs research, and commits results.
- Current verified trading performance: none yet. Results must come from an actual completed workflow run.
