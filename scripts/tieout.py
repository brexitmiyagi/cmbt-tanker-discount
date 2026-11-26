# fails loudly if a number quoted in the article stops reproducing
import subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
def run(s): return subprocess.run([sys.executable, os.path.join(HERE, s)], capture_output=True, text=True, check=True).stdout
checks = {
 'nav_bridge.py': ['$12.04 a share', 'net debt $4,870.3m', 'NAV $7,259.1m = $25.02 a share', '= $30.67 a share', 'price/NAV route 1 0.70',
                   '69.4% of the $3,128m tanker FMV', '-72.1%', '-69.5%', '$17.24 a share', '$21.13 a share', '$20.18 a share', 'down 20%: $12.41 a share'],
 'fcf_stress.py': ['$723m = $2.49 a share, 14.2%', '$490m = $1.69 a share, 9.6%', '$158m = $0.55 a share, 3.1%', '15.51', '1.63'],
 'q4_floor.py': ['booked uplift +$171.1m', '$635.5m = $2.19 a share', 'about $1.10 a share'],
 'tanker_sales.py': ['total 2026 tanker gains $677.7m', 'VLCCs $431.8m', 'agreed before the war $357.5m (53%)'],
 'peer_discount.py': ['price/NAV 0.76', '= 62% of the $3,128m broker value', 'route 1 $19.04, route 2 $23.35'],
 'target_bridge.py': ['ratio 58.1%', '= 41% of the $12,186m fleet', '= $+0.45 a share of NAV', 'midpoint $21.19', 'nets $0.587'],
 'tc_drag.py': ['gap $82.9m = $0.29 a share', 'gap $246.8m = $0.85 a share', 'on charter 2,271 (6.2 ships)', '$108.2m = $0.37 a share', '$34.6m a year', '$183m = $0.63 a share', '$284m = $0.98 a share', 'midpoint $20.72', 'midpoint $20.45', 'of which on time charter: 1', 'charters (3 yrs): $20.50', 'charters (8 yrs): $20.15'],
 'fleet_table.py': ['on time charter in April: 10', 'Valero: 6', 'of which on time charter: 1'],
 'fleet_valuation.py': ['108 ships $6,915m vs the company broker figure $7,017m', '-1.4%', 'together $2,807m', 'Suezmax $426m + VLCC $32m = $458m', 'Suezmax $568m + VLCC $32m = $600m', '= $28.71 a share', '= $29.20 a share', 'FSOs if my tanker curves are right: $321m', '(+44%)'],
 'model.py': ['everything else $12.7m a quarter', 'Q4 26            428.4    619.2   2.13', 'FY2026 EPS $5.95 reported', '$3.59 ex gains', 'FY2027 EPS $2.50; consensus $2.16 (+16%)', 'FY2028 EPS $1.04; consensus $1.91 (-46%)', 'net debt end-2026 $4,393m', '6.0% of gross debt', '<1y $1,154m', '= $2.35 a share; Q4 2026 distribution about $1.07'],
 'valuation.py': ['SBLK  dry bulk  market cap $3,140m, NAV $4,125m, 0.76x', 'GNK   dry bulk  market cap $1,027m, NAV $1,300m, 0.79x', 'DHT   tanker    market cap $3,438m, NAV $2,932m, 1.17x', 'INSW  tanker    market cap $5,057m, NAV $4,650m, 1.09x', 'dry bulk 0.78x, tankers 1.13x', 'SOTP route 1: $19.88 to $20.27', 'grid base (route 1 SOTP midpoint) $20.08'],
 'hormuz_paths.py': ['A. Reopens in Q1 2027                         tanker profit  -155m, values -31%, charter marks $151m (1-5 yrs ', 'B. Reopens in H2 2027                         tanker profit  -103m, values -31%, charter marks $251m (1-5 yrs ', 'C. Opens, mines and attacks keep risk high    tanker profit    +0m, values -15%, charter marks $160m (1-5 yrs ', 'D. Stays shut through 2027                    tanker profit  +349m, values +0%, charter marks $332m (1-5 yrs l'],
 'payoff.py': ['= 13.4%'],
 'holdco_discount.py': ['GNK   dry bulk  EV/fleet value 0.78', 'DHT   tanker    EV/fleet value 1.16', 'INSW  tanker    EV/fleet value 0.88', 'SBLK  dry bulk  EV/fleet value 0.78', 'GNK   dry bulk  EV/fleet value 0.83', 'DHT   tanker    EV/fleet value 1.15', 'INSW  tanker    EV/fleet value 1.08',
   'route 1, other at dry bulk multiple: peer-implied equity $2,714m ($9.35); market cap $2,800m; holdco discount -3%', 'route 2, other at dry bulk multiple: peer-implied equity $5,119m ($17.64); market cap $2,800m; holdco discount 45%',
   'route 1, other at dry bulk multiple: peer-implied equity $5,531m ($19.06); market cap $5,090m; holdco discount 8%', 'route 2, other at dry bulk multiple: peer-implied equity $7,173m ($24.72); market cap $5,090m; holdco discount 29%',
   'route 1, other at 1.0x: peer-implied equity $5,936m ($20.46); market cap $5,090m; holdco discount 14%', 'route 2, other at 1.0x: peer-implied equity $7,577m ($26.11); market cap $5,090m; holdco discount 33%',
   'charter marks $115m', 'at 0.92x vs tanker peers 1.12x (-18%)', 'at 1.89x vs tanker peers 1.12x (+69%)', '= $19.67 a share', '= $18.23 a share', '= $13.52 a share', '= $13.18 a share'],
 'payoff_both_routes.py': ['expected 12-month total return (25/50/25): +3.7% before the ex-date, +0.0% after; cost of equity 8.2% (4.91% +', 'SELL line 3.2%: with bull at 25%, the call is a SELL if the bear case is weighted above 26.4%'],
 'dry_bulk_cases.py': ['EPS 2027 $2.50, 2028 $1.04 (consensus $1.91, -46%)', 'EPS 2027 $2.50, 2028 $0.48 (consensus $1.91, -75%)', 'EPS 2027 $2.50, 2028 $-0.50 (consensus $1.91, -126%)', 'EPS 2027 $2.50, 2028 $2.57 (consensus $1.91, +35%)'],
 'holdco_series.py': ['2025-12-31 route 1: CMB.TECH extra discount 1% (band -11% to 20%)', '2025-12-31 route 2: CMB.TECH extra discount 46% (band 43% to 53%)', '2026-06-30 route 1: CMB.TECH extra discount 28% (band 22% to 34%)', '2026-06-30 route 2: CMB.TECH extra discount 42% (band 38% to 46%)', '2026-09-30 route 1: CMB.TECH extra discount 15% (band 12% to 21%)', '2026-09-30 route 2: CMB.TECH extra discount 32% (band 30% to 36%)', 'tankers implied at 0.89x (band 0.67-1.35) vs tanker peers 1.19x (-26%; band -44% to +13%)', '2026-09-30 dry bulk 0.88 (0.86-0.90)  [GNK 0.92, SBLK 0.84]', '2026-09-30 tanker   1.19 (1.18-1.24)  [DHT 1.22, INSW 1.17]', 'less the 15% average discount = $19.03', 'less the 40% average discount = $16.69', 'on $17.54 today that is $20.48', 'on $17.54 today that is $17.63', 'on $17.54 today that is $13.86', 'on $17.54 today that is $15.46'],
 'war_money_screen.py': ['CMB.TECH               $   88.8m, +32% of its Q3 profit, $0.31 a share', 'DHT Holdings           $   54.5m (days partly derived), +20% of its Q3 profit, $0.34 a share', 'Teekay Tankers         $   20.7m, +11% of its Q3 profit', 'International Seaways  $  -22.0m', 'total across the 7 owners: $312m', 'is 1.3% of that', 'Frontline              $   77.7m', 'Hafnia                 $   52.1m', 'Scorpio Tankers        $   40.6m'],
 'pair_trade.py': ['since the war +8%, since Jan 2025 -24%', 'hedge ratio 0.64', 'pair volatility 31%', '= -2.2% a year before borrow cost', '= +1.5% a year before borrow cost', 'DHT trailing four dividends $3.72'],
 'yield_check.py': ['2027 $2.74 (15.6%), 2028 $1.73 (9.9%)', 'book equity at the start of the normal year (end-2028, model): $4,167m', 'cost of equity 7.0%: price needs normal EPS $0.87 = 6.0% on end-2028 book; 41%', 'cost of equity 8.2%: price needs normal EPS $1.03 = 7.2% on end-2028 book; 35%', 'cost of equity 10.0%: price needs normal EPS $1.31 = 9.1% on end-2028 book; 29%', 'central DCF: common-window adjusted average 7.7% on end-2028 book -> $18.39', 'implied 12-month return +13.4%', 'fleet-weighted: 6.8% -> DCF $16.89; implied 12-month return +4.2%', 'DCF $21.43, implied return +32.2%'],
 'nav_covenant.py': ['fully owned by a member of the Group within pre-agreed segments', '$1,642m of ship value over book', '30% of the $5,406m total uplift', 'left out 55%', 'left out 32%', 'left out 30%'],
 'ammonia_premium.py': ['2025 rates: Newcastlemax $27,047/day', '+28% premium needed', 'through-cycle: Newcastlemax $19,319', '+80% premium needed'],
 'through_cycle.py': ['VLCC spot $37,786', 'Suezmax spot $32,777', 'Capesize 10-year about $15,212', 'VLCC charters +4,285/day against spot (above spot in 7 of 11 years)', 'Suezmax charters -2,961/day (above spot in 4 of 11 years)'],
 'roe_windows.py': ['adjusted: full span 6.7%; 8-year windows 2015-2022 3.9%, 2016-2023 4.6%, 2017-2024 5.1%', 'reported: full span 12.9%', 'common window 2015-2024, adjusted: Euronav 6.7%, Star Bulk 9.7%, Golden Ocean 6.8%', 'common window 2015-2024, reported: Euronav 12.9%, Star Bulk 7.5%, Golden Ocean 6.2%', 'all 8-year windows, adjusted: 17 windows, range -4.3% to 13.0%, median 5.0%', 'routine gains kept, Frontline break-up sale and impairments out: Euronav 9.5%, Star Bulk 9.9%, Golden Ocean 7.2%', 'routine gains kept: 17 windows, range -5.0% to 13.5%, median 6.4%', 'all 8-year windows, reported: 17 windows, range -18.8% to 13.4%, median 5.5%'],
 'hormuz_multiple.py': ['CMBT: correlation of log price with reopening odds, weekly since March: -0.83', 'DHT: correlation of log price with reopening odds, weekly since March: -0.84', 'odds 88% on 2026-03-20 -> 2% on 2026-11-24; CMBT $12.22 -> $17.54'],
 'excel_check.py': ['weighted value: Excel 18.2103, Python 18.2103, match', 'FY2027 EPS: Excel 2.4993, Python 2.4993, match'],
 'structure_and_green.py': ['CMB NV: 61.6% of shares outside treasury', 'US register: 30.4%', 'short interest 2.9% of free float, 2.9 days', '= $23,056/day; plus opex = $30,095/day', '20% ammonia premium on cost: $34,706/day'],
 'nav_reconcile.py': ['route 1 $15.78, route 2 $24.07, gap $8.29', 'route 1 $20.88, route 2 $25.61, gap $4.72', 'route 1 $25.02, route 2 $30.67, gap $5.66', 'route 2 0.40x', 'route 2 0.55x', 'route 2 0.62x'],
 'who_it_trades_with.py': ['CMBT +18.4%', 'FRO +25.2%', 'CMBT -14.9%', 'FRO -15.3%'],
 'rating.py': ['probability-weighted 12-month price $15.85, total return +3.7%', 'v16 published: normal-year return 6.14%', 'target $15.36 -> $15.40 (rounded up), expected +1.2% vs SELL line 3.2%', 'more than 14.0% (bull 25%)', 'at cost of equity 7.50%: expected +3.6% vs SELL line 2.5%', 'at cost of equity 8.43%: expected -0.0% vs SELL line 3.4%'],
 'vessel_sales.py': ['all 58 ships: gains $1,594m', 'total $291.0m of gains on sales agreed June to October 2026', '$2,347m (Euronav announced $2.35bn), gains $696m, 44%', 'sold $651m, worth about $1,223m', '2023: 13 ships, sold $1,207m against book $834m, gain $372m (45% over book)', '2026H1: 11 ships, sold $793m against book $398m, gain $395m (99% over book)'],
 'hormuz_sensitivity.py': ['daily  CMBT: a 10-point rise in reopening odds -> -0.42% (t -0.8), correlation of changes -0.06', 'on 5 of 10 days', 'levels, weekly, CMBT: correlation -0.83', 'levels, weekly, FRO: correlation -0.88', 'daily  SBLK: a 10-point rise in reopening odds -> -0.71% (t -1.7), correlation of changes -0.13'],
 'beta_check.py': ['whole 18 months  daily : CMBT 0.52', 'whole 18 months  weekly: CMBT 0.89', 'before the war   weekly: CMBT 0.55, DHT -0.52, FRO -1.00, SBLK 1.28'],
 'covenant_timeline.py': ['bridge drawn: 31 Dec 2025 $122.5m, 30 Jun 2026 $0.0m', 'SOFR + 2.10% - 2.75%', 'SOFR + 1.50% - 2.00%'],
 'gain_decomposition.py': ['10-year/5-year value ratio 0.755: 50 tankers, gains $1,533m = depreciation $-86m (-6%) + price $1,619m (106%)', 'ratio 0.69: 50 tankers, gains $1,533m = depreciation $-364m (-24%) + price $1,897m (124%)', 'ratio 0.8: 50 tankers, gains $1,533m = depreciation $130m (8%) + price $1,403m (92%)', 'Frontline block  24 ships: gains $   696m, depreciation $   -93m, price $  +789m', 'implied sale about $108m each', 'implied sale about $116m each'],
 'spike_history.py': ['INSW: 2019-12-31 0.85', '2020-09-30 0.38', 'Euronav: 2019-12-31 1.17, 2020-12-31 0.70', 'DHT: 2019-12-31 1.30, 2020-12-31 0.81', 'a fall of -35%', '38% to 56%'],
 'newbuild_share.py': ['dry bulk: 38 of 112 ships built 2023-2026', 'plus $843m of capex', 'costs $132m today'],
 'war_money_v2.py': ['old CMB.TECH figure: $88.8m', 'average $103,813', 'spot days 780, profit-split ship-days 399: A (peer benchmark) profit share $34.9m, CMB.TECH total $21.8m; B (50/50 split) profit share $18.4m, own pure spot $125,004, total $53.5m', 'range across methods and day counts: $16m to $81m'],
 'ammonia_fuel.py': ['VLSFO 31 t/day = $24,697/day; ammonia (grey, NW Europe Sep 2026 $700/t) 62 t/day + pilot = $45,473/day, $+20,776/day more', '$+28,233/day more', '$+35,068/day more'],
 'forward_gains.py': ['0.31 points of ROE per point of yearly drift', 'drift +3.7%/yr -> normal-year return 7.9% -> expected 12-month total return +9.4%', 'drift +0.0%/yr -> normal-year return 6.8% -> expected 12-month total return +4.0%', 'drift -2.0%/yr -> normal-year return 6.1%', 'drift -7.6%/yr -> normal-year return 4.4%'],
}
checks['gain_decomposition.py'].append('price part 82% to 126% of the gains')
checks['rating.py'] += ["at Kalshi's 33% bear weight (bull 25%): expected -0.6%", 'DCF $15.93 today, $14.88 in 12 months', 'at cost of equity 9.40%: expected -3.0% vs SELL line 4.4%']
bad = []
for s, needles in checks.items():
    out = run(s)
    with open(os.path.join(HERE, '..', 'results', s.replace('.py', '.txt')), 'w') as f: f.write(out)
    bad += [f'{s}: {n}' for n in needles if n not in out]
