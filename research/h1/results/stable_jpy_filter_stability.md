# Stable JPY filter pair stability

Pair-level diagnostic for the pooled Discovery shortlist. No candidate selection is performed here; Validation/OOS are evaluation only.

|Conditions|Val min n|Val min win|Val min PF|OOS min n|OOS min win|OOS min PF|Val all +|OOS all +|
|---|---:|---:|---:|---:|---:|---:|:---:|:---:|
|trend_down & h4_bull & d1_bull & w1_bull|14|0.625|1.667|16|0.750|3.750|True|True|
|trend_down & h4_bull & d1_bull & adx20+ & w1_bull|8|0.625|1.667|10|0.643|2.250|True|True|
|trend_down & h4_bull & d1_bull & macd_pos & rsi_up6|24|0.542|1.182|21|0.619|2.167|True|True|
|trend_down & h4_bull & d1_bull & macd_neg & rsi_up6|14|0.438|0.778|13|0.857|7.500|False|True|
|trend_down & h4_bull & d1_bull & rsi55_60|18|0.348|0.571|13|0.800|5.500|False|True|
|trend_down & h4_bull & d1_bull & atr_above_med & near_ema20|13|0.429|0.750|15|0.733|5.000|False|True|
|trend_down & h4_bull & d1_bull & rsi_up6|27|0.500|1.000|24|0.769|4.750|False|True|
|trend_down & h4_bull & d1_bull & rsi55_60 & rsi_up6|17|0.318|0.500|11|0.769|4.500|False|True|
|trend_down & h4_bull & d1_bull & rsi_up6 & w1_bull|12|0.467|0.875|14|0.786|4.000|False|True|
|trend_down & h4_bull & d1_bull & atr_above_med & w1_bull|10|0.429|0.750|13|0.733|3.667|False|True|
|trend_down & h4_bull & d1_bull & atr_above_med & rsi45_55|16|0.438|0.778|14|0.733|3.500|False|True|
|trend_down & h4_bull & d1_bull & macd_pos & near_ema20|19|0.474|0.900|16|0.688|3.400|False|True|
|trend_down & h4_bull & d1_bull & near_ema20 & rsi_up6|20|0.500|1.000|17|0.684|3.250|False|True|
|trend_down & h4_bull & d1_bull & macd_neg & rsi40_45|13|0.500|1.000|8|0.750|3.000|False|True|
|trend_down & h4_bull & d1_bull & rsi45_55 & rsi_up6|22|0.500|1.000|17|0.706|3.000|False|True|
|trend_down & h4_bull & d1_bull & near_ema20|21|0.476|0.909|19|0.737|3.000|False|True|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi55_60|13|0.333|0.545|7|0.750|3.000|False|True|
|trend_down & h4_bull & d1_bull & adx20+ & rsi45_55|16|0.500|1.000|13|0.667|2.750|False|True|
|trend_down & h4_bull & d1_bull & far_ema200 & near_ema20|19|0.474|0.900|16|0.727|2.667|False|True|
|trend_down & h4_bull & d1_bull & macd_pos & rsi45_55|21|0.476|0.909|16|0.682|2.500|False|True|
|trend_down & h4_bull & d1_bull & adx20+ & near_ema20|14|0.429|0.750|13|0.625|2.500|False|True|
|trend_down & h4_bull & d1_bull & macd_pos & w1_bull|12|0.385|0.625|13|0.667|2.500|False|True|
|trend_down & h4_bull & d1_bull & macd_pos|24|0.458|0.846|22|0.636|2.333|False|True|
|trend_down & h4_bull & d1_bull & adx25+ & near_ema20|7|0.444|0.800|10|0.692|2.333|False|True|
|trend_down & h4_bull & d1_bull & rsi45_55|23|0.478|0.917|19|0.667|2.286|False|True|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi45_55|21|0.476|0.909|16|0.667|2.000|False|True|
|trend_down & h4_bull & d1_bull & rsi45_55 & w1_bull|12|0.429|0.750|11|0.667|2.000|False|True|
|trend_down & h4_bull & d1_bull & adx20+ & bb_narrow|8|0.375|0.600|8|0.600|2.000|False|True|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi<40|17|0.412|0.700|6|0.500|1.000|False|False|
|trend_down & h4_bull & d1_bull & rsi<40|17|0.412|0.700|6|0.500|1.000|False|False|
