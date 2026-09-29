# H1 Research Results

- candidate rows: 1440
- discovery-eligible rows: 30
- follow-up rows: 60

Protocol: signal at confirmed candle close; entry at next H1 open; non-overlapping trades; same-candle TP/SL => conservative SL; chronological 60/20/20 splits with no trade crossing split boundaries.
Selection rule: discovery only; minimum 30 trades, PF >= 1.10 and positive expectancy. Validation/OOS are not used to select rules.

## Validation/OOS follow-up

|Rule|TP|SL|H|Split|Trades|Win rate|PF|Expectancy pips|Total pips|
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
|h4_aligned_long|100|50|72|oos|189|0.412|1.0646592527903707|1.78|344.7|
|h4_aligned_long|100|50|72|validation|225|0.347|0.9764352951794604|-0.80|-201.2|
|h4_aligned_long|150|75|120|oos|203|0.381|0.9610815908473976|-2.42|-668.1|
|h4_aligned_long|150|75|120|validation|232|0.344|0.9909709285708201|-0.43|-27.6|
|meanrev_long|100|50|72|oos|13|0.154|0.2647837599293912|-32.04|-416.5|
|meanrev_long|100|50|72|validation|30|0.233|0.5821021528070917|-16.50|-495.0|
|meanrev_long|150|75|120|oos|25|0.200|0.32996418623159063|-33.68|-841.9|
|meanrev_long|150|75|120|validation|15|0.533|1.71042727473986|21.39|320.9|
|meanrev_short|75|35|48|oos|26|0.231|0.44596834966088506|-14.14|-367.6|
|meanrev_short|75|35|48|validation|37|0.324|0.6230335759567865|-8.68|-321.1|
|meanrev_short|100|50|72|oos|51|0.395|0.95032128359764|-6.81|-361.9|
|meanrev_short|100|50|72|validation|62|0.456|1.2533817316316664|4.05|206.1|
|meanrev_short|150|75|120|oos|87|0.376|0.7514300564897809|-14.01|-1151.9|
|meanrev_short|150|75|120|validation|101|0.478|1.2463263277767769|4.22|447.1|
|momentum_long|75|35|48|oos|88|0.273|0.5852095600969938|-10.89|-958.0|
|momentum_long|75|35|48|validation|84|0.405|1.3693150684931719|8.02|674.0|
|momentum_long|100|50|72|oos|135|0.370|0.8481123193200755|-5.31|-710.5|
|momentum_long|100|50|72|validation|144|0.372|1.1036882380476094|2.55|270.1|
|momentum_long|150|75|120|oos|141|0.369|0.9083023087089317|-4.42|-614.8|
|momentum_long|150|75|120|validation|165|0.386|1.2105916431109451|9.52|1659.4|
|trend_breakout_long|75|35|48|oos|85|0.383|1.0836049971749673|1.05|40.1|
|trend_breakout_long|75|35|48|validation|79|0.332|0.9514592019059112|-1.43|-131.2|
|trend_breakout_long|100|50|72|oos|135|0.358|0.8977843556710254|-4.23|-591.9|
|trend_breakout_long|100|50|72|validation|151|0.305|0.8045996462567325|-7.03|-1058.8|
|trend_breakout_long|150|75|120|oos|90|0.313|0.8173951883864728|-9.62|-865.2|
|trend_breakout_long|150|75|120|validation|90|0.314|0.8935466948964509|-7.12|-467.1|
|trend_breakout_short|150|75|120|oos|19|0.263|0.6932773109243697|-17.29|-328.5|
|trend_breakout_short|150|75|120|validation|35|0.486|1.8333333333333333|32.79|1147.5|
