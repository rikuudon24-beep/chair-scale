# H1 +100 Pip Precursor Study

Protocol: signal at H1 close; entry at next H1 open; +100 pips measured over the following 48 H1 bars; events are non-overlapping.
Discovery only. This study identifies candidate state changes; it does not freeze a notification rule.

## Repeated boolean states before +100 pip moves

|Pair|Dir|Feature|Event rate|Baseline rate|Lift|Events|
|---|---|---|---:|---:|---:|---:|
|usdcad|short|break20_up|0.466|0.061|0.405|176|
|eurusd|short|break20_up|0.451|0.055|0.396|153|
|audusd|short|break20_up|0.423|0.060|0.363|137|
|gbpusd|long|break20_down|0.410|0.059|0.351|212|
|audusd|long|break20_down|0.385|0.059|0.326|122|
|nzdusd|short|break20_up|0.365|0.058|0.307|115|
|eurjpy|long|break20_down|0.346|0.047|0.300|254|
|eurjpy|short|break20_up|0.353|0.071|0.282|215|
|gbpusd|short|break20_up|0.338|0.059|0.279|225|
|usdchf|long|break20_down|0.330|0.052|0.278|112|
|audjpy|long|break20_down|0.325|0.048|0.277|191|
|eurgbp|short|break20_up|0.324|0.049|0.275|37|
|eurusd|long|break20_down|0.333|0.060|0.273|144|
|eurgbp|long|break20_down|0.326|0.053|0.273|43|
|gbpjpy|long|break20_down|0.314|0.046|0.267|306|
|usdchf|short|break20_up|0.324|0.056|0.267|102|
|gbpjpy|short|break20_up|0.318|0.070|0.248|274|
|usdjpy|long|break20_down|0.283|0.041|0.241|230|
|nzdusd|long|break20_down|0.297|0.059|0.238|101|
|audjpy|short|break20_up|0.303|0.071|0.232|178|
|usdcad|long|break20_down|0.293|0.063|0.230|181|
|usdjpy|short|break20_up|0.297|0.073|0.224|182|
|audnzd|long|break20_down|0.254|0.044|0.210|67|
|eurgbp|short|trend_up|0.514|0.325|0.189|37|
|audnzd|short|break20_up|0.196|0.058|0.138|51|
|audnzd|long|trend_down|0.448|0.357|0.091|67|
|audjpy|long|trend_down|0.356|0.287|0.069|191|
|usdcad|short|trend_up|0.449|0.382|0.067|176|
|nzdusd|short|trend_up|0.409|0.343|0.066|115|
|nzdusd|long|trend_down|0.436|0.379|0.056|101|
|gbpusd|long|trend_down|0.410|0.363|0.048|212|
|audusd|long|trend_down|0.426|0.386|0.040|122|
|usdchf|long|trend_up|0.420|0.382|0.038|112|
|audnzd|short|trend_up|0.412|0.374|0.038|51|
|eurjpy|long|trend_down|0.319|0.281|0.038|254|
|gbpjpy|short|trend_down|0.307|0.277|0.029|274|
|usdchf|short|pullback_down|0.118|0.096|0.022|102|
|usdchf|short|trend_up|0.402|0.382|0.020|102|
|gbpjpy|long|trend_down|0.294|0.277|0.017|306|
|audusd|long|pullback_up|0.107|0.092|0.014|122|

## Largest numeric state changes (median vs baseline)

|Pair|Dir|Feature|Event median|Baseline median|Median delta|Events|
|---|---|---|---:|---:|---:|---:|
|usdcad|short|rsi14|64.17|49.73|14.44|176|
|audusd|short|rsi14|64.28|50.12|14.17|137|
|eurusd|short|rsi14|62.59|49.53|13.06|153|
|audusd|long|rsi14|37.35|50.12|-12.76|122|
|nzdusd|short|rsi14|62.55|49.86|12.69|115|
|gbpusd|long|rsi14|37.59|50.04|-12.45|212|
|audjpy|long|rsi14|39.63|51.83|-12.21|191|
|eurjpy|long|rsi14|39.82|52|-12.18|254|
|eurusd|long|rsi14|38.65|49.53|-10.88|144|
|nzdusd|long|rsi14|39.37|49.86|-10.49|101|
|usdchf|long|rsi14|40.48|50.55|-10.06|112|
|audnzd|long|rsi14|40.73|50.13|-9.396|67|
|gbpusd|short|rsi14|59.39|50.04|9.344|225|
|usdchf|short|rsi14|59.88|50.55|9.332|102|
|usdjpy|long|rsi14|43.54|52.81|-9.265|230|
|eurgbp|short|rsi14|58.19|49.13|9.063|37|
|gbpjpy|long|rsi14|43|51.93|-8.931|306|
|usdcad|long|rsi14|40.92|49.73|-8.808|181|
|audnzd|short|rsi14|58.67|50.13|8.54|51|
|audjpy|short|rsi14|60.08|51.83|8.243|178|
|eurjpy|short|rsi14|59.82|52|7.823|215|
|gbpjpy|short|rsi14|58.18|51.93|6.246|274|
|usdjpy|short|rsi14|58.69|52.81|5.878|182|
|eurgbp|long|rsi14|43.66|49.13|-5.47|43|
|eurgbp|short|dist_ema200_atr|2.963|-0.4866|3.45|37|
|usdchf|short|adx14|25.68|23.04|2.643|102|
|audjpy|short|adx14|25.36|22.75|2.604|178|
|usdcad|short|dist_ema200_atr|2.509|0.1405|2.368|176|
|usdjpy|short|adx14|26.58|24.22|2.358|182|
|gbpjpy|short|adx14|25.43|23.11|2.317|274|
|audjpy|long|dist_ema200_atr|-1.488|0.7438|-2.232|191|
|usdchf|short|dist_ema200_atr|2.141|0.1114|2.03|102|
|usdchf|long|adx14|25.02|23.04|1.977|112|
|usdjpy|long|adx14|26.18|24.22|1.964|230|
|audusd|short|dist_ema200_atr|1.447|-0.5152|1.963|137|
|eurusd|short|dist_ema200_atr|1.318|-0.5846|1.903|153|
|audnzd|short|adx14|20.56|22.42|-1.86|51|
|eurjpy|long|dist_ema200_atr|-0.7034|1.141|-1.845|254|
|eurjpy|long|adx14|25.69|23.92|1.764|254|
|audusd|long|dist_ema200_atr|-2.227|-0.5152|-1.712|122|