if bad:
    print('TIEOUT FAILED'); print('\n'.join(bad)); sys.exit(1)
print('tieout ok')
checks2 = {
 'earnings_implied_value.py': ['VLCC     5-year-old $215m; earnings-implied $206m', 'Suezmax  5-year-old $139m; earnings-implied $138m', 'Capesize 5-year-old $78m; earnings-implied $40m', 'VLCC: first two years $117m', 'Suezmax: first two years $67m',
                               'needs $27,273 a day from year 3 on, against $15,212', 'twenty years: -2.3% a year; over ten: -4.5%'],
 'orderbook.py': ['VLCC 33.1%, Suezmax 29.3%, Capesize 19.1%', '+40% before scrapping', 'Q1 2028 alone: 89', '$162.5m (2008 peak) to $97.0m (Jan 2015), -40%, -7.6% a year', 'average $65.3m'],
 'sector_screen.py': ['Euronav      2021-2024: gains $1,119m = 70% of profit', 'Frontline fleet sale: 27% of profit', 'INSW         2021-2025: gains $154m = 10% of profit', 'Golden Ocean 2021-2024: gains $75m = 6% of profit', 'Star Bulk    2021-2025: gains $54m = 3% of profit',
                      '-18.1% of equity a year', '-5.1% of equity a year', '-5.4% of equity a year', '-8.0% of equity a year', '+1.8% of equity a year', 'predicts -2.4 points', 'CMBT  fleet $10,145m, NAV $8,900m: NAV -11%'],
 'short_checks.py': ['2026-11-13: 2.53m shares short, about 2.3% of free float, 2.76 days', '3.21m shares short'],
 'rating.py': ['bull $18.58, base $17.10, bear $10.25 -> $15.21; DCF in 12 months $14.88', 'target $15.04 -> $15.05 (rounded up), expected -0.8% vs SELL line 3.2%', 'drift flat                   weights 25/42/33: expected +2.4%',
               'drift +3.7% (2016-23)        weights 25/42/33: expected +8.2%', 'v17 at cost of equity 7.50%: expected +1.8% vs SELL line 2.5%', 'v17 at cost of equity 9.40%: expected -4.8% vs SELL line 4.4%', 'any drift below +0.50% a year', 'more than 12.5%', 'weights 25/50/25: expected +0.7%'],
}
bad2 = []
for s, needles in checks2.items():
    out = run(s)
    bad2 += [f'{s}: {n}' for n in needles if n not in out]
