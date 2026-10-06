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
|h4_aligned_long|100|50|72|validation|229|0.350|0.9996036014168024|-0.03|-34.7|
|h4_aligned_long|150|75|120|oos|143|0.385|0.9705924260307554|-2.03|-420.8|
|h4_aligned_long|150|75|120|validation|165|0.341|0.9910369983176242|-0.46|-91.4|
|meanrev_long|100|50|72|oos|34|0.267|0.7211424562671338|-15.10|-378.0|
|meanrev_long|100|50|72|validation|44|0.402|0.8203661448966968|-7.87|-484.3|
|meanrev_long|150|75|120|oos|24|0.208|0.35135593220338446|-31.89|-765.4|
|meanrev_long|150|75|120|validation|15|0.533|1.5931785494144126|19.25|288.7|
|meanrev_short|75|35|48|oos|25|0.240|0.47192982456139915|-13.24|-331.1|
|meanrev_short|75|35|48|validation|38|0.289|0.49426903114185855|-12.31|-467.7|
|meanrev_short|100|50|72|oos|50|0.420|1.0810353709388911|-4.89|-244.3|
|meanrev_short|100|50|72|validation|63|0.436|1.1669973112816|1.22|4.5|
|meanrev_short|150|75|120|oos|83|0.381|0.6988138268338465|-15.11|-1181.2|
|meanrev_short|150|75|120|validation|99|0.444|1.122683513192448|-0.99|-62.0|
|momentum_long|75|35|48|oos|88|0.273|0.5852095600969938|-10.89|-958.0|
|momentum_long|75|35|48|validation|84|0.405|1.3693150684931719|8.02|674.0|
|momentum_long|100|50|72|oos|133|0.369|0.8368958612433945|-5.65|-757.5|
|momentum_long|100|50|72|validation|147|0.365|1.0836978523692877|1.97|190.3|
|momentum_long|150|75|120|oos|140|0.372|0.923762553470583|-3.76|-538.3|
|momentum_long|150|75|120|validation|167|0.378|1.159001576882944|7.26|1200.7|
|trend_breakout_long|75|35|48|oos|84|0.376|1.0732331772141055|0.94|24.2|
|trend_breakout_long|75|35|48|validation|81|0.348|0.9695056581298551|-1.10|-100.9|
|trend_breakout_long|100|50|72|oos|134|0.346|0.861770592878907|-5.49|-755.2|
|trend_breakout_long|100|50|72|validation|154|0.319|0.835662456968106|-5.80|-896.3|
|trend_breakout_long|150|75|120|oos|89|0.317|0.8353583649424982|-8.73|-788.7|
|trend_breakout_long|150|75|120|validation|92|0.312|0.8937519431393892|-6.24|-496.7|
|trend_breakout_short|150|75|120|oos|19|0.263|0.6932773109243697|-17.29|-328.5|
|trend_breakout_short|150|75|120|validation|35|0.486|1.8333333333333333|32.79|1147.5|
