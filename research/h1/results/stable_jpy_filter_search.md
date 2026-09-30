# Stable JPY filter search

Universe: USDJPY/EURJPY/GBPJPY. Base structure is frozen as trend_down & h4_bull & d1_bull.
Only simple 1-2 additional filters were selected on pooled Discovery. TP50/SL75, next-open, non-overlapping 48-H1 window.
Validation and OOS are evaluation only.

|Conditions|Split|Trades|Win|LCB95|PF|ExpR|
|---|---|---:|---:|---:|---:|---:|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi55_60|discovery|86|0.663|0.558|2.714|0.419|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi55_60|validation|45|0.467|0.329|0.913|-0.044|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi55_60|oos|23|0.826|0.629|4.750|0.652|
|trend_down & h4_bull & d1_bull & adx25+ & near_ema20|discovery|84|0.643|0.536|2.455|0.381|
|trend_down & h4_bull & d1_bull & adx25+ & near_ema20|validation|25|0.680|0.484|2.125|0.360|
|trend_down & h4_bull & d1_bull & adx25+ & near_ema20|oos|32|0.750|0.579|3.429|0.531|
|trend_down & h4_bull & d1_bull & near_ema20 & rsi_up6|discovery|153|0.608|0.529|2.114|0.320|
|trend_down & h4_bull & d1_bull & near_ema20 & rsi_up6|validation|62|0.565|0.441|1.346|0.145|
|trend_down & h4_bull & d1_bull & near_ema20 & rsi_up6|oos|52|0.788|0.660|4.556|0.615|
|trend_down & h4_bull & d1_bull & rsi45_55 & rsi_up6|discovery|155|0.606|0.528|2.186|0.329|
|trend_down & h4_bull & d1_bull & rsi45_55 & rsi_up6|validation|69|0.580|0.462|1.429|0.174|
|trend_down & h4_bull & d1_bull & rsi45_55 & rsi_up6|oos|52|0.731|0.597|3.455|0.519|
|trend_down & h4_bull & d1_bull & atr_above_med & near_ema20|discovery|122|0.615|0.526|2.143|0.328|
|trend_down & h4_bull & d1_bull & atr_above_med & near_ema20|validation|44|0.614|0.466|1.588|0.227|
|trend_down & h4_bull & d1_bull & atr_above_med & near_ema20|oos|48|0.812|0.681|5.571|0.667|
|trend_down & h4_bull & d1_bull & adx20+ & near_ema20|discovery|131|0.603|0.517|2.135|0.321|
|trend_down & h4_bull & d1_bull & adx20+ & near_ema20|validation|46|0.630|0.486|1.812|0.283|
|trend_down & h4_bull & d1_bull & adx20+ & near_ema20|oos|44|0.750|0.606|3.667|0.545|
|trend_down & h4_bull & d1_bull & atr_above_med & w1_bull|discovery|94|0.617|0.516|1.758|0.266|
|trend_down & h4_bull & d1_bull & atr_above_med & w1_bull|validation|37|0.622|0.461|1.643|0.243|
|trend_down & h4_bull & d1_bull & atr_above_med & w1_bull|oos|43|0.767|0.623|4.125|0.581|
|trend_down & h4_bull & d1_bull & macd_pos & near_ema20|discovery|162|0.593|0.516|2.087|0.309|
|trend_down & h4_bull & d1_bull & macd_pos & near_ema20|validation|64|0.578|0.456|1.423|0.172|
|trend_down & h4_bull & d1_bull & macd_pos & near_ema20|oos|54|0.741|0.611|3.636|0.537|
|trend_down & h4_bull & d1_bull & rsi_up6 & w1_bull|discovery|119|0.605|0.515|2.057|0.311|
|trend_down & h4_bull & d1_bull & rsi_up6 & w1_bull|validation|41|0.561|0.410|1.278|0.122|
|trend_down & h4_bull & d1_bull & rsi_up6 & w1_bull|oos|46|0.804|0.668|5.286|0.652|
|trend_down & h4_bull & d1_bull & macd_pos & rsi45_55|discovery|159|0.591|0.514|2.043|0.302|
|trend_down & h4_bull & d1_bull & macd_pos & rsi45_55|validation|71|0.592|0.475|1.500|0.197|
|trend_down & h4_bull & d1_bull & macd_pos & rsi45_55|oos|54|0.685|0.553|2.846|0.444|
|trend_down & h4_bull & d1_bull & far_ema200 & near_ema20|discovery|163|0.589|0.512|1.959|0.288|
|trend_down & h4_bull & d1_bull & far_ema200 & near_ema20|validation|67|0.582|0.463|1.444|0.179|
|trend_down & h4_bull & d1_bull & far_ema200 & near_ema20|oos|53|0.755|0.624|3.333|0.528|
|trend_down & h4_bull & d1_bull & macd_pos & w1_bull|discovery|109|0.606|0.512|2.129|0.321|
|trend_down & h4_bull & d1_bull & macd_pos & w1_bull|validation|38|0.553|0.397|1.235|0.105|
|trend_down & h4_bull & d1_bull & macd_pos & w1_bull|oos|46|0.696|0.552|3.200|0.478|
|trend_down & h4_bull & d1_bull & atr_above_med & rsi45_55|discovery|127|0.598|0.511|1.949|0.291|
|trend_down & h4_bull & d1_bull & atr_above_med & rsi45_55|validation|50|0.660|0.522|1.941|0.320|
|trend_down & h4_bull & d1_bull & atr_above_med & rsi45_55|oos|48|0.750|0.612|4.000|0.562|
|trend_down & h4_bull & d1_bull & adx20+ & bb_narrow|discovery|92|0.609|0.507|2.154|0.326|
|trend_down & h4_bull & d1_bull & adx20+ & bb_narrow|validation|32|0.594|0.423|1.462|0.188|
|trend_down & h4_bull & d1_bull & adx20+ & bb_narrow|oos|25|0.760|0.566|4.750|0.600|
|trend_down & h4_bull & d1_bull & adx20+ & rsi45_55|discovery|130|0.592|0.506|2.026|0.300|
|trend_down & h4_bull & d1_bull & adx20+ & rsi45_55|validation|54|0.648|0.515|1.944|0.315|
|trend_down & h4_bull & d1_bull & adx20+ & rsi45_55|oos|43|0.698|0.549|3.000|0.465|
|trend_down & h4_bull & d1_bull & near_ema20|discovery|185|0.578|0.506|1.981|0.286|
|trend_down & h4_bull & d1_bull & near_ema20|validation|69|0.565|0.448|1.345|0.145|
|trend_down & h4_bull & d1_bull & near_ema20|oos|61|0.770|0.651|3.917|0.574|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi45_55|discovery|160|0.581|0.504|1.898|0.275|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi45_55|validation|74|0.595|0.481|1.517|0.203|
|trend_down & h4_bull & d1_bull & far_ema200 & rsi45_55|oos|51|0.725|0.591|2.846|0.471|
|trend_down & h4_bull & d1_bull & macd_pos & rsi_up6|discovery|194|0.572|0.502|1.762|0.247|
|trend_down & h4_bull & d1_bull & macd_pos & rsi_up6|validation|76|0.605|0.493|1.586|0.224|
|trend_down & h4_bull & d1_bull & macd_pos & rsi_up6|oos|67|0.687|0.568|3.067|0.463|
|trend_down & h4_bull & d1_bull & rsi45_55 & w1_bull|discovery|93|0.602|0.501|1.931|0.290|
|trend_down & h4_bull & d1_bull & rsi45_55 & w1_bull|validation|38|0.579|0.422|1.375|0.158|
|trend_down & h4_bull & d1_bull & rsi45_55 & w1_bull|oos|37|0.811|0.658|6.000|0.676|
|trend_down & h4_bull & d1_bull & adx20+ & w1_bull|discovery|104|0.596|0.500|1.938|0.288|
|trend_down & h4_bull & d1_bull & adx20+ & w1_bull|validation|31|0.677|0.501|2.100|0.355|
|trend_down & h4_bull & d1_bull & adx20+ & w1_bull|oos|37|0.730|0.570|3.375|0.514|
|trend_down & h4_bull & d1_bull & rsi55_60 & rsi_up6|discovery|115|0.591|0.500|1.943|0.287|
|trend_down & h4_bull & d1_bull & rsi55_60 & rsi_up6|validation|61|0.426|0.310|0.765|-0.131|
|trend_down & h4_bull & d1_bull & rsi55_60 & rsi_up6|oos|39|0.795|0.645|5.167|0.641|
|trend_down & h4_bull & d1_bull & rsi45_55|discovery|182|0.571|0.499|1.891|0.269|
|trend_down & h4_bull & d1_bull & rsi45_55|validation|76|0.579|0.467|1.419|0.171|
|trend_down & h4_bull & d1_bull & rsi45_55|oos|61|0.721|0.598|3.143|0.492|
|trend_down & h4_bull & d1_bull & rsi55_60|discovery|130|0.585|0.499|2.111|0.308|
|trend_down & h4_bull & d1_bull & rsi55_60|validation|63|0.460|0.343|0.879|-0.063|
|trend_down & h4_bull & d1_bull & rsi55_60|oos|44|0.818|0.680|6.000|0.682|
|trend_down & h4_bull & d1_bull & macd_pos|discovery|207|0.565|0.497|1.828|0.256|
|trend_down & h4_bull & d1_bull & macd_pos|validation|80|0.562|0.453|1.324|0.138|
|trend_down & h4_bull & d1_bull & macd_pos|oos|72|0.681|0.566|2.882|0.444|
|trend_down & h4_bull & d1_bull & macd_neg & rsi_up6|discovery|112|0.589|0.497|2.000|0.295|
|trend_down & h4_bull & d1_bull & macd_neg & rsi_up6|validation|45|0.511|0.370|1.045|0.022|
|trend_down & h4_bull & d1_bull & macd_neg & rsi_up6|oos|44|0.886|0.760|9.750|0.795|
|trend_down & h4_bull & d1_bull & rsi_up6|discovery|219|0.562|0.495|1.708|0.233|
|trend_down & h4_bull & d1_bull & rsi_up6|validation|86|0.558|0.453|1.263|0.116|
|trend_down & h4_bull & d1_bull & rsi_up6|oos|73|0.795|0.688|5.273|0.644|
|trend_down & h4_bull & d1_bull & near_ema20 & w1_bull|discovery|94|0.596|0.495|1.867|0.277|
|trend_down & h4_bull & d1_bull & near_ema20 & w1_bull|validation|35|0.543|0.382|1.188|0.086|
|trend_down & h4_bull & d1_bull & near_ema20 & w1_bull|oos|39|0.821|0.673|6.400|0.692|
|trend_down & h4_bull & d1_bull & near_ema20 & rsi45_55|discovery|176|0.568|0.494|1.887|0.267|
|trend_down & h4_bull & d1_bull & near_ema20 & rsi45_55|validation|68|0.559|0.441|1.310|0.132|
|trend_down & h4_bull & d1_bull & near_ema20 & rsi45_55|oos|60|0.750|0.628|3.462|0.533|
|trend_down & h4_bull & d1_bull & far_ema200 & macd_pos|discovery|182|0.566|0.493|1.746|0.242|
|trend_down & h4_bull & d1_bull & far_ema200 & macd_pos|validation|76|0.566|0.454|1.344|0.145|
|trend_down & h4_bull & d1_bull & far_ema200 & macd_pos|oos|62|0.694|0.570|2.688|0.435|
|trend_down & h4_bull & d1_bull & adx20+ & rsi_up6|discovery|173|0.566|0.492|1.750|0.243|
|trend_down & h4_bull & d1_bull & adx20+ & rsi_up6|validation|68|0.662|0.543|1.957|0.324|
|trend_down & h4_bull & d1_bull & adx20+ & rsi_up6|oos|53|0.717|0.584|3.455|0.509|
