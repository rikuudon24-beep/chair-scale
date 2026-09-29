# H1 Research Results

- candidate rows: 1440
- discovery-eligible rows: 30
- follow-up rows: 60

Protocol: signal at confirmed candle close; entry at next H1 open; non-overlapping trades; same-candle TP/SL => conservative SL; chronological 60/20/20 splits with no trade crossing split boundaries.
Selection rule: discovery only; minimum 30 trades, PF >= 1.10 and positive expectancy. Validation/OOS are not used to select rules.

## Validation/OOS follow-up

|Rule|TP|SL|H|Split|Trades|Win rate|PF|Expectancy pips|Total pips|
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
|h4_aligned_long|100|50|72|oos|190|0.410|1.0538345373353257|1.49|293.2|
|h4_aligned_long|100|50|72|validation|226|0.350|0.9907085889050073|-0.33|-102.7|
|h4_aligned_long|150|75|120|oos|203|0.381|0.9610815908473976|-2.42|-668.1|
|h4_aligned_long|150|75|120|validation|233|0.339|0.9725185173737566|-1.35|-286.5|
|meanrev_long|100|50|72|oos|34|0.267|0.7003955683003287|-15.32|-387.0|
|meanrev_long|100|50|72|validation|44|0.402|0.8009140901021765|-8.12|-491.4|
|meanrev_short|75|35|48|oos|26|0.231|0.44596834966088506|-14.14|-367.6|
|meanrev_short|75|35|48|validation|38|0.316|0.5974332995609487|-9.41|-357.6|
|meanrev_short|100|50|72|oos|51|0.395|0.95032128359764|-6.81|-361.9|
|meanrev_short|100|50|72|validation|62|0.456|1.2533817316316664|4.05|206.1|
|meanrev_short|150|75|120|oos|87|0.376|0.7514300564897809|-14.01|-1151.9|
|meanrev_short|150|75|120|validation|101|0.478|1.2463263277767769|4.22|447.1|
|momentum_long|75|35|48|oos|88|0.273|0.5852095600969938|-10.89|-958.0|
|momentum_long|75|35|48|validation|84|0.405|1.3693150684931719|8.02|674.0|
|momentum_long|100|50|72|oos|135|0.370|0.8481123193200755|-5.31|-710.5|
|momentum_long|100|50|72|validation|145|0.369|1.085842434294049|2.08|218.6|
|momentum_long|150|75|120|oos|141|0.369|0.9083023087089317|-4.42|-614.8|
|momentum_long|150|75|120|validation|165|0.376|1.1511808524474494|7.00|1153.3|
|trend_breakout_long|75|35|48|oos|85|0.383|1.0836049971749673|1.05|40.1|
|trend_breakout_long|75|35|48|validation|79|0.332|0.9514592019059112|-1.43|-131.2|
|trend_breakout_long|100|50|72|oos|136|0.356|0.8909030238864742|-4.51|-643.4|
|trend_breakout_long|100|50|72|validation|153|0.295|0.76474162426781|-8.53|-1311.8|
|trend_breakout_long|150|75|120|oos|90|0.313|0.8173951883864728|-9.62|-865.2|
|trend_breakout_long|150|75|120|validation|89|0.289|0.7940266121963351|-11.50|-942.2|
|trend_breakout_short|150|75|120|oos|19|0.263|0.6932773109243697|-17.29|-328.5|
|trend_breakout_short|150|75|120|validation|35|0.486|1.8333333333333333|32.79|1147.5|
