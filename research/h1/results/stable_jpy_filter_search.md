# Stable JPY filter search

Universe: USDJPY/EURJPY/GBPJPY. Base structure is frozen as trend_down & h4_bull & d1_bull.
Only simple 1-2 additional filters were selected on pooled Discovery. TP50/SL75, next-open, non-overlapping 48-H1 window.
Validation and OOS are evaluation only.

|Conditions|Split|Trades|Win|LCB95|PF|ExpR|
|---|---|---:|---:|---:|---:|---:|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi55_60|discovery|86|0.663|0.558|2.714|0.419|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi55_60|validation|45|0.467|0.329|0.913|-0.044|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi55_60|oos|25|0.840|0.653|5.250|0.680|
|trend_down & h4_bull & d1_bull & adx25+ & near_ema20|discovery|84|0.643|0.536|2.455|0.381|
|trend_down & h4_bull & d1_bull & adx25+ & near_ema20|validation|25|0.680|0.484|2.125|0.360|
|trend_down & h4_bull & d1_bull & adx25+ & near_ema20|oos|34|0.735|0.569|3.125|0.500|
|trend_down & h4_bull & d1_bull & near_ema20 & rsi_up6|discovery|154|0.604|0.525|2.067|0.312|
|trend_down & h4_bull & d1_bull & near_ema20 & rsi_up6|validation|62|0.565|0.441|1.346|0.145|
|trend_down & h4_bull & d1_bull & near_ema20 & rsi_up6|oos|53|0.811|0.686|5.375|0.660|
|trend_down & h4_bull & d1_bull & rsi45_55 & rsi_up6|discovery|156|0.603|0.524|2.136|0.321|
|trend_down & h4_bull & d1_bull & rsi45_55 & rsi_up6|validation|69|0.580|0.462|1.429|0.174|
|trend_down & h4_bull & d1_bull & rsi45_55 & rsi_up6|oos|53|0.755|0.624|4.000|0.566|
|trend_down & h4_bull & d1_bull & atr_above_med & near_ema20|discovery|123|0.610|0.521|2.083|0.317|
|trend_down & h4_bull & d1_bull & atr_above_med & near_ema20|validation|43|0.605|0.456|1.529|0.209|
|trend_down & h4_bull & d1_bull & atr_above_med & near_ema20|oos|48|0.812|0.681|5.571|0.667|
|trend_down & h4_bull & d1_bull & atr_above_med & w1_bull|discovery|95|0.621|0.521|1.788|0.274|
|trend_down & h4_bull & d1_bull & atr_above_med & w1_bull|validation|36|0.611|0.449|1.571|0.222|
|trend_down & h4_bull & d1_bull & atr_above_med & w1_bull|oos|42|0.762|0.615|4.000|0.571|
|trend_down & h4_bull & d1_bull & adx20+ & near_ema20|discovery|131|0.603|0.517|2.135|0.321|
|trend_down & h4_bull & d1_bull & adx20+ & near_ema20|validation|46|0.609|0.465|1.647|0.239|
|trend_down & h4_bull & d1_bull & adx20+ & near_ema20|oos|45|0.756|0.613|3.778|0.556|
|trend_down & h4_bull & d1_bull & far_ema200 & near_ema20|discovery|164|0.591|0.515|1.980|0.293|
|trend_down & h4_bull & d1_bull & far_ema200 & near_ema20|validation|67|0.567|0.448|1.357|0.149|
|trend_down & h4_bull & d1_bull & far_ema200 & near_ema20|oos|55|0.764|0.637|3.500|0.545|
|trend_down & h4_bull & d1_bull & macd_pos & near_ema20|discovery|163|0.589|0.512|2.043|0.301|
|trend_down & h4_bull & d1_bull & macd_pos & near_ema20|validation|64|0.578|0.456|1.423|0.172|
|trend_down & h4_bull & d1_bull & macd_pos & near_ema20|oos|56|0.750|0.623|3.818|0.554|
|trend_down & h4_bull & d1_bull & rsi_up6 & w1_bull|discovery|120|0.600|0.511|2.000|0.300|
|trend_down & h4_bull & d1_bull & rsi_up6 & w1_bull|validation|41|0.585|0.434|1.412|0.171|
|trend_down & h4_bull & d1_bull & rsi_up6 & w1_bull|oos|45|0.800|0.662|5.143|0.644|
|trend_down & h4_bull & d1_bull & macd_pos & rsi45_55|discovery|160|0.588|0.510|2.000|0.294|
|trend_down & h4_bull & d1_bull & macd_pos & rsi45_55|validation|71|0.592|0.475|1.500|0.197|
|trend_down & h4_bull & d1_bull & macd_pos & rsi45_55|oos|56|0.696|0.567|3.000|0.464|
|trend_down & h4_bull & d1_bull & atr_above_med & rsi45_55|discovery|128|0.594|0.507|1.900|0.281|
|trend_down & h4_bull & d1_bull & atr_above_med & rsi45_55|validation|49|0.653|0.513|1.882|0.306|
|trend_down & h4_bull & d1_bull & atr_above_med & rsi45_55|oos|48|0.750|0.612|4.000|0.562|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi45_55|discovery|161|0.584|0.507|1.918|0.280|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi45_55|validation|74|0.581|0.467|1.433|0.176|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi45_55|oos|53|0.736|0.604|3.000|0.491|
|trend_down & h4_bull & d1_bull & macd_pos & w1_bull|discovery|110|0.600|0.507|2.062|0.309|
|trend_down & h4_bull & d1_bull & macd_pos & w1_bull|validation|38|0.553|0.397|1.235|0.105|
|trend_down & h4_bull & d1_bull & macd_pos & w1_bull|oos|45|0.711|0.566|3.556|0.511|
|trend_down & h4_bull & d1_bull & adx20+ & bb_narrow|discovery|92|0.609|0.507|2.154|0.326|
|trend_down & h4_bull & d1_bull & adx20+ & bb_narrow|validation|31|0.581|0.408|1.385|0.161|
|trend_down & h4_bull & d1_bull & adx20+ & bb_narrow|oos|27|0.778|0.592|5.250|0.630|
|trend_down & h4_bull & d1_bull & adx20+ & rsi45_55|discovery|130|0.592|0.506|2.026|0.300|
|trend_down & h4_bull & d1_bull & adx20+ & rsi45_55|validation|54|0.630|0.496|1.789|0.278|
|trend_down & h4_bull & d1_bull & adx20+ & rsi45_55|oos|44|0.705|0.558|3.100|0.477|
|trend_down & h4_bull & d1_bull & near_ema20|discovery|186|0.575|0.503|1.945|0.280|
|trend_down & h4_bull & d1_bull & near_ema20|validation|69|0.565|0.448|1.345|0.145|
|trend_down & h4_bull & d1_bull & near_ema20|oos|63|0.778|0.661|4.083|0.587|
|trend_down & h4_bull & d1_bull & adx20+ & w1_bull|discovery|104|0.596|0.500|1.938|0.288|
|trend_down & h4_bull & d1_bull & adx20+ & w1_bull|validation|31|0.677|0.501|2.100|0.355|
|trend_down & h4_bull & d1_bull & adx20+ & w1_bull|oos|36|0.722|0.560|3.250|0.500|
|trend_down & h4_bull & d1_bull & macd_pos & rsi_up6|discovery|195|0.569|0.499|1.734|0.241|
|trend_down & h4_bull & d1_bull & macd_pos & rsi_up6|validation|76|0.605|0.493|1.586|0.224|
|trend_down & h4_bull & d1_bull & macd_pos & rsi_up6|oos|68|0.706|0.589|3.429|0.500|
|trend_down & h4_bull & d1_bull & macd_neg & rsi_up6|discovery|112|0.589|0.497|2.000|0.295|
|trend_down & h4_bull & d1_bull & macd_neg & rsi_up6|validation|46|0.522|0.381|1.091|0.043|
|trend_down & h4_bull & d1_bull & macd_neg & rsi_up6|oos|44|0.886|0.760|9.750|0.795|
|trend_down & h4_bull & d1_bull & rsi45_55|discovery|183|0.568|0.496|1.857|0.262|
|trend_down & h4_bull & d1_bull & rsi45_55|validation|76|0.579|0.467|1.419|0.171|
|trend_down & h4_bull & d1_bull & rsi45_55|oos|63|0.730|0.610|3.286|0.508|
|trend_down & h4_bull & d1_bull & rsi55_60 & rsi_up6|discovery|116|0.586|0.495|1.889|0.276|
|trend_down & h4_bull & d1_bull & rsi55_60 & rsi_up6|validation|60|0.433|0.316|0.788|-0.117|
|trend_down & h4_bull & d1_bull & rsi55_60 & rsi_up6|oos|41|0.805|0.660|5.500|0.659|
|trend_down & h4_bull & d1_bull & rsi45_55 & w1_bull|discovery|94|0.596|0.495|1.867|0.277|
|trend_down & h4_bull & d1_bull & rsi45_55 & w1_bull|validation|38|0.579|0.422|1.375|0.158|
|trend_down & h4_bull & d1_bull & rsi45_55 & w1_bull|oos|36|0.833|0.681|7.500|0.722|
|trend_down & h4_bull & d1_bull & macd_pos|discovery|208|0.562|0.495|1.800|0.250|
|trend_down & h4_bull & d1_bull & macd_pos|validation|80|0.562|0.453|1.324|0.138|
|trend_down & h4_bull & d1_bull & macd_pos|oos|74|0.689|0.577|3.000|0.459|
|trend_down & h4_bull & d1_bull & rsi55_60|discovery|131|0.580|0.495|2.054|0.298|
|trend_down & h4_bull & d1_bull & rsi55_60|validation|62|0.468|0.349|0.906|-0.048|
|trend_down & h4_bull & d1_bull & rsi55_60|oos|46|0.826|0.693|6.333|0.696|
|trend_down & h4_bull & d1_bull & w1_bull|discovery|131|0.580|0.495|1.900|0.275|
|trend_down & h4_bull & d1_bull & w1_bull|validation|46|0.630|0.486|1.706|0.261|
|trend_down & h4_bull & d1_bull & w1_bull|oos|52|0.788|0.660|4.556|0.615|
|trend_down & h4_bull & d1_bull & rsi_up6|discovery|220|0.559|0.493|1.685|0.227|
|trend_down & h4_bull & d1_bull & rsi_up6|validation|86|0.570|0.464|1.324|0.140|
|trend_down & h4_bull & d1_bull & rsi_up6|oos|74|0.797|0.692|5.364|0.649|
|trend_down & h4_bull & d1_bull & rsi<40|discovery|124|0.581|0.493|1.895|0.274|
|trend_down & h4_bull & d1_bull & rsi<40|validation|54|0.519|0.389|1.077|0.037|
|trend_down & h4_bull & d1_bull & rsi<40|oos|31|0.774|0.602|3.429|0.548|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi<40|discovery|124|0.581|0.493|1.895|0.274|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi<40|validation|54|0.519|0.389|1.077|0.037|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi<40|oos|31|0.774|0.602|3.429|0.548|
|trend_down & h4_bull & d1_bull & macd_neg & rsi40_45|discovery|87|0.598|0.493|2.364|0.345|
|trend_down & h4_bull & d1_bull & macd_neg & rsi40_45|validation|41|0.610|0.457|1.562|0.220|
|trend_down & h4_bull & d1_bull & macd_neg & rsi40_45|oos|34|0.794|0.632|4.500|0.618|
