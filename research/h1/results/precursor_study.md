# H1 +100 Pip Precursor Study

Protocol: signal at H1 close; entry at next H1 open; +100 pips measured over the following 48 H1 bars; events are non-overlapping.
Discovery only. This study identifies candidate state changes; it does not freeze a notification rule.

## Repeated boolean states before +100 pip moves

|Pair|Dir|Feature|Event rate|Baseline rate|Lift|Events|
|---|---|---|---:|---:|---:|---:|
|usdcad|short|break20_up|0.466|0.061|0.405|176|
|eurusd|short|break20_up|0.455|0.056|0.399|154|
|audusd|short|break20_up|0.423|0.060|0.363|137|
|gbpusd|long|break20_down|0.408|0.059|0.350|213|
|audusd|long|break20_down|0.385|0.059|0.326|122|
|nzdusd|short|break20_up|0.365|0.058|0.307|115|
|eurjpy|long|break20_down|0.353|0.047|0.306|258|
|eurjpy|short|break20_up|0.358|0.071|0.287|218|
|audjpy|long|break20_down|0.332|0.048|0.284|193|
|gbpusd|short|break20_up|0.338|0.059|0.279|225|
|usdchf|long|break20_down|0.330|0.053|0.278|112|
|eurgbp|short|break20_up|0.324|0.049|0.275|37|
|eurgbp|long|break20_down|0.326|0.053|0.273|43|
|eurusd|long|break20_down|0.331|0.060|0.271|145|
|gbpjpy|long|break20_down|0.316|0.046|0.270|310|
|usdchf|short|break20_up|0.324|0.056|0.267|102|
|gbpjpy|short|break20_up|0.321|0.070|0.251|277|
|usdjpy|long|break20_down|0.286|0.041|0.244|231|
|nzdusd|long|break20_down|0.294|0.059|0.235|102|
|audjpy|short|break20_up|0.306|0.071|0.234|180|
|usdcad|long|break20_down|0.293|0.063|0.230|181|
|usdjpy|short|break20_up|0.295|0.073|0.222|183|
|audnzd|long|break20_down|0.254|0.044|0.210|67|
|eurgbp|short|trend_up|0.514|0.320|0.194|37|
|audnzd|short|break20_up|0.196|0.058|0.138|51|
|audnzd|long|trend_down|0.448|0.362|0.086|67|
|usdcad|short|trend_up|0.449|0.382|0.067|176|
|audjpy|long|trend_down|0.352|0.286|0.066|193|
|nzdusd|short|trend_up|0.409|0.343|0.066|115|
|nzdusd|long|trend_down|0.441|0.379|0.062|102|
|gbpusd|long|trend_down|0.413|0.363|0.050|213|
|audnzd|short|trend_up|0.412|0.368|0.043|51|
|audusd|long|trend_down|0.426|0.387|0.040|122|
|usdchf|long|trend_up|0.420|0.381|0.038|112|
|eurjpy|long|trend_down|0.318|0.282|0.036|258|
|gbpjpy|short|trend_down|0.307|0.275|0.032|277|
|usdchf|short|pullback_down|0.118|0.096|0.022|102|
|usdchf|short|trend_up|0.402|0.381|0.021|102|
|gbpjpy|long|trend_down|0.290|0.275|0.015|310|
|audusd|long|pullback_up|0.107|0.092|0.014|122|

## Largest numeric state changes (median vs baseline)

|Pair|Dir|Feature|Event median|Baseline median|Median delta|Events|
|---|---|---|---:|---:|---:|---:|
|usdcad|short|rsi14|64.17|49.72|14.45|176|
|audusd|short|rsi14|64.28|50.12|14.16|137|
|eurusd|short|rsi14|62.6|49.53|13.08|154|
|audusd|long|rsi14|37.35|50.12|-12.77|122|
|nzdusd|short|rsi14|62.55|49.87|12.68|115|
|eurjpy|long|rsi14|39.53|51.98|-12.46|258|
|gbpusd|long|rsi14|37.62|50.05|-12.43|213|
|audjpy|long|rsi14|39.47|51.87|-12.4|193|
|eurusd|long|rsi14|38.52|49.53|-11.01|145|
|nzdusd|long|rsi14|39.27|49.87|-10.6|102|
|usdchf|long|rsi14|40.48|50.54|-10.06|112|
|usdjpy|long|rsi14|43.2|52.81|-9.609|231|
|gbpusd|short|rsi14|59.39|50.05|9.34|225|
|audnzd|long|rsi14|40.73|50.07|-9.339|67|
|usdchf|short|rsi14|59.88|50.54|9.338|102|
|eurgbp|short|rsi14|58.19|49.07|9.121|37|
|gbpjpy|long|rsi14|42.91|51.97|-9.06|310|
|usdcad|long|rsi14|40.92|49.72|-8.795|181|
|audnzd|short|rsi14|58.67|50.07|8.596|51|
|audjpy|short|rsi14|60.21|51.87|8.346|180|
|eurjpy|short|rsi14|59.97|51.98|7.983|218|
|gbpjpy|short|rsi14|58.43|51.97|6.457|277|
|usdjpy|short|rsi14|58.37|52.81|5.561|183|
|eurgbp|long|rsi14|43.66|49.07|-5.412|43|
|eurgbp|short|dist_ema200_atr|2.963|-0.5379|3.501|37|
|audjpy|short|adx14|25.36|22.7|2.653|180|
|usdchf|short|adx14|25.68|23.04|2.648|102|
|gbpjpy|short|adx14|25.65|23.08|2.577|277|
|usdcad|short|dist_ema200_atr|2.509|0.1432|2.365|176|
|usdjpy|short|adx14|26.55|24.19|2.364|183|
|audjpy|long|dist_ema200_atr|-1.496|0.7364|-2.232|193|
|usdchf|short|dist_ema200_atr|2.141|0.1092|2.032|102|
|usdchf|long|adx14|25.02|23.04|1.983|112|
|audusd|short|dist_ema200_atr|1.447|-0.5171|1.964|137|
|eurusd|short|dist_ema200_atr|1.335|-0.5929|1.928|154|
|eurjpy|long|dist_ema200_atr|-0.7679|1.122|-1.89|258|
|audnzd|short|adx14|20.56|22.44|-1.882|51|
|usdjpy|long|adx14|26.06|24.19|1.875|231|
|gbpusd|long|dist_ema200_atr|-1.826|-0.08879|-1.737|213|
|audusd|long|dist_ema200_atr|-2.227|-0.5171|-1.71|122|
