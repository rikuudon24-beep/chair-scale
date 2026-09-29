# H1 precursor trade quality

Metrics use next H1 open entry and non-overlapping 48-H1 outcome windows. MFE/MAE are excursion over the full window; target100_h1 is first H1 bar reaching +100 pips.

|Pair|Dir|Conditions|Split|Trades|Hit|MFE med|MFE p75|MAE med|MAE p75|100p med H1|100p p25|100p p75|
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|gbpjpy|long|trend_down & rsi55_60 & far_ema200|discovery|81|0.605|117.1|187.4|60.8|142.4|23.0|11.0|31.0|
|gbpjpy|long|trend_down & rsi55_60 & far_ema200|validation|24|0.458|89.5|176.0|178.3|248.5|11.0|5.5|15.5|
|gbpjpy|long|trend_down & rsi55_60 & far_ema200|oos|16|0.625|116.6|130.7|34.1|87.5|24.0|10.2|31.5|
|gbpjpy|long|trend_down & macd_pos & d1_bull|discovery|85|0.600|119.8|181.2|67.5|155.3|15.0|10.5|30.0|
|gbpjpy|long|trend_down & macd_pos & d1_bull|validation|25|0.640|153.6|224.8|113.6|218.4|20.0|7.8|32.0|
|gbpjpy|long|trend_down & macd_pos & d1_bull|oos|25|0.560|103.8|172.7|64.2|115.4|14.5|8.8|22.2|
|gbpjpy|long|trend_down & far_ema200 & d1_bull|discovery|101|0.584|121.1|187.5|63.5|156.7|16.0|10.5|33.0|
|gbpjpy|long|trend_down & far_ema200 & d1_bull|validation|33|0.576|152.0|239.0|96.8|235.7|17.0|10.0|30.5|
|gbpjpy|long|trend_down & far_ema200 & d1_bull|oos|32|0.531|110.1|175.6|54.0|100.2|10.0|8.0|23.0|
|gbpjpy|long|trend_down & d1_bull|discovery|103|0.583|121.1|185.5|63.5|157.6|16.0|11.0|31.2|
|gbpjpy|long|trend_down & d1_bull|validation|35|0.571|152.0|229.9|96.8|232.9|20.5|11.0|30.0|
|gbpjpy|long|trend_down & d1_bull|oos|32|0.531|110.1|175.6|54.0|100.2|10.0|8.0|23.0|
|gbpjpy|long|trend_down & atr_above_med & d1_bull|discovery|79|0.595|125.7|196.2|87.8|157.6|16.0|10.5|30.0|
|gbpjpy|long|trend_down & atr_above_med & d1_bull|validation|27|0.519|110.6|221.8|181.3|252.3|23.5|10.2|32.0|
|gbpjpy|long|trend_down & atr_above_med & d1_bull|oos|25|0.480|95.3|173.4|53.6|99.7|10.5|5.8|23.0|
|gbpjpy|long|adx25+ & rsi>60 & d1_bear|discovery|73|0.589|113.0|206.2|65.8|106.1|21.0|10.5|29.0|
|gbpjpy|long|adx25+ & rsi>60 & d1_bear|validation|28|0.429|86.3|149.3|127.7|247.0|18.5|7.5|30.0|
|gbpjpy|long|adx25+ & rsi>60 & d1_bear|oos|24|0.292|65.0|109.2|87.4|142.8|32.0|25.0|38.0|
|gbpjpy|long|trend_down & d1_bull & w1_bull|discovery|51|0.608|125.7|182.4|83.7|177.2|15.0|11.0|27.5|
|gbpjpy|long|trend_down & d1_bull & w1_bull|validation|19|0.579|152.0|185.0|128.1|173.9|25.0|20.5|32.0|
|gbpjpy|long|trend_down & d1_bull & w1_bull|oos|24|0.500|114.2|182.8|38.0|96.1|9.0|7.2|10.5|
|gbpjpy|long|trend_down & d1_bull & rsi_up6|discovery|89|0.573|117.1|190.2|83.7|159.6|17.0|9.5|34.0|
|gbpjpy|long|trend_down & d1_bull & rsi_up6|validation|31|0.645|171.0|235.3|94.2|214.4|13.0|8.8|29.8|
|gbpjpy|long|trend_down & d1_bull & rsi_up6|oos|25|0.520|104.8|153.4|64.0|98.2|12.0|10.0|23.0|
|gbpjpy|long|trend_down & rsi55_60 & d1_bull|discovery|61|0.590|117.7|187.5|62.7|152.5|16.0|10.5|23.8|
|gbpjpy|long|trend_down & rsi55_60 & d1_bull|validation|19|0.579|112.7|212.0|175.5|278.9|18.0|8.5|33.5|
|gbpjpy|long|trend_down & rsi55_60 & d1_bull|oos|15|0.600|118.5|151.3|55.2|73.6|27.0|12.0|34.0|
|gbpjpy|long|trend_down & adx20+ & rsi>60|discovery|71|0.577|109.4|196.0|63.9|117.8|17.0|10.0|27.0|
|gbpjpy|long|trend_down & adx20+ & rsi>60|validation|21|0.429|85.1|175.8|109.1|223.3|7.0|3.0|19.0|
|gbpjpy|long|trend_down & adx20+ & rsi>60|oos|20|0.400|94.5|118.8|68.8|124.2|17.5|8.5|25.2|
|gbpjpy|long|trend_down & adx25+ & d1_bull|discovery|71|0.577|121.1|201.5|82.2|159.6|15.0|9.0|31.0|
|gbpjpy|long|trend_down & adx25+ & d1_bull|validation|19|0.526|110.6|212.6|180.0|244.2|11.5|7.5|26.5|
|gbpjpy|long|trend_down & adx25+ & d1_bull|oos|19|0.526|126.0|196.3|54.3|137.7|9.5|8.2|23.8|
|gbpjpy|long|trend_down & rsi>60 & macd_pos|discovery|95|0.558|106.1|191.1|63.9|141.1|20.0|10.0|27.0|
|gbpjpy|long|trend_down & rsi>60 & macd_pos|validation|30|0.467|87.5|173.6|115.0|252.3|7.5|4.5|11.5|
|gbpjpy|long|trend_down & rsi>60 & macd_pos|oos|24|0.458|97.3|119.9|69.2|101.9|23.0|12.5|31.0|
|gbpjpy|long|trend_down & h4_bull & d1_bull|discovery|82|0.561|115.8|182.9|83.0|155.6|16.0|9.5|29.8|
|gbpjpy|long|trend_down & h4_bull & d1_bull|validation|31|0.613|154.3|229.0|128.4|237.0|15.0|11.0|27.0|
|gbpjpy|long|trend_down & h4_bull & d1_bull|oos|26|0.615|118.7|183.0|46.3|89.2|15.5|9.0|25.5|
|gbpjpy|long|trend_down & adx20+ & rsi55_60|discovery|86|0.558|114.0|186.2|64.8|142.9|17.5|9.8|29.2|
|gbpjpy|long|trend_down & adx20+ & rsi55_60|validation|26|0.423|84.9|157.9|158.4|239.6|11.0|5.5|16.0|
|gbpjpy|long|trend_down & adx20+ & rsi55_60|oos|22|0.500|94.5|129.9|53.1|87.8|28.0|13.5|34.0|
|gbpjpy|long|trend_down & rsi>60|discovery|96|0.552|105.5|190.9|66.6|140.7|20.0|10.0|27.0|
|gbpjpy|long|trend_down & rsi>60|validation|30|0.467|87.5|173.6|115.0|252.3|7.5|4.5|11.5|
|gbpjpy|long|trend_down & rsi>60|oos|24|0.458|97.3|119.9|69.2|101.9|23.0|12.5|31.0|
