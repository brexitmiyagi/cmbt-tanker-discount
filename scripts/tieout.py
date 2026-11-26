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
checks4 = {
 'backtest_capesize.py': ['23 dates with an outcome. correlation of log(price/value) with the next yearly price change: +0.01', 'correlation of price/newbuild with the next yearly price change: -0.69', 'next price change +9.8%/yr', '+10.1%/yr', 'range of price/newbuild in the sample 0.47-0.82', '2026-11-20 VLCC price/newbuild 1.67, Suezmax 1.65', 'price/newbuild 1.02'],
 'newbuild_premium.py': ['$220.0m against newbuild $132.0m = 1.67; highest earlier ratio 0.84 -> $111m, -49%', 'Suezmax  five-year-old $150.0m against newbuild $91.0m = 1.65; highest earlier ratio 0.96 -> $87m, -42%', 'Capesize five-year-old $78.3m against newbuild $76.5m = 1.02; highest earlier ratio 0.82 -> $63m, -20%', 'CMB.TECH fleet mix: -10.5% a year', 'yard cover 3.7 years'],
 'peer_earnings_nav.py': ['SBLK  (Capesize curve, age 12.7): price/NAV on broker values 0.77, on through-cycle earnings 1.13, on replacement-cost earnings 0.65', 'GNK   (Capesize curve, age 12.9): price/NAV on broker values 0.79, on through-cycle earnings 1.22, on replacement-cost earnings 0.64', 'DHT   (VLCC curve, age 11.4): price/NAV on broker values 1.19, on through-cycle earnings 1.11, on replacement-cost earnings 1.04', 'CMBT at $17.72: broker 0.58, through-cycle earnings 0.90, replacement-cost earnings 0.58'],
 'rating_v19.py': ['bear weight 32.5%', 'bull $18.59, base $17.29, bear $10.25 -> $15.33; DCF in 12 months $14.88', 'target $15.10 -> $15.15 (rounded up), expected -1.3% vs SELL line 3.2%', 'drift flat: expected +1.7%', 'drift +3.7% (2016-23): expected +7.5%', 'drift -4.5%: expected -6.4%', 'cost of equity 7.50%: expected +1.1% vs SELL line 2.5%', 'cost of equity 9.40%: expected -5.5% vs SELL line 4.4%', 'any drift below +0.95% a year', 'more than 8.9%; at 25% expected -0.0%', 'earnings NAV $19.59 (price/NAV 0.90); target + distributions discounted a year $16.18', '= -$1.09; what is left -$2.32 = 13% discount', 'price today is 0.96 times', 'SBLK 1.13, GNK 1.22, DHT 1.11'],
 'replacement_cost.py': ['Suezmax  broker newbuild $91.0m (20 Nov 2026) needs $32,223', 'Capesize broker newbuild $76.5m (20 Nov 2026) needs $26,129'],
}
bad4 = []
for s, needles in checks4.items():
    out = run(s)
    bad4 += [f'{s}: {n}' for n in needles if n not in out]
if bad4:
    print('TIEOUT FAILED (v19 checks)'); print('\n'.join(bad4)); sys.exit(1)
print('tieout v19 ok')
for s, needles in {'dry_bulk_demand.py': ['VLCC orderbook 33.1%, Suezmax 29.3%, Capesize 19.1%; VLCC fleet growth 2027-29 7.1/16.1/12.3%, Suezmax 8.7/11.9/8.5%', 'VLCCs over 20 years 19%', 'Capesizes over 15 years 44%', '795.61mt (-2.8%)', '(+3.1%)', 'about 20mt', '120mt by end-2027', '+25% tonne-miles', 'iron ore tonne-miles 2.8% 2026, 4.3% 2027 against Capesize fleet growth 2.5% and 5.7%'],
                   'frontline_side.py': ['paid $2,347m, worth about $4,704m']}.items():
    out = run(s); miss = [n for n in needles if n not in out]
    if miss: print('TIEOUT FAILED', s, miss); sys.exit(1)
