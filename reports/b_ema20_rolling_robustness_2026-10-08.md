# B + EMA20 ローリング堅牢性検証 2026-10-08

## 固定条件
- B: signal_range_atr <= 1.151613
- B: bars_touch_to_signal <= 6
- Entry: existing signal entry_timestamp / entry_price
- Initial SL: touch candle low for Long / high for Short
- Exit: SL -> EMA20 reverse cross -> max 20 bars TIME
- H4 EMA20 calculated sequentially from closes
- No parameter optimization

## Results
- Total N=98, win rate 39.8%, mean +10.2 pips, PF 1.471, total +1002.9 pips
- Discovery N=63, win rate 36.5%, mean +3.3 pips, PF 1.137, total +209.8 pips
- Validation N=22, win rate 36.4%, mean +12.9 pips, PF 1.645, total +282.8 pips
- OOS N=13, win rate 61.5%, mean +39.3 pips, PF 4.193, total +510.3 pips

## Rolling 12-month windows, shifted every 3 months
2021-01/2022-01: N18 WR11.1% PF0.144 -418.3p
2021-04/2022-04: N21 WR14.3% PF0.493 -289.6p
2021-07/2022-07: N20 WR35.0% PF1.235 +106.0p
2021-10/2022-10: N18 WR27.8% PF0.901 -53.5p
2022-01/2023-01: N17 WR35.3% PF0.983 -8.8p
2022-04/2023-04: N16 WR43.8% PF0.684 -140.5p
2022-07/2023-07: N14 WR35.7% PF0.788 -94.5p
2022-10/2023-10: N12 WR41.7% PF1.108 +34.1p
2023-01/2024-01: N15 WR53.3% PF2.394 +373.1p
2023-04/2024-04: N13 WR53.8% PF3.022 +423.9p
2023-07/2024-07: N13 WR46.2% PF1.431 +96.1p
2023-10/2024-10: N16 WR50.0% PF1.426 +151.3p
2024-01/2025-01: N13 WR53.8% PF2.010 +263.8p
2024-04/2025-04: N16 WR56.3% PF3.218 +586.9p
2024-07/2025-07: N21 WR52.4% PF1.937 +461.7p
2024-10/2025-10: N24 WR45.8% PF2.533 +635.7p
2025-01/2026-01: N22 WR36.4% PF1.645 +282.8p
2025-04/2026-04: N19 WR36.8% PF1.906 +357.1p
2025-07/2026-07: N18 WR44.4% PF4.053 +650.5p
2025-10/2026-10: N15 WR53.3% PF3.308 +467.5p

## Conclusion
B + EMA20 remains a strong candidate, but not production-approved. The strategy is clearly regime-dependent: 2021-2022 was weak, while rolling windows from 2023 onward were predominantly profitable. Do not change B thresholds yet. Next research should identify market-regime features (ATR, EMA slope, trend strength, range/trend state) that explain when B works or fails.