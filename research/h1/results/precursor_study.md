# H1 +100 Pip Precursor Study

Protocol: signal at H1 close; entry at next H1 open; +100 pips measured over the following 48 H1 bars; events are non-overlapping.
Discovery only. This study identifies candidate state changes; it does not freeze a notification rule.

## Repeated boolean states before +100 pip moves

|Pair|Dir|Feature|Event rate|Baseline rate|Lift|Events|
|---|---|---|---:|---:|---:|---:|
|usdcad|short|break20_up|0.460|0.061|0.399|174|
|eurusd|short|break20_up|0.451|0.055|0.395|153|
|audusd|short|break20_up|0.423|0.060|0.363|137|
|gbpusd|long|break20_down|0.410|0.059|0.351|212|
|audusd|long|break20_down|0.385|0.059|0.326|122|
|nzdusd|short|break20_up|0.360|0.057|0.302|114|
|eurjpy|long|break20_down|0.346|0.047|0.300|254|
|eurjpy|short|break20_up|0.353|0.071|0.282|215|
|gbpusd|short|break20_up|0.338|0.058|0.279|225|
|usdchf|long|break20_down|0.330|0.052|0.278|112|
|audjpy|long|break20_down|0.325|0.048|0.277|191|
|eurgbp|short|break20_up|0.324|0.049|0.275|37|
|eurusd|long|break20_down|0.333|0.060|0.273|144|
|usdchf|short|break20_up|0.330|0.057|0.273|100|
|gbpjpy|long|break20_down|0.320|0.047|0.273|300|
|eurgbp|long|break20_down|0.326|0.053|0.273|43|
|gbpjpy|short|break20_up|0.316|0.069|0.247|272|
|usdjpy|long|break20_down|0.283|0.041|0.241|230|
|nzdusd|long|break20_down|0.297|0.059|0.238|101|
|audjpy|short|break20_up|0.303|0.071|0.232|178|
|usdcad|long|break20_down|0.292|0.063|0.229|178|
|usdjpy|short|break20_up|0.297|0.073|0.223|182|
|audnzd|long|break20_down|0.254|0.044|0.210|67|
|eurgbp|short|trend_up|0.514|0.325|0.189|37|
|audnzd|short|break20_up|0.196|0.058|0.138|51|
|audnzd|long|trend_down|0.448|0.357|0.091|67|
|audjpy|long|trend_down|0.356|0.287|0.069|191|
|nzdusd|short|trend_up|0.404|0.339|0.065|114|
|usdcad|short|trend_up|0.443|0.380|0.062|174|
|nzdusd|long|trend_down|0.436|0.383|0.053|101|
|gbpusd|long|trend_down|0.410|0.362|0.048|212|
|audusd|long|trend_down|0.426|0.386|0.040|122|
|audnzd|short|trend_up|0.412|0.374|0.038|51|
|eurjpy|long|trend_down|0.319|0.281|0.038|254|
|usdchf|long|trend_up|0.420|0.385|0.035|112|
|gbpjpy|short|trend_down|0.309|0.281|0.028|272|
|usdchf|short|trend_up|0.410|0.385|0.025|100|
|gbpjpy|long|trend_down|0.297|0.281|0.015|300|
|audusd|long|pullback_up|0.107|0.092|0.014|122|
|usdchf|short|pullback_down|0.110|0.096|0.014|100|

## Largest numeric state changes (median vs baseline)

|Pair|Dir|Feature|Event median|Baseline median|Median delta|Events|
|---|---|---|---:|---:|---:|---:|
|usdcad|short|rsi14|64.02|49.71|14.31|174|
|audusd|short|rsi14|64.28|50.12|14.17|137|
|eurusd|short|rsi14|62.59|49.54|13.05|153|
|audusd|long|rsi14|37.35|50.12|-12.76|122|
|nzdusd|short|rsi14|62.41|49.8|12.61|114|
|gbpusd|long|rsi14|37.59|50.04|-12.44|212|
|audjpy|long|rsi14|39.63|51.83|-12.21|191|
|eurjpy|long|rsi14|39.82|52|-12.18|254|
|eurusd|long|rsi14|38.65|49.54|-10.89|144|
|nzdusd|long|rsi14|39.37|49.8|-10.43|101|
|usdchf|long|rsi14|40.48|50.61|-10.13|112|
|usdchf|short|rsi14|60.35|50.61|9.737|100|
|audnzd|long|rsi14|40.73|50.13|-9.396|67|
|gbpusd|short|rsi14|59.39|50.04|9.349|225|
|usdjpy|long|rsi14|43.54|52.81|-9.267|230|
|gbpjpy|long|rsi14|42.6|51.8|-9.205|300|
|eurgbp|short|rsi14|58.19|49.13|9.063|37|
|usdcad|long|rsi14|41.01|49.71|-8.703|178|
|audnzd|short|rsi14|58.67|50.13|8.54|51|
|audjpy|short|rsi14|60.08|51.83|8.243|178|
|eurjpy|short|rsi14|59.82|52|7.823|215|
|gbpjpy|short|rsi14|57.82|51.8|6.013|272|
|usdjpy|short|rsi14|58.69|52.81|5.876|182|
|eurgbp|long|rsi14|43.66|49.13|-5.47|43|
|eurgbp|short|dist_ema200_atr|2.963|-0.4866|3.45|37|
|usdchf|short|adx14|25.68|23|2.686|100|
|audjpy|short|adx14|25.36|22.75|2.604|178|
|usdjpy|short|adx14|26.58|24.22|2.357|182|
|usdcad|short|dist_ema200_atr|2.458|0.1288|2.329|174|
|gbpjpy|short|adx14|25.43|23.12|2.306|272|
|audjpy|long|dist_ema200_atr|-1.488|0.7438|-2.232|191|
|usdchf|short|dist_ema200_atr|2.219|0.1461|2.073|100|
|usdchf|long|adx14|25.02|23|2.02|112|
|usdjpy|long|adx14|26.18|24.22|1.963|230|
|audusd|short|dist_ema200_atr|1.447|-0.506|1.953|137|
|eurusd|short|dist_ema200_atr|1.318|-0.5806|1.899|153|
|audnzd|short|adx14|20.56|22.42|-1.86|51|
|eurjpy|long|dist_ema200_atr|-0.7034|1.141|-1.845|254|
|eurjpy|long|adx14|25.69|23.92|1.764|254|
|audusd|long|dist_ema200_atr|-2.227|-0.506|-1.721|122|
