# H1 mined filter chronological validation

Fixed shortlist from historical mining. Exact final entry/exit mechanics. Costs tested at 3p and 5p.

## {pair}
- BASE @ 3p: D: N=66 Win=0.515 PF=0.923 ExpR=-1.564 NetR=-103.20 | V: N=28 Win=0.536 PF=0.993 ExpR=-0.143 NetR=-4.00 | O: N=24 Win=0.583 PF=1.205 ExpR=3.667 NetR=88.00
- BASE @ 5p: D: N=66 Win=0.515 PF=0.833 ExpR=-3.564 NetR=-235.20 | V: N=28 Win=0.536 PF=0.897 ExpR=-2.143 NetR=-60.00 | O: N=24 Win=0.583 PF=1.089 ExpR=1.667 NetR=40.00
- bb_pct<=0.5 + utc_00_06 @ 3p: D: N=12 Win=0.750 PF=2.581 ExpR=17.000 NetR=204.00 | V: N=5 Win=0.800 PF=3.442 ExpR=21.000 NetR=105.00 | O: N=2 Win=1.000 PF=inf ExpR=37.000 NetR=74.00
- bb_pct<=0.5 + utc_00_06 @ 5p: D: N=12 Win=0.750 PF=2.333 ExpR=15.000 NetR=180.00 | V: N=5 Win=0.800 PF=3.111 ExpR=19.000 NetR=95.00 | O: N=2 Win=1.000 PF=inf ExpR=35.000 NetR=70.00

## {pair}
- BASE @ 3p: D: N=82 Win=0.341 PF=1.014 ExpR=0.401 NetR=32.90 | V: N=27 Win=0.444 PF=1.805 ExpR=19.222 NetR=519.00 | O: N=29 Win=0.448 PF=1.763 ExpR=16.983 NetR=492.50
- BASE @ 5p: D: N=82 Win=0.341 PF=0.945 ExpR=-1.599 NetR=-131.10 | V: N=27 Win=0.444 PF=1.689 ExpR=17.222 NetR=465.00 | O: N=29 Win=0.448 PF=1.642 ExpR=14.983 NetR=434.50
- dist_ema20<=0 + body_range>=0.6 @ 3p: D: N=48 Win=0.521 PF=1.990 ExpR=19.700 NetR=945.60 | V: N=17 Win=0.471 PF=2.217 ExpR=25.053 NetR=425.90 | O: N=14 Win=0.571 PF=2.739 ExpR=32.050 NetR=448.70
- dist_ema20<=0 + body_range>=0.6 @ 5p: D: N=48 Win=0.500 PF=1.847 ExpR=17.700 NetR=849.60 | V: N=17 Win=0.471 PF=2.065 ExpR=23.053 NetR=391.90 | O: N=14 Win=0.571 PF=2.558 ExpR=30.050 NetR=420.70
- rsi<=45 + body_range>=0.6 @ 3p: D: N=31 Win=0.452 PF=1.400 ExpR=8.990 NetR=278.70 | V: N=11 Win=0.545 PF=3.268 ExpR=36.718 NetR=403.90 | O: N=13 Win=0.538 PF=2.363 ExpR=27.054 NetR=351.70
- rsi<=45 + body_range>=0.6 @ 5p: D: N=31 Win=0.419 PF=1.296 ExpR=6.990 NetR=216.70 | V: N=11 Win=0.545 PF=3.030 ExpR=34.718 NetR=381.90 | O: N=13 Win=0.538 PF=2.206 ExpR=25.054 NetR=325.70
- bb_pct<=0.5 + body_range>=0.6 @ 3p: D: N=49 Win=0.490 PF=1.678 ExpR=14.869 NetR=728.60 | V: N=18 Win=0.500 PF=2.494 ExpR=29.050 NetR=522.90 | O: N=14 Win=0.500 PF=2.026 ExpR=22.050 NetR=308.70
- bb_pct<=0.5 + body_range>=0.6 @ 5p: D: N=49 Win=0.469 PF=1.560 ExpR=12.869 NetR=630.60 | V: N=18 Win=0.500 PF=2.323 ExpR=27.050 NetR=486.90 | O: N=14 Win=0.500 PF=1.891 ExpR=20.050 NetR=280.70

