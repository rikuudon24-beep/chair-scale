# Systematic H1 Condition Mining

Target: +100 pips within 48 H1 bars.
Discovery only was used to nominate conditions; validation/OOS were not used for selection.
Gate: discovery n >= 50, hit rate >= 55%, Wilson 95% lower bound >= 45%.

## Validation/OOS candidates

|Pair|Dir|Conditions|Split|Trades|Hit rate|LCB95|Mean MFE|Median MFE|Mean MAE|
|---|---|---|---|---:|---:|---:|---:|---:|---:|
|gbpjpy|long|adx25+ & rsi_extreme_low & atr_above_med|validation|215|0.995|0.974|406.2|349.1|-50.8|
|gbpjpy|long|adx25+ & rsi_extreme_low & atr_above_med|oos|169|1.000|0.978|293.9|252.9|-39.4|
|gbpjpy|short|adx25+ & rsi_extreme_high & w1_bear|validation|123|1.000|0.970|311.7|308.8|-19.6|
|gbpjpy|short|adx25+ & rsi_extreme_high & w1_bear|oos|146|1.000|0.974|232.1|221.2|-15.4|
|gbpjpy|long|adx20+ & rsi_extreme_low & atr_above_med|validation|226|0.996|0.975|398.8|343.1|-50.8|
|gbpjpy|long|adx20+ & rsi_extreme_low & atr_above_med|oos|181|1.000|0.979|286.1|245.4|-39.7|
|gbpjpy|long|rsi_extreme_low & atr_above_med & w1_bull|validation|124|0.992|0.956|318.1|304.8|-49.4|
|gbpjpy|long|rsi_extreme_low & atr_above_med & w1_bull|oos|111|1.000|0.967|277.6|255.8|-42.8|
|gbpjpy|short|adx25+ & rsi_extreme_high & dist_ema20_far|validation|302|1.000|0.987|285.5|270.5|-20.1|
|gbpjpy|short|adx25+ & rsi_extreme_high & dist_ema20_far|oos|307|0.997|0.982|253.1|233.6|-17.0|
|gbpjpy|short|rsi_extreme_high & atr_above_med & w1_bear|validation|59|1.000|0.939|317.1|285.8|-21.1|
|gbpjpy|short|rsi_extreme_high & atr_above_med & w1_bear|oos|76|1.000|0.952|234.3|226.7|-17.3|
|gbpjpy|long|rsi_extreme_low & atr_above_med|validation|231|0.996|0.976|395.2|333.2|-51.0|
|gbpjpy|long|rsi_extreme_low & atr_above_med|oos|186|0.995|0.970|282.1|239.3|-39.4|
|gbpjpy|long|rsi_extreme_low & atr_above_med & dist_ema20_far|validation|231|0.996|0.976|395.2|333.2|-51.0|
|gbpjpy|long|rsi_extreme_low & atr_above_med & dist_ema20_far|oos|186|0.995|0.970|282.1|239.3|-39.4|
|gbpjpy|short|adx25+ & rsi_extreme_high & atr_above_med|validation|128|1.000|0.971|307.4|293.5|-22.8|
|gbpjpy|short|adx25+ & rsi_extreme_high & atr_above_med|oos|175|1.000|0.979|277.3|260.3|-18.7|
|gbpjpy|short|adx20+ & rsi_extreme_high & atr_above_med|validation|160|1.000|0.977|303.2|281.7|-24.1|
|gbpjpy|short|adx20+ & rsi_extreme_high & atr_above_med|oos|204|1.000|0.982|263.8|246.2|-19.8|
|gbpjpy|short|adx20+ & rsi_extreme_high & w1_bear|validation|156|1.000|0.976|306.7|294.7|-20.4|
|gbpjpy|short|adx20+ & rsi_extreme_high & w1_bear|oos|166|1.000|0.977|229.6|219.5|-15.2|
|gbpjpy|short|rsi_extreme_high & atr_above_med|validation|179|1.000|0.979|297.8|273.4|-23.7|
|gbpjpy|short|rsi_extreme_high & atr_above_med|oos|217|1.000|0.983|258.9|239.5|-19.7|
|gbpjpy|short|rsi_extreme_high & atr_above_med & dist_ema20_far|validation|179|1.000|0.979|297.8|273.4|-23.7|
|gbpjpy|short|rsi_extreme_high & atr_above_med & dist_ema20_far|oos|217|1.000|0.983|258.9|239.5|-19.7|
|gbpjpy|short|adx20+ & rsi_extreme_high & dist_ema20_far|validation|375|1.000|0.990|279.3|266.5|-21.0|
|gbpjpy|short|adx20+ & rsi_extreme_high & dist_ema20_far|oos|359|0.997|0.984|243.4|224.0|-17.6|
|gbpjpy|long|rsi_extreme_low & atr_above_med & body_strong|validation|97|0.990|0.944|386.1|325.7|-48.4|
|gbpjpy|long|rsi_extreme_low & atr_above_med & body_strong|oos|65|1.000|0.944|270.7|240.0|-42.7|
|gbpjpy|short|adx25+ & rsi_extreme_high|validation|302|1.000|0.987|285.5|270.5|-20.1|
|gbpjpy|short|adx25+ & rsi_extreme_high|oos|307|0.997|0.982|253.1|233.6|-17.0|
|gbpjpy|short|adx20+ & adx25+ & rsi_extreme_high|validation|302|1.000|0.987|285.5|270.5|-20.1|
|gbpjpy|short|adx20+ & adx25+ & rsi_extreme_high|oos|307|0.997|0.982|253.1|233.6|-17.0|
|gbpjpy|short|rsi_extreme_high & w1_bear|validation|177|1.000|0.979|300.1|287.6|-21.5|
|gbpjpy|short|rsi_extreme_high & w1_bear|oos|182|0.995|0.970|226.6|216.7|-14.8|
|gbpjpy|short|rsi_extreme_high & dist_ema20_far & w1_bear|validation|177|1.000|0.979|300.1|287.6|-21.5|
|gbpjpy|short|rsi_extreme_high & dist_ema20_far & w1_bear|oos|182|0.995|0.970|226.6|216.7|-14.8|
|gbpjpy|long|adx25+ & rsi_extreme_low|validation|252|0.996|0.978|388.0|328.7|-47.2|
|gbpjpy|long|adx25+ & rsi_extreme_low|oos|219|0.982|0.954|280.0|237.8|-35.4|
|gbpjpy|long|adx20+ & adx25+ & rsi_extreme_low|validation|252|0.996|0.978|388.0|328.7|-47.2|
|gbpjpy|long|adx20+ & adx25+ & rsi_extreme_low|oos|219|0.982|0.954|280.0|237.8|-35.4|
|gbpjpy|long|adx25+ & rsi_extreme_low & dist_ema20_far|validation|252|0.996|0.978|388.0|328.7|-47.2|
|gbpjpy|long|adx25+ & rsi_extreme_low & dist_ema20_far|oos|219|0.982|0.954|280.0|237.8|-35.4|
|gbpjpy|long|adx25+ & rsi_extreme_low & body_strong|validation|105|0.990|0.948|379.0|322.8|-43.5|
|gbpjpy|long|adx25+ & rsi_extreme_low & body_strong|oos|74|0.973|0.907|269.4|240.9|-38.2|
|gbpjpy|short|rsi_extreme_high & dist_ema20_far|validation|419|0.995|0.983|272.8|260.5|-21.5|
|gbpjpy|short|rsi_extreme_high & dist_ema20_far|oos|402|0.985|0.968|235.5|216.7|-17.1|
|gbpjpy|short|adx20+ & rsi_extreme_high|validation|375|1.000|0.990|279.3|266.5|-21.0|
|gbpjpy|short|adx20+ & rsi_extreme_high|oos|359|0.997|0.984|243.4|224.0|-17.6|
|gbpjpy|long|adx20+ & rsi_extreme_low|validation|267|0.996|0.979|379.8|324.3|-46.9|
|gbpjpy|long|adx20+ & rsi_extreme_low|oos|247|0.972|0.943|265.9|224.0|-35.1|
|gbpjpy|long|adx20+ & rsi_extreme_low & dist_ema20_far|validation|267|0.996|0.979|379.8|324.3|-46.9|
|gbpjpy|long|adx20+ & rsi_extreme_low & dist_ema20_far|oos|247|0.972|0.943|265.9|224.0|-35.1|
|gbpjpy|short|adx25+ & rsi_extreme_high & bb_below_med|validation|22|1.000|0.851|293.3|279.1|-13.2|
|gbpjpy|short|adx25+ & rsi_extreme_high & bb_below_med|oos|20|1.000|0.839|205.8|198.4|-20.0|
|gbpusd|short|rsi_extreme_high & macd_neg & dist_ema20_far|validation|28|0.750|0.566|144.0|135.1|-14.1|
|gbpusd|short|rsi_extreme_high & macd_neg & dist_ema20_far|oos|28|0.893|0.728|173.2|166.0|-14.9|
|gbpjpy|long|adx20+ & rsi_extreme_low & body_strong|validation|113|0.991|0.952|370.6|312.8|-43.0|
|gbpjpy|long|adx20+ & rsi_extreme_low & body_strong|oos|89|0.978|0.922|254.7|216.9|-37.6|
|gbpjpy|short|adx25+ & rsi_extreme_high & body_strong|validation|92|1.000|0.960|306.8|296.6|-17.8|
|gbpjpy|short|adx25+ & rsi_extreme_high & body_strong|oos|103|0.990|0.947|251.5|233.1|-18.2|
|gbpjpy|long|rsi30_45 & macd_pos & dist_ema20_far|validation|117|1.000|0.968|373.1|296.6|-54.2|
|gbpjpy|long|rsi30_45 & macd_pos & dist_ema20_far|oos|106|0.981|0.934|261.4|213.6|-48.2|
|gbpjpy|long|rsi_extreme_low|validation|275|0.996|0.980|375.1|322.0|-46.8|
|gbpjpy|long|rsi_extreme_low|oos|261|0.962|0.931|258.7|216.4|-34.5|
|gbpjpy|long|rsi_extreme_low & dist_ema20_far|validation|275|0.996|0.980|375.1|322.0|-46.8|
|gbpjpy|long|rsi_extreme_low & dist_ema20_far|oos|261|0.962|0.931|258.7|216.4|-34.5|
|gbpjpy|short|rsi_extreme_high|validation|419|0.995|0.983|272.8|260.5|-21.5|
|gbpjpy|short|rsi_extreme_high|oos|402|0.985|0.968|235.5|216.7|-17.1|
|gbpjpy|short|rsi_extreme_high & atr_above_med & body_strong|validation|71|1.000|0.949|309.0|291.7|-22.8|
|gbpjpy|short|rsi_extreme_high & atr_above_med & body_strong|oos|79|1.000|0.954|250.7|229.6|-19.8|
|gbpusd|short|adx25+ & rsi_extreme_high & atr_above_med|validation|245|0.906|0.863|167.7|160.1|-16.5|
|gbpusd|short|adx25+ & rsi_extreme_high & atr_above_med|oos|176|0.926|0.878|166.4|158.8|-16.7|
|gbpjpy|short|adx20+ & rsi_extreme_high & body_strong|validation|120|1.000|0.969|295.2|287.7|-20.3|
|gbpjpy|short|adx20+ & rsi_extreme_high & body_strong|oos|122|0.992|0.955|239.6|224.9|-18.2|
|gbpjpy|long|rsi_extreme_low & atr_above_med & h4_bull|validation|42|1.000|0.916|344.7|320.0|-57.4|
|gbpjpy|long|rsi_extreme_low & atr_above_med & h4_bull|oos|31|1.000|0.890|352.7|309.6|-41.9|
|usdjpy|short|rsi_extreme_high & macd_neg & atr_above_med|validation|16|1.000|0.806|306.4|321.7|-22.5|
|usdjpy|short|rsi_extreme_high & macd_neg & atr_above_med|oos|30|0.833|0.664|226.8|167.2|-14.3|
|gbpjpy|long|rsi30_45 & macd_pos & atr_above_med|validation|251|1.000|0.985|346.2|296.6|-88.6|
|gbpjpy|long|rsi30_45 & macd_pos & atr_above_med|oos|235|0.957|0.923|254.3|217.4|-74.1|
|gbpjpy|long|adx25+ & rsi30_45 & macd_pos|validation|314|1.000|0.988|325.2|282.6|-78.2|
|gbpjpy|long|adx25+ & rsi30_45 & macd_pos|oos|301|0.907|0.869|235.1|195.9|-65.6|
|gbpusd|long|rsi_extreme_low & macd_pos|validation|16|0.938|0.717|167.5|178.0|-18.6|
|gbpusd|long|rsi_extreme_low & macd_pos|oos|27|0.889|0.719|186.8|197.7|-8.5|
|gbpusd|long|adx20+ & rsi_extreme_low & macd_pos|validation|16|0.938|0.717|167.5|178.0|-18.6|
|gbpusd|long|adx20+ & rsi_extreme_low & macd_pos|oos|27|0.889|0.719|186.8|197.7|-8.5|
|gbpusd|long|adx25+ & rsi_extreme_low & macd_pos|validation|15|0.933|0.702|170.2|182.4|-19.7|
|gbpusd|long|adx25+ & rsi_extreme_low & macd_pos|oos|27|0.889|0.719|186.8|197.7|-8.5|
|gbpusd|long|rsi_extreme_low & macd_pos & dist_ema20_far|validation|16|0.938|0.717|167.5|178.0|-18.6|
|gbpusd|long|rsi_extreme_low & macd_pos & dist_ema20_far|oos|27|0.889|0.719|186.8|197.7|-8.5|
|gbpjpy|short|rsi55_70 & macd_neg & dist_ema20_far|validation|159|0.969|0.929|271.4|258.8|-29.8|
|gbpjpy|short|rsi55_70 & macd_neg & dist_ema20_far|oos|155|0.981|0.945|203.6|176.5|-22.7|
|gbpjpy|long|rsi_extreme_low & atr_above_med & d1_bull|validation|73|1.000|0.950|308.4|306.9|-51.1|
|gbpjpy|long|rsi_extreme_low & atr_above_med & d1_bull|oos|98|0.990|0.944|296.5|235.0|-53.0|
|gbpjpy|short|rsi_extreme_high & body_strong & dist_ema20_far|validation|148|0.986|0.952|283.9|272.4|-21.0|
|gbpjpy|short|rsi_extreme_high & body_strong & dist_ema20_far|oos|145|0.993|0.962|227.8|214.7|-17.4|
|gbpjpy|short|adx25+ & rsi55_70 & macd_neg|validation|259|0.954|0.921|264.3|249.8|-45.5|
|gbpjpy|short|adx25+ & rsi55_70 & macd_neg|oos|273|1.000|0.986|212.5|194.4|-36.4|
|gbpjpy|long|adx25+ & rsi_extreme_low & w1_bull|validation|118|0.992|0.954|325.0|310.5|-47.4|
|gbpjpy|long|adx25+ & rsi_extreme_low & w1_bull|oos|134|0.985|0.947|279.7|254.6|-38.0|
|gbpjpy|short|rsi_extreme_high & body_strong & w1_bear|validation|58|1.000|0.938|318.8|301.4|-20.3|
|gbpjpy|short|rsi_extreme_high & body_strong & w1_bear|oos|60|1.000|0.940|212.8|212.1|-13.6|
|gbpjpy|long|adx20+ & rsi_extreme_low & w1_bull|validation|130|0.992|0.958|318.4|305.3|-47.5|
|gbpjpy|long|adx20+ & rsi_extreme_low & w1_bull|oos|154|0.968|0.926|264.7|237.5|-37.3|
|eurjpy|short|rsi_extreme_high & macd_neg & w1_bear|validation|13|1.000|0.772|437.0|474.2|-28.5|
|eurjpy|short|rsi_extreme_high & macd_neg & w1_bear|oos|8|1.000|0.676|173.6|160.1|-8.1|
|gbpjpy|short|rsi_extreme_high & body_strong|validation|148|0.986|0.952|283.9|272.4|-21.0|
|gbpjpy|short|rsi_extreme_high & body_strong|oos|145|0.993|0.962|227.8|214.7|-17.4|
|gbpjpy|long|rsi_extreme_low & body_strong|validation|120|0.992|0.954|360.8|305.0|-42.9|
|gbpjpy|long|rsi_extreme_low & body_strong|oos|96|0.979|0.927|246.7|207.3|-36.1|
|gbpjpy|long|rsi_extreme_low & body_strong & dist_ema20_far|validation|120|0.992|0.954|360.8|305.0|-42.9|
|gbpjpy|long|rsi_extreme_low & body_strong & dist_ema20_far|oos|96|0.979|0.927|246.7|207.3|-36.1|
|gbpjpy|short|rsi_extreme_high & macd_neg & dist_ema20_far|validation|27|1.000|0.875|294.6|307.0|-21.6|
|gbpjpy|short|rsi_extreme_high & macd_neg & dist_ema20_far|oos|38|1.000|0.908|339.5|356.3|-16.0|
|gbpjpy|short|rsi_extreme_high & macd_neg & atr_above_med|validation|3|1.000|0.438|361.4|402.2|-21.5|
|gbpjpy|short|rsi_extreme_high & macd_neg & atr_above_med|oos|22|1.000|0.851|373.9|356.2|-17.0|
|usdcad|short|rsi_extreme_high & macd_neg & w1_bear|validation|10|0.700|0.397|111.0|115.3|-5.1|
|usdcad|short|rsi_extreme_high & macd_neg & w1_bear|oos|6|0.333|0.097|99.8|96.3|-5.6|
|gbpjpy|long|rsi_extreme_low & w1_bull|validation|135|0.993|0.959|315.3|304.3|-48.0|
|gbpjpy|long|rsi_extreme_low & w1_bull|oos|166|0.958|0.916|255.3|228.5|-36.0|
|gbpjpy|long|rsi_extreme_low & dist_ema20_far & w1_bull|validation|135|0.993|0.959|315.3|304.3|-48.0|
|gbpjpy|long|rsi_extreme_low & dist_ema20_far & w1_bull|oos|166|0.958|0.916|255.3|228.5|-36.0|
|usdcad|short|rsi_extreme_high & macd_neg & atr_above_med|validation|2|1.000|0.342|132.6|132.6|-4.2|
|usdcad|short|rsi_extreme_high & macd_neg & atr_above_med|oos|8|0.875|0.529|139.0|145.5|-7.0|
|gbpusd|long|rsi_extreme_low & macd_pos & atr_above_med|validation|10|1.000|0.722|182.3|183.3|-20.5|
|gbpusd|long|rsi_extreme_low & macd_pos & atr_above_med|oos|20|1.000|0.839|213.9|219.0|-8.9|
|gbpjpy|short|adx20+ & rsi55_70 & macd_neg|validation|420|0.950|0.925|236.0|220.5|-42.3|
|gbpjpy|short|adx20+ & rsi55_70 & macd_neg|oos|355|0.983|0.964|199.7|181.9|-35.3|
|gbpusd|short|adx25+ & rsi_extreme_high & dist_ema20_far|validation|432|0.831|0.793|152.4|144.3|-14.4|
|gbpusd|short|adx25+ & rsi_extreme_high & dist_ema20_far|oos|278|0.881|0.838|153.4|150.7|-14.3|
|gbpjpy|long|adx20+ & rsi30_45 & macd_pos|validation|355|1.000|0.989|310.5|272.3|-75.8|
|gbpjpy|long|adx20+ & rsi30_45 & macd_pos|oos|337|0.908|0.872|224.7|185.7|-62.5|
|gbpjpy|long|adx20+ & rsi_extreme_low & h4_bull|validation|49|1.000|0.927|340.8|321.4|-52.1|
|gbpjpy|long|adx20+ & rsi_extreme_low & h4_bull|oos|34|1.000|0.898|346.0|282.4|-40.7|
|gbpjpy|long|adx25+ & rsi_extreme_low & h4_bull|validation|49|1.000|0.927|340.8|321.4|-52.1|
|gbpjpy|long|adx25+ & rsi_extreme_low & h4_bull|oos|33|1.000|0.896|351.8|306.8|-40.6|
|usdcad|short|rsi_extreme_high & macd_neg|validation|21|0.762|0.549|117.0|109.4|-5.9|
|usdcad|short|rsi_extreme_high & macd_neg|oos|22|0.409|0.233|108.3|96.3|-6.4|
|usdcad|short|adx20+ & rsi_extreme_high & macd_neg|validation|20|0.800|0.584|118.1|112.3|-6.1|
|usdcad|short|adx20+ & rsi_extreme_high & macd_neg|oos|22|0.409|0.233|108.3|96.3|-6.4|
|usdcad|short|adx25+ & rsi_extreme_high & macd_neg|validation|20|0.800|0.584|118.1|112.3|-6.1|
|usdcad|short|adx25+ & rsi_extreme_high & macd_neg|oos|22|0.409|0.233|108.3|96.3|-6.4|
|usdcad|short|rsi_extreme_high & macd_neg & dist_ema20_far|validation|21|0.762|0.549|117.0|109.4|-5.9|
|usdcad|short|rsi_extreme_high & macd_neg & dist_ema20_far|oos|22|0.409|0.233|108.3|96.3|-6.4|
|gbpjpy|short|rsi55_70 & macd_neg & atr_above_med|validation|165|0.945|0.900|252.0|231.0|-48.7|
|gbpjpy|short|rsi55_70 & macd_neg & atr_above_med|oos|213|0.977|0.946|214.3|191.8|-42.2|
|gbpjpy|short|rsi_extreme_high & d1_bear & w1_bear|validation|25|1.000|0.867|316.1|296.6|-23.5|
|gbpjpy|short|rsi_extreme_high & d1_bear & w1_bear|oos|16|1.000|0.806|204.2|201.0|-23.8|
|gbpusd|short|rsi_extreme_high & macd_neg|validation|28|0.750|0.566|144.0|135.1|-14.1|
|gbpusd|short|rsi_extreme_high & macd_neg|oos|28|0.893|0.728|173.2|166.0|-14.9|
|gbpusd|short|adx20+ & rsi_extreme_high & macd_neg|validation|28|0.750|0.566|144.0|135.1|-14.1|
|gbpusd|short|adx20+ & rsi_extreme_high & macd_neg|oos|28|0.893|0.728|173.2|166.0|-14.9|
|gbpusd|short|adx25+ & rsi_extreme_high & macd_neg|validation|26|0.769|0.579|143.5|135.1|-14.7|
|gbpusd|short|adx25+ & rsi_extreme_high & macd_neg|oos|28|0.893|0.728|173.2|166.0|-14.9|
|gbpjpy|long|adx25+ & rsi30_45 & roc_pos|validation|85|1.000|0.957|275.7|264.9|-92.8|
|gbpjpy|long|adx25+ & rsi30_45 & roc_pos|oos|98|0.908|0.835|224.3|186.2|-83.7|
|gbpusd|short|rsi_extreme_high & macd_neg & w1_bear|validation|13|0.769|0.497|131.2|122.5|-16.7|
|gbpusd|short|rsi_extreme_high & macd_neg & w1_bear|oos|16|0.812|0.570|151.2|161.9|-11.8|
