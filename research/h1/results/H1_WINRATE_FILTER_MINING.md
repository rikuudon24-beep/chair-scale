# H1 win-rate filter mining

Historical optimization of the existing frozen H1 candidates. Base rules are not replaced automatically.
3-pip cost per trade. Minimum 15 trades; candidates require PF>1 and positive expectancy.

## USDJPY
Base: N=172, Win=0.494, PF=0.843, ExpR=-3.392
- PAIR: bb_pct<=0.5 + utc_00_06 | N=15 Win=0.733 (+0.239) PF=2.366 ExpR=15.667 Net=235.0
- SINGLE: utc_00_06 | N=53 Win=0.642 (+0.147) PF=1.540 ExpR=8.321 Net=441.0
- SINGLE: bb_pct<=0.5 | N=79 Win=0.544 (+0.050) PF=1.037 ExpR=0.704 Net=55.6
- SINGLE: rsi<=45 | N=56 Win=0.536 (+0.042) PF=1.004 ExpR=0.082 Net=4.6

## EURJPY
Base: N=260, Win=0.373, PF=1.235, ExpR=6.262
- PAIR: rsi<=40 + macd_hist>=0 | N=21 Win=0.571 (+0.198) PF=2.975 ExpR=33.195 Net=697.1
- PAIR: rsi>=45 + bb_pct<=0.4 | N=38 Win=0.526 (+0.153) PF=2.275 ExpR=25.963 Net=986.6
- PAIR: rsi<=45 + atr_pct>=0.002 | N=46 Win=0.522 (+0.149) PF=2.382 ExpR=28.428 Net=1307.7
- PAIR: dist_ema20<=0 + body_range>=0.6 | N=103 Win=0.515 (+0.141) PF=2.173 ExpR=23.668 Net=2437.8
- PAIR: atr_pct>=0.002 + utc_18_24 | N=35 Win=0.514 (+0.141) PF=2.347 ExpR=28.131 Net=984.6
- PAIR: rsi<=45 + body_range>=0.6 | N=69 Win=0.507 (+0.134) PF=2.094 ExpR=22.057 Net=1521.9
- PAIR: bb_pct<=0.4 + body_range>=0.6 | N=83 Win=0.506 (+0.133) PF=2.079 ExpR=21.990 Net=1825.2
- PAIR: bb_pct<=0.5 + body_range>=0.6 | N=107 Win=0.505 (+0.132) PF=2.106 ExpR=22.645 Net=2423.0
- PAIR: rsi<=40 + lower_wick>=body | N=40 Win=0.500 (+0.127) PF=2.087 ExpR=22.368 Net=894.7
- PAIR: bb_pct<=0.4 + body_range>=0.4 | N=106 Win=0.491 (+0.117) PF=1.932 ExpR=19.449 Net=2061.6

## GBPJPY
Base: N=192, Win=0.510, PF=0.733, ExpR=-6.778
- SINGLE: ema20_slope>=0 | N=95 Win=0.632 (+0.121) PF=1.253 ExpR=4.714 Net=447.8
- SINGLE: ema20_slope>=0.001 | N=30 Win=0.600 (+0.090) PF=1.047 ExpR=1.000 Net=30.0
- PAIR: ema20_slope>=0 + ema20_slope>=0.001 | N=30 Win=0.600 (+0.090) PF=1.047 ExpR=1.000 Net=30.0

## USDCHF
Base: N=246, Win=0.561, PF=1.164, ExpR=2.705
- PAIR: adx>=25 + rsi>=50 | N=62 Win=0.726 (+0.165) PF=2.807 ExpR=15.324 Net=950.1
- PAIR: adx>=25 + ema20_slope>=0 | N=51 Win=0.725 (+0.165) PF=2.391 ExpR=13.073 Net=666.7
- PAIR: adx>=25 + close_above_ema20 | N=77 Win=0.688 (+0.127) PF=2.173 ExpR=12.322 Net=948.8
- PAIR: rsi>=50 + bb_pct<=0.5 | N=21 Win=0.667 (+0.106) PF=2.016 ExpR=11.724 Net=246.2
- PAIR: adx>=25 + rsi>=45 | N=81 Win=0.667 (+0.106) PF=1.925 ExpR=10.644 Net=862.2
- PAIR: adx>=25 + utc_00_06 | N=53 Win=0.660 (+0.099) PF=1.877 ExpR=10.647 Net=564.3
- PAIR: bb_pct<=0.4 + utc_00_06 | N=29 Win=0.655 (+0.094) PF=1.771 ExpR=9.414 Net=273.0
- PAIR: adx>=25 + dist_ema20>=-0.5 | N=86 Win=0.640 (+0.079) PF=1.670 ExpR=8.351 Net=718.2
- PAIR: adx>=25 + macd_hist>=0 | N=93 Win=0.634 (+0.073) PF=1.625 ExpR=8.171 Net=759.9
- PAIR: adx>=30 + rsi>=50 | N=30 Win=0.633 (+0.072) PF=1.734 ExpR=8.560 Net=256.8

## AUDNZD
Base: N=147, Win=0.571, PF=1.188, ExpR=3.982
- PAIR: adx>=20 + ema50_slope>=0 | N=40 Win=0.725 (+0.154) PF=1.881 ExpR=13.763 Net=550.5
- PAIR: adx>=25 + ema50_slope>=0 | N=24 Win=0.708 (+0.137) PF=1.621 ExpR=10.267 Net=246.4
- PAIR: adx>=20 + ema20_slope>=0.001 | N=16 Win=0.688 (+0.116) PF=1.649 ExpR=13.737 Net=219.8
- PAIR: adx>=25 + utc_06_12 | N=35 Win=0.686 (+0.114) PF=1.520 ExpR=8.637 Net=302.3
- SINGLE: ema20_slope>=0.001 | N=19 Win=0.684 (+0.113) PF=1.571 ExpR=12.526 Net=238.0
- PAIR: rsi>=45 + ema20_slope>=0.001 | N=19 Win=0.684 (+0.113) PF=1.571 ExpR=12.526 Net=238.0
- PAIR: rsi>=50 + ema20_slope>=0.001 | N=19 Win=0.684 (+0.113) PF=1.571 ExpR=12.526 Net=238.0
- PAIR: rsi_change6>=2 + ema20_slope>=0.001 | N=19 Win=0.684 (+0.113) PF=1.571 ExpR=12.526 Net=238.0
- PAIR: atr_pct<=0.006 + ema20_slope>=0.001 | N=19 Win=0.684 (+0.113) PF=1.571 ExpR=12.526 Net=238.0
- PAIR: ema20_slope>=0 + ema20_slope>=0.001 | N=19 Win=0.684 (+0.113) PF=1.571 ExpR=12.526 Net=238.0