print('tieout v19 extras ok')
checks5 = {
 'charter_test.py': ['VLCC      5-yr $ 220.0m vs newbuild $132.0m; on the 3-yr charter it\'s worth $ 172.9m (+27%', '$ 221.4m with year 1 at the 1-yr rate (-1%)', 'Suezmax   5-yr $ 150.0m vs newbuild $ 91.0m; on the 3-yr charter it\'s worth $ 118.9m (+26%', '$ 138.7m with year 1 at the 1-yr rate (+8%)',
                     'Capesize  5-yr $  78.3m vs newbuild $ 76.5m; on the 3-yr charter it\'s worth $  58.2m (+34%', '$  61.9m with year 1 at the 1-yr rate (+26%); the price needs $44,852/day', 'Kamsarmax', '(+50%)', '(+41%)'],
 'backtest_robust.py': ['Capesize     : 10 non-overlapping pairs, correlation -0.49, t-stat -1.6', 'tankers      : 16 non-overlapping pairs, correlation -0.12', 'all segments : 26 non-overlapping pairs, correlation -0.26', 'highest price/newbuild in these pairs 0.96'],
 'sector_exposure.py': ['GNK   fleet-weighted price/newbuild 1.05; fleet/NAV 1.22; NAV hit if ratios go to 0.85: -23%; if prices fall to what charters pay for: -29%', 'SBLK  fleet-weighted price/newbuild 1.06; fleet/NAV 1.07; NAV hit if ratios go to 0.85: -21%; if prices fall to what charters pay for: -29%', 'CMBT  fleet-weighted price/newbuild 1.23; fleet/NAV 1.14; NAV hit if ratios go to 0.85: -31%; if prices fall to what charters pay for: -19%', 'INSW  fleet-weighted price/newbuild 1.43; fleet/NAV 1.05; NAV hit if ratios go to 0.85: -40%; if prices fall to what charters pay for: -6%', 'DHT   fleet-weighted price/newbuild 1.67; fleet/NAV 1.12; NAV hit if ratios go to 0.85: -55%; if prices fall to what charters pay for: -0%'],
 'valuation_simple.py': ['cash Q4 2026-2028 $6.41 + end-2028 book at the cost of equity $12.64 = $19.05; normal year 6.1% vs cost of equity 8.2%: $-3.12', 'value today $15.93; a year at 8.2% $+1.30; distributions -$2.35; 12-month $14.88 -> target $14.90', 'expected 12-month total return at $17.72: -2.7% vs SELL line 3.2%', 'needs a normal year of 7.3%', 'drift flat: normal year 6.8%, expected +3.1%', 'drift +3.7% (2016-23): normal year 7.9%, expected +13.9%', 'drift -4.5%: normal year 5.4%, expected -10.2%', 'cost of equity 7.50%: expected +2.5% vs SELL line 2.5%', 'cost of equity 9.40%: expected -10.7%', 'asset view across the Hormuz paths $15.33'],
}
bad5 = []
for s, needles in checks5.items():
    out = run(s)
    bad5 += [f'{s}: {n}' for n in needles if n not in out]
if bad5:
    print('TIEOUT FAILED (v20 checks)'); print('\n'.join(bad5)); sys.exit(1)
