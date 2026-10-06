# Stable JPY filter search

Universe: USDJPY/EURJPY/GBPJPY. Base structure is frozen as trend_down & h4_bull & d1_bull.
Only simple 1-2 additional filters were selected on pooled Discovery. TP50/SL75, next-open, non-overlapping 48-H1 window.
Validation and OOS are evaluation only.

|Conditions|Split|Trades|Win|LCB95|PF|ExpR|
|---|---|---:|---:|---:|---:|---:|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi55_60|discovery|86|0.663|0.558|2.714|0.419|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi55_60|validation|45|0.467|0.329|0.913|-0.044|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi55_60|oos|25|0.800|0.609|4.000|0.600|
|trend_down & h4_bull & d1_bull & adx25+ & near_ema20|discovery|84|0.643|0.536|2.455|0.381|
|trend_down & h4_bull & d1_bull & adx25+ & near_ema20|validation|26|0.654|0.462|1.889|0.308|
|trend_down & h4_bull & d1_bull & adx25+ & near_ema20|oos|35|0.743|0.579|3.250|0.514|
|trend_down & h4_bull & d1_bull & near_ema20 & rsi_up6|discovery|154|0.604|0.525|2.067|0.312|
|trend_down & h4_bull & d1_bull & near_ema20 & rsi_up6|validation|64|0.562|0.441|1.333|0.141|
|trend_down & h4_bull & d1_bull & near_ema20 & rsi_up6|oos|52|0.827|0.703|6.143|0.692|
|trend_down & h4_bull & d1_bull & rsi45_55 & rsi_up6|discovery|156|0.603|0.524|2.136|0.321|
|trend_down & h4_bull & d1_bull & rsi45_55 & rsi_up6|validation|71|0.577|0.462|1.414|0.169|
|trend_down & h4_bull & d1_bull & rsi45_55 & rsi_up6|oos|52|0.769|0.639|4.444|0.596|
|trend_down & h4_bull & d1_bull & atr_above_med & near_ema20|discovery|123|0.610|0.521|2.083|0.317|
|trend_down & h4_bull & d1_bull & atr_above_med & near_ema20|validation|45|0.600|0.455|1.500|0.200|
|trend_down & h4_bull & d1_bull & atr_above_med & near_ema20|oos|47|0.809|0.675|5.429|0.660|
|trend_down & h4_bull & d1_bull & atr_above_med & w1_bull|discovery|95|0.621|0.521|1.788|0.274|
|trend_down & h4_bull & d1_bull & atr_above_med & w1_bull|validation|37|0.622|0.461|1.643|0.243|
|trend_down & h4_bull & d1_bull & atr_above_med & w1_bull|oos|41|0.756|0.607|3.875|0.561|
|trend_down & h4_bull & d1_bull & adx20+ & near_ema20|discovery|131|0.603|0.517|2.135|0.321|
|trend_down & h4_bull & d1_bull & adx20+ & near_ema20|validation|47|0.596|0.453|1.556|0.213|
|trend_down & h4_bull & d1_bull & adx20+ & near_ema20|oos|46|0.761|0.621|3.889|0.565|
|trend_down & h4_bull & d1_bull & far_ema200 & near_ema20|discovery|164|0.591|0.515|1.980|0.293|
|trend_down & h4_bull & d1_bull & far_ema200 & near_ema20|validation|69|0.565|0.448|1.345|0.145|
|trend_down & h4_bull & d1_bull & far_ema200 & near_ema20|oos|54|0.778|0.651|3.818|0.574|
|trend_down & h4_bull & d1_bull & macd_pos & near_ema20|discovery|163|0.589|0.512|2.043|0.301|
|trend_down & h4_bull & d1_bull & macd_pos & near_ema20|validation|66|0.576|0.456|1.407|0.167|
|trend_down & h4_bull & d1_bull & macd_pos & near_ema20|oos|55|0.764|0.637|4.200|0.582|
|trend_down & h4_bull & d1_bull & rsi_up6 & w1_bull|discovery|120|0.600|0.511|2.000|0.300|
|trend_down & h4_bull & d1_bull & rsi_up6 & w1_bull|validation|42|0.595|0.445|1.471|0.190|
|trend_down & h4_bull & d1_bull & rsi_up6 & w1_bull|oos|44|0.795|0.655|5.000|0.636|
|trend_down & h4_bull & d1_bull & macd_pos & rsi45_55|discovery|160|0.588|0.510|2.000|0.294|
|trend_down & h4_bull & d1_bull & macd_pos & rsi45_55|validation|73|0.589|0.474|1.483|0.192|
|trend_down & h4_bull & d1_bull & macd_pos & rsi45_55|oos|55|0.709|0.579|3.250|0.491|
|trend_down & h4_bull & d1_bull & atr_above_med & rsi45_55|discovery|128|0.594|0.507|1.900|0.281|
|trend_down & h4_bull & d1_bull & atr_above_med & rsi45_55|validation|51|0.647|0.510|1.833|0.294|
|trend_down & h4_bull & d1_bull & atr_above_med & rsi45_55|oos|47|0.745|0.605|3.889|0.553|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi45_55|discovery|161|0.584|0.507|1.918|0.280|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi45_55|validation|76|0.579|0.467|1.419|0.171|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi45_55|oos|52|0.750|0.618|3.250|0.519|
|trend_down & h4_bull & d1_bull & macd_pos & w1_bull|discovery|110|0.600|0.507|2.062|0.309|
|trend_down & h4_bull & d1_bull & macd_pos & w1_bull|validation|39|0.564|0.410|1.294|0.128|
|trend_down & h4_bull & d1_bull & macd_pos & w1_bull|oos|44|0.705|0.558|3.444|0.500|
|trend_down & h4_bull & d1_bull & adx20+ & bb_narrow|discovery|92|0.609|0.507|2.154|0.326|
|trend_down & h4_bull & d1_bull & adx20+ & bb_narrow|validation|31|0.581|0.408|1.385|0.161|
|trend_down & h4_bull & d1_bull & adx20+ & bb_narrow|oos|28|0.750|0.566|4.200|0.571|
|trend_down & h4_bull & d1_bull & adx20+ & rsi45_55|discovery|130|0.592|0.506|2.026|0.300|
|trend_down & h4_bull & d1_bull & adx20+ & rsi45_55|validation|55|0.618|0.486|1.700|0.255|
|trend_down & h4_bull & d1_bull & adx20+ & rsi45_55|oos|45|0.711|0.566|3.200|0.489|
|trend_down & h4_bull & d1_bull & near_ema20|discovery|186|0.575|0.503|1.945|0.280|
|trend_down & h4_bull & d1_bull & near_ema20|validation|71|0.563|0.448|1.333|0.141|
|trend_down & h4_bull & d1_bull & near_ema20|oos|62|0.790|0.674|4.455|0.613|
|trend_down & h4_bull & d1_bull & adx20+ & w1_bull|discovery|104|0.596|0.500|1.938|0.288|
|trend_down & h4_bull & d1_bull & adx20+ & w1_bull|validation|31|0.677|0.501|2.100|0.355|
|trend_down & h4_bull & d1_bull & adx20+ & w1_bull|oos|36|0.722|0.560|3.250|0.500|
|trend_down & h4_bull & d1_bull & macd_pos & rsi_up6|discovery|195|0.569|0.499|1.734|0.241|
|trend_down & h4_bull & d1_bull & macd_pos & rsi_up6|validation|78|0.603|0.492|1.567|0.218|
|trend_down & h4_bull & d1_bull & macd_pos & rsi_up6|oos|67|0.701|0.583|3.357|0.493|
|trend_down & h4_bull & d1_bull & macd_neg & rsi_up6|discovery|112|0.589|0.497|2.000|0.295|
|trend_down & h4_bull & d1_bull & macd_neg & rsi_up6|validation|48|0.542|0.403|1.182|0.083|
|trend_down & h4_bull & d1_bull & macd_neg & rsi_up6|oos|44|0.886|0.760|9.750|0.795|
|trend_down & h4_bull & d1_bull & rsi45_55|discovery|183|0.568|0.496|1.857|0.262|
|trend_down & h4_bull & d1_bull & rsi45_55|validation|78|0.577|0.466|1.406|0.167|
|trend_down & h4_bull & d1_bull & rsi45_55|oos|62|0.742|0.621|3.538|0.532|
|trend_down & h4_bull & d1_bull & rsi55_60 & rsi_up6|discovery|116|0.586|0.495|1.889|0.276|
|trend_down & h4_bull & d1_bull & rsi55_60 & rsi_up6|validation|61|0.443|0.325|0.818|-0.098|
|trend_down & h4_bull & d1_bull & rsi55_60 & rsi_up6|oos|41|0.780|0.633|4.571|0.610|
|trend_down & h4_bull & d1_bull & rsi45_55 & w1_bull|discovery|94|0.596|0.495|1.867|0.277|
|trend_down & h4_bull & d1_bull & rsi45_55 & w1_bull|validation|39|0.590|0.434|1.438|0.179|
|trend_down & h4_bull & d1_bull & rsi45_55 & w1_bull|oos|35|0.829|0.673|7.250|0.714|
|trend_down & h4_bull & d1_bull & macd_pos|discovery|208|0.562|0.495|1.800|0.250|
|trend_down & h4_bull & d1_bull & macd_pos|validation|82|0.561|0.453|1.314|0.134|
|trend_down & h4_bull & d1_bull & macd_pos|oos|73|0.685|0.571|2.941|0.452|
|trend_down & h4_bull & d1_bull & rsi55_60|discovery|131|0.580|0.495|2.054|0.298|
|trend_down & h4_bull & d1_bull & rsi55_60|validation|63|0.476|0.358|0.938|-0.032|
|trend_down & h4_bull & d1_bull & rsi55_60|oos|45|0.800|0.662|5.143|0.644|
|trend_down & h4_bull & d1_bull & w1_bull|discovery|131|0.580|0.495|1.900|0.275|
|trend_down & h4_bull & d1_bull & w1_bull|validation|47|0.638|0.495|1.765|0.277|
|trend_down & h4_bull & d1_bull & w1_bull|oos|51|0.784|0.654|4.444|0.608|
|trend_down & h4_bull & d1_bull & rsi_up6|discovery|220|0.559|0.493|1.685|0.227|
|trend_down & h4_bull & d1_bull & rsi_up6|validation|88|0.580|0.475|1.378|0.159|
|trend_down & h4_bull & d1_bull & rsi_up6|oos|74|0.784|0.677|4.833|0.622|
|trend_down & h4_bull & d1_bull & rsi<40|discovery|124|0.581|0.493|1.895|0.274|
|trend_down & h4_bull & d1_bull & rsi<40|validation|55|0.527|0.398|1.115|0.055|
|trend_down & h4_bull & d1_bull & rsi<40|oos|32|0.781|0.612|3.571|0.562|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi<40|discovery|124|0.581|0.493|1.895|0.274|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi<40|validation|55|0.527|0.398|1.115|0.055|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi<40|oos|32|0.781|0.612|3.571|0.562|
|trend_down & h4_bull & d1_bull & macd_neg & rsi40_45|discovery|87|0.598|0.493|2.364|0.345|
|trend_down & h4_bull & d1_bull & macd_neg & rsi40_45|validation|41|0.610|0.457|1.562|0.220|
|trend_down & h4_bull & d1_bull & macd_neg & rsi40_45|oos|35|0.771|0.610|3.857|0.571|