if bad2:
    print('TIEOUT FAILED (v17 checks)'); print('\n'.join(bad2)); sys.exit(1)
print('tieout v17 ok')
checks3 = {
 'replacement_cost.py': ['VLCC     newbuild $132.0m needs $42,033 a day', 'Suezmax  newbuild $90.0m needs $31,969 a day', 'Capesize newbuild $75.2m needs $25,799 a day', 'at 7%: Capesize newbuild needs $24,210', 'at 9%: Capesize newbuild needs $27,418', '$46.0m (2016) needs $18,384', '$61.0m (2023) needs $22,193'],
 'backtest_eiv.py': ['2016-02 Capesize 5-year-old $23.0m, earnings value $27m (+18%)', '2023-02 VLCC     5-year-old $100.5m, earnings value $111m (+11%)', '2023-02 Suezmax  5-year-old $68.5m, earnings value $93m (+36%)', '2023-02 Capesize 5-year-old $44.5m, earnings value $32m (-29%)', '(+16.1% a year)', '(+9.9% a year)', 'direction right in 3 of 4 tests'],
 'earnings_nav.py': ['(H) through-cycle rates: tankers on earnings 95% of broker value, dry bulk 56%; fleet $-3,216m; NAV route 2 $19.59 (price/NAV 0.90), route 1 $13.94 (1.26)', '(R) replacement-cost rates: tankers on earnings 96% of broker value, dry bulk 100%; fleet $-96m; NAV route 2 $30.34 (price/NAV 0.58)', '130 ships marked'],
 'supply_net.py': ['+40%; fleet about 870 ships, about 345', 'net growth +39%', 'net growth +25%', 'net growth +19%', 'shadow/sanctioned VLCCs about 23%', 'grows +51%', 'rises another +15%'],
 'frontline_side.py': ['paid $2,347m, worth about $4,704m now (ages 3-11), +100%, $2,357m', 'booked $696m of gains'],
}
bad3 = []
for s, needles in checks3.items():
    out = run(s)
    bad3 += [f'{s}: {n}' for n in needles if n not in out]
if bad3:
    print('TIEOUT FAILED (v18 checks)'); print('\n'.join(bad3)); sys.exit(1)
print('tieout v18 ok')