print('tieout v20 ok')
checks6 = {
 'charter_test_curves.py': ['Capesize  price $  78.3m; worth $  65.2m on Compass curve (+20%), $  63.0m on KOBC (+24%); residual is 59% of worth; residual -/+10% gives +28% / +13%', 'Kamsarmax price $  42.0m; worth $  30.2m on Compass curve (+39%)', 'Ultramax  price $  39.0m; worth $  29.8m on Compass curve (+31%)', 'VLCC      price $ 220.0m; worth $ 237.0m', 'Suezmax   price $ 150.0m; worth $ 150.5m',
                            'worth $61.6m, price +27% above it; with year 1 at the $38,000 one-year rate, +23%. the price needs $41,952/day', 'bulkers 19% of their value above what charters pay for; closing it by 2030 is -5.4%/yr on the bulkers, -3.8%/yr across the fleet', 'KOBC curve -4.4%; Capesize on the FFA curve -4.1%'],
 'sector_exposure_curves.py': ['SBLK  NAV hit if prices fell to what charters pay for: -23%; price/NAV 0.77 now, 1.00 after', 'GNK   NAV hit if prices fell to what charters pay for: -23%; price/NAV 0.79 now, 1.03 after', 'CMBT  NAV hit if prices fell to what charters pay for: -15%; price/NAV 0.58 now, 0.68 after', 'INSW  NAV hit if prices fell to what charters pay for: -0%', 'DHT   NAV hit if prices fell to what charters pay for: -0%'],
 'valuation_derived.py': ['normal year: 5.6% while the gap closes, 6.8% after', 'KOBC     drift -4.4%: 12-month value $15.65, expected total return +1.5%', 'FFA      drift -4.1%: 12-month value $15.67, expected total return +1.7%',
                          'cash $6.41 + end-2028 book at the cost of equity $12.64 + normal-year shortfall $-2.37 = $16.68 today; a year at 8.2% $+1.36, distributions -$2.35: $15.69 -> target $15.70, expected +1.9%',
                          'flat ship prices +3.1%; the same gap closed at half the speed +0.8%', 'cost of equity 7.50%: expected +7.6%', 'cost of equity 8.43%: expected -0.3%', 'cost of equity 9.40%: expected -6.9%', 'CMBT  price/book 1.47; ten-year ROE 6.8%',
                          'net debt $4,870m; loan-to-value 40% on broker values ($12,200m), 45% with the bulkers $1,303m lower', '58% on my rebuild (company reports 58.1%), 53% at charter value; it takes $5,015m off ship values, 71% of the bulker fleet', 'capex still to pay Q4 2026 to Q2 2029: $843m; liquidity $562m', '1.4x covered without the sales',
                          '2027 EPS: mine $2.50, consensus $2.16', '2028 EPS: mine $1.04, consensus $1.91 (-46%)', 'Q3 2026 bulker days on time charter: 745 of 9936, 7.5%'],
}
bad6 = []
for s, needles in checks6.items():
    out = run(s)
    bad6 += [f'{s}: {n}' for n in needles if n not in out]
if bad6:
    print('TIEOUT FAILED (v21 checks)'); print('\n'.join(bad6)); sys.exit(1)
print('tieout v21 ok')
checks7 = {'house_view_checks.py': [
  'my 2028 (published)                                     EPS 2027 $2.50, 2028 $1.04; expected 12-month total return +1.8%',
  'dry bulk on the forward curve                           EPS 2027 $2.43, 2028 $1.48; expected 12-month total return +4.8%',
  'dry bulk forward curve + tankers at the 3-year charter  EPS 2027 $2.43, 2028 $1.85; expected 12-month total return +7.8%',
  'my 2028 rates: VLCC $80,143, Suezmax $55,138, Capesize $23,594', '2028 EPS: mine $1.04; dry bulk at the forward curve +0.45; tankers at the 3-year charter +0.37; = $1.85 on market prices; consensus $1.91',
  'beta 0.52 7.23%', 'beta 0.75 8.25%', 'beta 0.96 9.17%', 'published case at 8.25%: expected +1.1%', 'published case at 7.23%: expected +10.3%', 'published case at 9.17%: expected -5.5%',
  'CMBT  price/book 1.47; ten-year ROE +7.9% reported, +6.8% without sale gains and impairments; justified (no growth, at 8.2%) 0.97 / 0.83',
  'SBLK  price/book 1.18; ten-year ROE +10.1% reported', 'DHT   price/book 2.49', 'INSW  price/book 2.16',
  'value +0.65 a share, expected +5.8%', 'EPS 2027 $1.78 (from $2.50), expected -2.4%', 'EPS 2027 $3.78 (from $2.50), expected +9.2%', 'on its SELL line at a cost of equity of 8.01%']}
bad7 = [f'{s}: {n}' for s, ns in checks7.items() for n in ns if n not in run(s)]
if bad7:
    print('TIEOUT FAILED (v22 checks)'); print('\n'.join(bad7)); sys.exit(1)
