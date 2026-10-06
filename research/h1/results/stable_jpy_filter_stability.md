# Stable JPY filter pair stability

Pair-level diagnostic for the pooled Discovery shortlist. No candidate selection is performed here; Validation/OOS are evaluation only.

|Conditions|Val min n|Val min win|Val min PF|OOS min n|OOS min win|OOS min PF|Val all +|OOS all +|
|---|---:|---:|---:|---:|---:|---:|:---:|:---:|
|trend_down & h4_bull & d1_bull & w1_bull|14|0.625|1.667|15|0.750|3.750|True|True|
|trend_down & h4_bull & d1_bull & rsi_up6|27|0.533|1.143|24|0.750|3.600|True|True|
|trend_down & h4_bull & d1_bull & adx20+ & w1_bull|8|0.625|1.667|10|0.643|2.250|True|True|
|trend_down & h4_bull & d1_bull & macd_pos & rsi_up6|26|0.538|1.167|20|0.600|2.000|True|True|
|trend_down & h4_bull & d1_bull & macd_neg & rsi_up6|14|0.500|1.000|13|0.857|7.500|False|True|
|trend_down & h4_bull & d1_bull & atr_above_med & near_ema20|13|0.438|0.778|14|0.714|5.000|False|True|
|trend_down & h4_bull & d1_bull & near_ema20 & rsi_up6|20|0.500|1.000|17|0.722|4.333|False|True|
|trend_down & h4_bull & d1_bull & rsi_up6 & w1_bull|12|0.500|1.000|13|0.769|4.000|False|True|
|trend_down & h4_bull & d1_bull & macd_pos & near_ema20|21|0.476|0.909|16|0.688|3.667|False|True|
|trend_down & h4_bull & d1_bull & atr_above_med & w1_bull|10|0.429|0.750|12|0.733|3.667|False|True|
|trend_down & h4_bull & d1_bull & near_ema20|23|0.478|0.917|19|0.737|3.600|False|True|
|trend_down & h4_bull & d1_bull & atr_above_med & rsi45_55|16|0.444|0.800|14|0.714|3.500|False|True|
|trend_down & h4_bull & d1_bull & far_ema200 & near_ema20|21|0.476|0.909|16|0.762|3.200|False|True|
|trend_down & h4_bull & d1_bull & rsi45_55 & rsi_up6|22|0.500|1.000|17|0.706|3.000|False|True|
|trend_down & h4_bull & d1_bull & macd_pos & rsi45_55|23|0.478|0.917|16|0.688|3.000|False|True|
|trend_down & h4_bull & d1_bull & rsi55_60|19|0.348|0.571|12|0.750|3.000|False|True|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi55_60|13|0.333|0.545|7|0.750|3.000|False|True|
|trend_down & h4_bull & d1_bull & macd_neg & rsi40_45|13|0.500|1.000|8|0.733|2.750|False|True|
|trend_down & h4_bull & d1_bull & adx20+ & rsi45_55|16|0.471|0.889|13|0.688|2.750|False|True|
|trend_down & h4_bull & d1_bull & adx20+ & near_ema20|14|0.400|0.667|13|0.647|2.750|False|True|
|trend_down & h4_bull & d1_bull & rsi45_55|25|0.480|0.923|19|0.696|2.667|False|True|
|trend_down & h4_bull & d1_bull & rsi55_60 & rsi_up6|18|0.318|0.500|11|0.727|2.667|False|True|
|trend_down & h4_bull & d1_bull & macd_pos & w1_bull|12|0.429|0.750|12|0.667|2.500|False|True|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi45_55|23|0.478|0.917|16|0.700|2.333|False|True|
|trend_down & h4_bull & d1_bull & adx25+ & near_ema20|7|0.400|0.667|10|0.700|2.333|False|True|
|trend_down & h4_bull & d1_bull & rsi45_55 & w1_bull|12|0.467|0.875|11|0.667|2.000|False|True|
|trend_down & h4_bull & d1_bull & adx20+ & bb_narrow|8|0.375|0.600|9|0.600|2.000|False|True|
|trend_down & h4_bull & d1_bull & macd_pos|26|0.462|0.857|22|0.591|1.857|False|True|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi<40|17|0.412|0.700|6|0.500|1.000|False|False|
|trend_down & h4_bull & d1_bull & rsi<40|17|0.412|0.700|6|0.500|1.000|False|False|