## {pair}
- BASE @ 3p: D: N=94 Win=0.564 PF=0.917 ExpR=-1.843 NetR=-173.20 | V: N=36 Win=0.806 PF=2.892 ExpR=19.500 NetR=702.00 | O: N=34 Win=0.529 PF=0.848 ExpR=-3.335 NetR=-113.40
- BASE @ 5p: D: N=94 Win=0.564 PF=0.833 ExpR=-3.843 NetR=-361.20 | V: N=36 Win=0.806 PF=2.636 ExpR=17.500 NetR=630.00 | O: N=34 Win=0.529 PF=0.767 ExpR=-5.335 NetR=-181.40
- ema20_slope>=0 @ 3p: D: N=66 Win=0.621 PF=1.212 ExpR=3.973 NetR=262.20 | V: N=26 Win=0.692 PF=1.571 ExpR=9.308 NetR=242.00 | O: N=18 Win=0.556 PF=1.126 ExpR=2.300 NetR=41.40
- ema20_slope>=0 @ 5p: D: N=66 Win=0.621 PF=1.101 ExpR=1.973 NetR=130.20 | V: N=26 Win=0.692 PF=1.432 ExpR=7.308 NetR=190.00 | O: N=18 Win=0.556 PF=1.016 ExpR=0.300 NetR=5.40

## {pair}
- BASE @ 3p: D: N=85 Win=0.576 PF=1.292 ExpR=4.364 NetR=370.90 | V: N=32 Win=0.625 PF=1.694 ExpR=9.022 NetR=288.70 | O: N=30 Win=0.567 PF=1.444 ExpR=5.420 NetR=162.60
- BASE @ 5p: D: N=85 Win=0.565 PF=1.150 ExpR=2.364 NetR=200.90 | V: N=32 Win=0.594 PF=1.510 ExpR=7.022 NetR=224.70 | O: N=30 Win=0.567 PF=1.261 ExpR=3.420 NetR=102.60
- adx>=25 + rsi>=50 @ 3p: D: N=19 Win=0.632 PF=1.332 ExpR=4.863 NetR=92.40 | V: N=9 Win=0.556 PF=0.981 ExpR=-0.289 NetR=-2.60 | O: N=10 Win=0.600 PF=1.459 ExpR=5.100 NetR=51.00
- adx>=25 + rsi>=50 @ 5p: D: N=19 Win=0.632 PF=1.186 ExpR=2.863 NetR=54.40 | V: N=9 Win=0.556 PF=0.855 ExpR=-2.289 NetR=-20.60 | O: N=10 Win=0.600 PF=1.260 ExpR=3.100 NetR=31.00
- adx>=25 + ema20_slope>=0 @ 3p: D: N=14 Win=0.714 PF=1.517 ExpR=6.350 NetR=88.90 | V: N=8 Win=0.625 PF=1.442 ExpR=5.050 NetR=40.40 | O: N=10 Win=0.600 PF=1.427 ExpR=5.550 NetR=55.50
- adx>=25 + ema20_slope>=0 @ 5p: D: N=14 Win=0.714 PF=1.338 ExpR=4.350 NetR=60.90 | V: N=8 Win=0.625 PF=1.251 ExpR=3.050 NetR=24.40 | O: N=10 Win=0.600 PF=1.257 ExpR=3.550 NetR=35.50

## {pair}
- BASE @ 3p: D: N=94 Win=0.521 PF=0.914 ExpR=-2.155 NetR=-202.60 | V: N=29 Win=0.552 PF=1.362 ExpR=5.514 NetR=159.90 | O: N=20 Win=0.800 PF=3.067 ExpR=27.290 NetR=545.80
- BASE @ 5p: D: N=94 Win=0.511 PF=0.841 ExpR=-4.155 NetR=-390.60 | V: N=29 Win=0.483 PF=1.217 ExpR=3.514 NetR=101.90 | O: N=20 Win=0.800 PF=2.860 ExpR=25.290 NetR=505.80
- adx>=20 + ema50_slope>=0 @ 3p: D: N=25 Win=0.760 PF=1.799 ExpR=11.860 NetR=296.50 | V: N=6 Win=0.500 PF=0.959 ExpR=-0.767 NetR=-4.60 | O: N=8 Win=0.875 PF=5.115 ExpR=40.125 NetR=321.00
- adx>=20 + ema50_slope>=0 @ 5p: D: N=25 Win=0.720 PF=1.641 ExpR=9.860 NetR=246.50 | V: N=6 Win=0.500 PF=0.861 ExpR=-2.767 NetR=-16.60 | O: N=8 Win=0.875 PF=4.812 ExpR=38.125 NetR=305.00
- adx>=25 + ema50_slope>=0 @ 3p: D: N=14 Win=0.786 PF=2.012 ExpR=11.550 NetR=161.70 | V: N=3 Win=0.333 PF=0.380 ExpR=-19.967 NetR=-59.90 | O: N=6 Win=0.833 PF=3.654 ExpR=34.500 NetR=207.00
- adx>=25 + ema50_slope>=0 @ 5p: D: N=14 Win=0.714 PF=1.799 ExpR=9.550 NetR=133.70 | V: N=3 Win=0.333 PF=0.345 ExpR=-21.967 NetR=-65.90 | O: N=6 Win=0.833 PF=3.438 ExpR=32.500 NetR=195.00