print('tieout v22 ok')
checks8 = {'forward_bias.py': ['vlcc      (realised, 25 reports 2015-2022): later earnings / 3-yr rate quoted = 1.01 on average; when the 3-yr rate was in its top third 0.75, bottom third 1.22',
                                'suezmax   (realised, 25 reports 2015-2022): later earnings / 3-yr rate quoted = 1.15 on average; when the 3-yr rate was in its top third 0.72',
                                'capesize  (later 1-yr quotes, 25 reports 2015-2022): later earnings / 3-yr rate quoted = 1.31 on average; when the 3-yr rate was in its top third 1.05'],
           'sell_case_checks.py': ['4 tanker sales if it stays shut: +3.0%', '8 tanker sales if it stays shut: +5.7%', '6 tankers sold in five months', 'net $-0.33 (-1.9%) before borrow', 'costs $8.47 (-47.8%)',
                                   'VLCC: on my 2028 rate after year one ($80,143), a five-year-old is worth $215.1m against $220.0m, price +2%', 'Suezmax: on my 2028 rate after year one ($55,138), a five-year-old is worth $133.0m against $150.0m, price +13%',
                                   '$2,041m of broker value, 17% of the fleet', '$623m ($2.15 a share)', '$1,225m ($4.22)', '+2.08 a share, +12.7 points']}
bad8 = [f'{s}: {n}' for s, ns in checks8.items() for n in ns if n not in run(s)]
if bad8:
    print('TIEOUT FAILED (v23 checks)'); print('\n'.join(bad8)); sys.exit(1)
print('tieout v23 ok')
checks9 = {'q4_preview.py': ['VLCC 115.5, Suezmax 159.1, Newcastlemax 62.7, Capesize 63.9, Kamsarmax/Panamax 16.0', 'Container +3.1, Chemicals +0.0, CSOV -5.4, CTV +7.9', 'Container +3.1, Chemicals +0.5, CSOV +6.2, CTV +10.1',
                              'group costs not in the breakevens, backed out of Q3: -7.2', 'profit ex gains $415m ($1.43); gains $190.8m; profit $606m, EPS $2.09', 'about $1.04', 'profit $710m, EPS $2.45', 'tankers $275m, dry bulk $143m',
                              '$79m a year ($0.27 a share), 6.5% on their $1,225m', '($3.34 a share) against $4.22', 'gap $0.88 a share, +5.4 points', 'about $44m']}
bad9 = [f'{s}: {n}' for s, ns in checks9.items() for n in ns if n not in run(s)]
if bad9:
    print('TIEOUT FAILED (v25 checks)'); print('\n'.join(bad9)); sys.exit(1)
print('tieout v25 ok')
checks10 = {'forward_bias_v2.py': ['Capesize on realised earnings (11 reports, 2019-2022; windows through 2018 dropped): later earnings / 3-yr rate 1.18 on average, top third 0.87', 'bottom third 1.51',
                                    'vlcc: top third 0.75 raw; 0.79 after a 5% commission; realised spot averaged 0.92x the same-year one-year quote (10 years), so 0.81 on that basis',
                                    'suezmax: top third 0.72 raw; 0.75 after a 5% commission; realised spot averaged 1.01x the same-year one-year quote (10 years), so 0.71 on that basis'],
            'valuation_v26.py': ['Q4 profit $604.9m (EPS $2.08); 12-month distributions $2.32; value today $16.60; 12-month $15.64 -> target $15.65; expected at the target +1.4%',
                                 'dry bulk at the forward curve: +4.4%', 'both at market forward prices: +7.4%; 2028 EPS $1.85', '2027 reopening: -2.9%', '2027 rates hold: +8.8%', 'four more tanker sales: +5.3%',
                                 '4 sales if shut): +2.6%', '8 sales if shut): +5.2%', 'other businesses at broker value: +6.8%', 'cost of equity of 7.96%', 'cost of equity 8.25%: +0.6%', 'cost of equity 7.23%: +9.8%', 'cost of equity 9.17%: -5.9%']}
bad10 = [f'{s}: {n}' for s, ns in checks10.items() for n in ns if n not in run(s)]
if bad10:
    print('TIEOUT FAILED (v26 checks)'); print('\n'.join(bad10)); sys.exit(1)
print('tieout v26 ok')
