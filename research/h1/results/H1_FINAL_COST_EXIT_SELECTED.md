# H1 final cost/exit refinement

Assumption: 3-pip round-trip cost per trade; TIME exits settle at the horizon-bar close. Validation selects entry/TP/SL/horizon; OOS is evaluated after freezing the rule. Because the six pairs were previously routed using OOS evidence, this is not a pristine untouched holdout.

|Pair|Entry|TP|SL|H|Val n|Val PF|Val ExpR|OOS n|OOS Win|OOS PF|OOS ExpR|OOS NetR|TP/SL/TIME|
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
|usdjpy|confirm_1bar|125|40|48|29|1.081|0.063|25|0.440|1.244|0.141|3.53|2/13/10|
|eurjpy|next_open|100|40|72|27|1.805|0.481|29|0.448|1.763|0.425|12.31|11/15/3|
|gbpjpy|break_signal_high|40|75|24|36|1.965|0.195|34|0.559|0.715|-0.101|-3.45|17/11/6|
|usdchf|confirm_1bar|75|40|48|32|1.808|0.294|30|0.533|1.532|0.181|5.44|4/8/18|
|audusd|confirm_1bar|75|40|72|31|1.087|0.048|22|0.409|0.968|-0.017|-0.36|4/9/9|
|audnzd|next_open|75|75|72|29|1.328|0.067|20|0.750|2.865|0.339|6.78|7/3/10|
