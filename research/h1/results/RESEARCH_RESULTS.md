# H1 Research Results

- candidate rows: 1440
- discovery-eligible rows: 30
- follow-up rows: 60

Protocol: signal at confirmed candle close; entry at next H1 open; non-overlapping trades; same-candle TP/SL => conservative SL; chronological 60/20/20 splits with no trade crossing split boundaries.
Selection rule: discovery only; minimum 30 trades, PF >= 1.10 and positive expectancy. Validation/OOS are not used to select rules.

## Validation/OOS follow-up

|Rule|TP|SL|H|Split|Trades|Win rate|PF|Expectancy pips|Total pips|
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
|h4_aligned_long|100|50|72|oos|188|0.409|1.0295770085007283|0.74|158.3|
|h4_aligned_long|100|50|72|validation|230|0.349|0.9919339968411655|-0.28|-86.2|
|h4_aligned_long|150|75|120|oos|144|0.384|0.9728826813038577|-2.18|-497.3|
|h4_aligned_long|150|75|120|validation|164|0.342|0.9988769906121027|-0.06|-14.9|
|meanrev_long|100|50|72|oos|34|0.267|0.7211424562671338|-15.10|-378.0|
|meanrev_long|100|50|72|validation|44|0.402|0.8203661448966968|-7.87|-484.3|
|meanrev_long|150|75|120|oos|24|0.208|0.35135593220338446|-31.89|-765.4|
|meanrev_long|150|75|120|validation|15|0.533|1.5874255188000699|19.06|285.9|
|meanrev_short|75|35|48|oos|26|0.231|0.44596834966088506|-14.14|-367.6|
|meanrev_short|75|35|48|validation|38|0.316|0.5974332995609487|-9.41|-357.6|
|meanrev_short|100|50|72|oos|51|0.395|0.9801039067315382|-6.52|-347.4|
|meanrev_short|100|50|72|validation|62|0.456|1.2533817316316664|4.05|206.1|
|meanrev_short|150|75|120|oos|84|0.365|0.6463103746883578|-16.34|-1312.6|
|meanrev_short|150|75|120|validation|100|0.458|1.1985855938453303|2.35|305.8|
|momentum_long|75|35|48|oos|88|0.273|0.5852095600969938|-10.89|-958.0|
|momentum_long|75|35|48|validation|84|0.405|1.3693150684931719|8.02|674.0|
|momentum_long|100|50|72|oos|133|0.369|0.8368958612433945|-5.65|-757.5|
|momentum_long|100|50|72|validation|147|0.365|1.0836978523692877|1.97|190.3|
|momentum_long|150|75|120|oos|139|0.375|0.9323829765502091|-3.29|-461.8|
|momentum_long|150|75|120|validation|166|0.380|1.1613992364959187|7.39|1221.1|
|trend_breakout_long|75|35|48|oos|85|0.383|1.0836049971749673|1.05|40.1|
|trend_breakout_long|75|35|48|validation|79|0.332|0.9514592019059112|-1.43|-131.2|
|trend_breakout_long|100|50|72|oos|135|0.350|0.8657369533703781|-5.43|-741.9|
|trend_breakout_long|100|50|72|validation|154|0.306|0.8051883218621474|-6.95|-1063.3|
|trend_breakout_long|150|75|120|oos|90|0.313|0.8173951883864728|-9.62|-865.2|
|trend_breakout_long|150|75|120|validation|89|0.289|0.7940266121963351|-11.50|-942.2|
|trend_breakout_short|150|75|120|oos|19|0.263|0.6932773109243697|-17.29|-328.5|
|trend_breakout_short|150|75|120|validation|35|0.486|1.8333333333333333|32.79|1147.5|
