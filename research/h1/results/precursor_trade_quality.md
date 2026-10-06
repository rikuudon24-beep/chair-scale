# H1 precursor trade quality

Metrics use next H1 open entry and non-overlapping 48-H1 outcome windows. MFE/MAE are excursion over the full window; target100_h1 is first H1 bar reaching +100 pips.

|Pair|Dir|Conditions|Split|Trades|Hit|MFE med|MFE p75|MAE med|MAE p75|100p med H1|100p p25|100p p75|
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|gbpjpy|long|trend_down & rsi55_60 & far_ema200|discovery|82|0.610|118.3|187.3|60.2|141.8|21.0|9.5|30.8|
|gbpjpy|long|trend_down & rsi55_60 & far_ema200|validation|23|0.435|88.2|180.7|195.9|249.4|11.5|5.2|16.8|
|gbpjpy|long|trend_down & rsi55_60 & far_ema200|oos|18|0.611|114.8|131.2|34.1|87.6|20.0|6.0|31.0|
|gbpjpy|long|trend_down & macd_pos & d1_bull|discovery|85|0.600|119.8|181.2|67.5|155.3|15.0|10.5|30.0|
|gbpjpy|long|trend_down & macd_pos & d1_bull|validation|27|0.593|146.5|219.7|113.6|206.1|20.0|7.8|32.0|
|gbpjpy|long|trend_down & macd_pos & d1_bull|oos|26|0.538|102.9|158.5|72.1|120.8|14.5|8.8|22.2|
|gbpjpy|long|trend_down & far_ema200 & d1_bull|discovery|101|0.584|121.1|187.5|63.5|156.7|16.0|10.5|33.0|
|gbpjpy|long|trend_down & far_ema200 & d1_bull|validation|36|0.528|121.6|233.7|95.6|231.5|17.0|10.0|30.5|
|gbpjpy|long|trend_down & far_ema200 & d1_bull|oos|33|0.515|105.7|173.4|55.2|119.4|10.0|8.0|23.0|
|gbpjpy|long|trend_down & d1_bull|discovery|104|0.577|121.0|184.8|66.8|157.2|16.0|11.0|31.2|
|gbpjpy|long|trend_down & d1_bull|validation|37|0.541|132.7|228.0|96.8|230.1|20.5|11.0|30.0|
|gbpjpy|long|trend_down & d1_bull|oos|33|0.515|105.7|173.4|55.2|119.4|10.0|8.0|23.0|
|gbpjpy|long|trend_down & atr_above_med & d1_bull|discovery|80|0.588|124.7|194.7|85.8|157.2|16.0|10.5|30.0|
|gbpjpy|long|trend_down & atr_above_med & d1_bull|validation|28|0.500|98.8|216.7|168.7|248.7|23.5|10.2|32.0|
|gbpjpy|long|trend_down & atr_above_med & d1_bull|oos|27|0.481|95.3|164.5|54.4|138.6|12.0|6.0|23.0|
|gbpjpy|long|trend_down & d1_bull & rsi_up6|discovery|89|0.573|117.1|190.2|83.7|159.6|17.0|9.5|34.0|
|gbpjpy|long|trend_down & d1_bull & rsi_up6|validation|33|0.606|159.6|231.6|93.7|210.4|13.0|8.8|29.8|
|gbpjpy|long|trend_down & d1_bull & rsi_up6|oos|28|0.500|101.8|148.3|64.5|115.4|13.0|10.0|23.0|
|gbpjpy|long|trend_down & rsi55_60 & d1_bull|discovery|61|0.590|117.7|187.5|62.7|152.5|16.0|10.5|23.8|
|gbpjpy|long|trend_down & rsi55_60 & d1_bull|validation|20|0.550|112.6|210.7|174.6|274.5|18.0|8.5|33.5|
|gbpjpy|long|trend_down & rsi55_60 & d1_bull|oos|15|0.600|116.0|139.1|55.2|88.9|27.0|12.0|34.0|
|gbpjpy|long|trend_down & adx25+ & d1_bull|discovery|71|0.577|121.1|201.5|82.2|159.6|15.0|9.0|31.0|
|gbpjpy|long|trend_down & adx25+ & d1_bull|validation|20|0.500|91.2|203.0|168.0|243.8|11.5|7.5|26.5|
|gbpjpy|long|trend_down & adx25+ & d1_bull|oos|23|0.478|96.8|188.6|54.4|171.5|10.0|8.5|24.0|
|gbpjpy|long|trend_down & d1_bull & w1_bull|discovery|52|0.596|123.4|181.8|83.0|176.9|15.0|11.0|27.5|
|gbpjpy|long|trend_down & d1_bull & w1_bull|validation|21|0.524|110.6|176.5|128.1|166.4|25.0|20.5|32.0|
|gbpjpy|long|trend_down & d1_bull & w1_bull|oos|23|0.522|131.7|183.6|39.5|86.1|9.0|7.2|10.5|
|gbpjpy|long|trend_down & adx20+ & rsi55_60|discovery|87|0.563|114.6|185.3|63.5|142.7|17.0|9.0|29.0|
|gbpjpy|long|trend_down & adx20+ & rsi55_60|validation|27|0.407|81.7|155.6|156.0|235.0|12.0|5.5|20.5|
|gbpjpy|long|trend_down & adx20+ & rsi55_60|oos|21|0.476|88.7|135.3|47.5|87.6|21.5|5.5|31.0|
|gbpjpy|long|adx25+ & rsi>60 & d1_bear|discovery|76|0.566|107.9|202.8|66.3|106.4|21.0|10.5|29.0|
|gbpjpy|long|adx25+ & rsi>60 & d1_bear|validation|27|0.444|87.4|152.4|138.5|255.2|18.5|7.5|30.0|
|gbpjpy|long|adx25+ & rsi>60 & d1_bear|oos|23|0.348|67.0|126.1|82.8|111.7|29.0|23.8|36.0|
|gbpjpy|long|trend_down & h4_bull & d1_bull|discovery|82|0.561|115.8|182.9|83.0|155.6|16.0|9.5|29.8|
|gbpjpy|long|trend_down & h4_bull & d1_bull|validation|33|0.576|152.0|228.4|113.2|235.0|15.0|11.0|27.0|
|gbpjpy|long|trend_down & h4_bull & d1_bull|oos|26|0.577|113.7|168.7|54.4|96.5|12.0|9.0|25.0|
|gbpjpy|long|trend_down & rsi55_60 & w1_bull|discovery|53|0.585|122.9|181.2|90.9|174.4|19.0|11.5|29.5|
|gbpjpy|long|trend_down & rsi55_60 & w1_bull|validation|23|0.522|112.5|162.3|131.1|220.1|18.0|11.0|27.5|
|gbpjpy|long|trend_down & rsi55_60 & w1_bull|oos|18|0.556|107.0|134.1|40.7|72.7|26.0|14.0|30.8|
