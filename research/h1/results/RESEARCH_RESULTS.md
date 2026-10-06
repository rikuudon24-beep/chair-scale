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
|h4_aligned_long|100|50|72|validation|226|0.346|0.9785265067489238|-0.72|-180.2|
|h4_aligned_long|150|75|120|oos|143|0.385|0.9705924260307554|-2.03|-420.8|
|h4_aligned_long|150|75|120|validation|164|0.336|0.969010239885158|-1.55|-239.9|
|meanrev_long|100|50|72|oos|34|0.267|0.7211424562671338|-15.10|-378.0|
|meanrev_long|100|50|72|validation|43|0.389|0.7787874196961901|-9.85|-582.8|
|meanrev_long|150|75|120|oos|24|0.208|0.35135593220338446|-31.89|-765.4|
|meanrev_long|150|75|120|validation|15|0.533|1.5931785494144126|19.25|288.7|
|meanrev_short|75|35|48|oos|25|0.240|0.47192982456139915|-13.24|-331.1|
|meanrev_short|75|35|48|validation|38|0.289|0.49426903114185855|-12.31|-467.7|
|meanrev_short|100|50|72|oos|50|0.420|1.0810353709388911|-4.89|-244.3|
|meanrev_short|100|50|72|validation|63|0.436|1.1669973112816|1.22|4.5|
|meanrev_short|150|75|120|oos|83|0.381|0.6988138268338465|-15.11|-1181.2|
|meanrev_short|150|75|120|validation|99|0.444|1.122683513192448|-0.99|-62.0|
|momentum_long|75|35|48|oos|89|0.270|0.576105025361245|-11.17|-994.5|
|momentum_long|75|35|48|validation|81|0.420|1.456718157971459|9.67|783.5|
|momentum_long|100|50|72|oos|134|0.366|0.829818804346949|-5.94|-809.0|
|momentum_long|100|50|72|validation|144|0.367|1.0939729903720754|2.23|194.8|
|momentum_long|150|75|120|oos|140|0.372|0.923762553470583|-3.76|-538.3|
|momentum_long|150|75|120|validation|167|0.371|1.1331642025066706|6.04|1026.0|
|trend_breakout_long|75|35|48|oos|85|0.373|1.0613779717690066|0.62|-12.3|
|trend_breakout_long|75|35|48|validation|80|0.351|0.9833932348894208|-0.72|-64.4|
|trend_breakout_long|100|50|72|oos|135|0.344|0.8554280912401737|-5.76|-806.7|
|trend_breakout_long|100|50|72|validation|153|0.321|0.843154919557656|-5.50|-844.8|
|trend_breakout_long|150|75|120|oos|90|0.314|0.8231923289374529|-9.47|-865.2|
|trend_breakout_long|150|75|120|validation|92|0.312|0.8937519431393892|-6.24|-496.7|
|trend_breakout_short|150|75|120|oos|18|0.278|0.746606334841629|-14.00|-252.0|
|trend_breakout_short|150|75|120|validation|35|0.486|1.8333333333333333|32.79|1147.5|
