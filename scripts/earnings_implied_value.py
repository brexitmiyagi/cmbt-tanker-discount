# what a five-year-old ship is worth on what it can earn, against what it trades at.
# year 1 at today's one-year time charter rate (Compass, 16 Nov 2026), year 2 halfway from there to the through-cycle
# rate, then the through-cycle rate (CMB.TECH/Euronav realised spot 2015-2025 for tankers, Clarksons-implied 10-year
# average for Capesize, through_cycle.py) until the ship is scrapped at 25 at lightweight x $460/ldt.
# opex is CMB.TECH's own (Q3 2026 release, fixtures.csv). 355 earning days a year. no drydock, no G&A, flat nominal
# rates and opex: crude, and on the generous side, because opex and drydocks rise and through-cycle includes 2022-25.
# the gap between price and earnings-implied value, closed over ten years, gives a yearly drift in ship prices.
import os, json
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
mr = {r['item']: float(r['value']) for r in rows('market_rates_2026-11-16.csv')}
sh = {(r['type'], r['age']): float(r['value_usd_m']) for r in rows('secondhand_values_2026-11-16.csv')}
opex = {r['segment'].split()[0]: float(r['opex']) for r in rows('fixtures.csv')}
tc = json.load(open(os.path.join(HERE, '..', 'results', 'through_cycle.json')))['through_cycle']
LDT = {'VLCC': 42000, 'Suezmax': 22000, 'Capesize': 24000}    # my estimates
ships = {'VLCC': mr['vlcc_1yr_tc'], 'Suezmax': mr['suezmax_1yr_tc'], 'Capesize': mr['capesize_1yr_tc']}

def eiv(seg, r, years=20, days=355):
    y1, tcy = ships[seg], tc[seg]
    rates = [y1, (y1 + tcy) / 2] + [tcy] * (years - 2)
    pv = sum((x - opex[seg]) * days / 1e6 / (1 + r) ** (i + 0.5) for i, x in enumerate(rates))
    return pv + LDT[seg] * 460 / 1e6 / (1 + r) ** years

out = {}
for seg in ships:
    px = sh[(seg, '5')]
    vals = {r: eiv(seg, r) for r in (0.07, 0.08, 0.09)}
    drift = {r: (v / px) ** 0.1 - 1 for r, v in vals.items()}
    out[seg] = {'price': px, 'eiv': vals[0.08], 'drift': drift[0.08], 'drift_range': [drift[0.09], drift[0.07]]}
    print(f'{seg:8s} 5-year-old ${px:.0f}m; earnings-implied ${vals[0.08]:.0f}m at 8% (${vals[0.09]:.0f}m-${vals[0.07]:.0f}m at 9%-7%), '
          f'{vals[0.08]/px-1:+.0%}; closing the gap over ten years is {drift[0.08]:+.1%} a year ({drift[0.09]:+.1%} to {drift[0.07]:+.1%})')
# CMB.TECH's fleet mix by value, 30 Sep 2026: tankers $3,128m, dry bulk $7,017m (Capesize stands in for dry bulk)
w = out['VLCC']['drift'] * 0.5 + out['Suezmax']['drift'] * 0.5
fleet = (w * 3128 + out['Capesize']['drift'] * 7017) / 10145
print(f'fleet-weighted drift (tankers half VLCC half Suezmax, dry bulk as Capesize): {fleet:+.1%} a year')
# how much of the earnings-implied value is the first two years
for seg in ships:
    first2 = sum((x - opex[seg]) * 355 / 1e6 / 1.08 ** (i + 0.5) for i, x in enumerate([ships[seg], (ships[seg] + tc[seg]) / 2]))
    print(f'  {seg}: first two years ${first2:.0f}m of the ${out[seg]["eiv"]:.0f}m')
out['fleet_drift'] = fleet
json.dump(out, open(os.path.join(HERE, '..', 'results', 'earnings_implied_value.json'), 'w'), indent=1)

# the other way round: what through-cycle rate does today's price need, at 8%?
for seg in ships:
    lo, hi = 0.0, 200000.0
    keep = tc[seg]
    for _ in range(60):
        m = (lo + hi) / 2; tc[seg] = m
        lo, hi = (m, hi) if eiv(seg, 0.08) < sh[(seg, '5')] else (lo, m)
    tc[seg] = keep
    out[seg]['rate_needed'] = m
    print(f'  {seg}: today\'s 5-year-old price needs ${m:,.0f} a day from year 3 on, against ${keep:,.0f} through the cycle')
json.dump(out, open(os.path.join(HERE, '..', 'results', 'earnings_implied_value.json'), 'w'), indent=1)

# the same gap closed over twenty years instead of ten (a ship's remaining life)
d20 = {seg: (out[seg]['eiv'] / out[seg]['price']) ** 0.05 - 1 for seg in ships}
f20 = ((d20['VLCC'] + d20['Suezmax']) / 2 * 3128 + d20['Capesize'] * 7017) / 10145
out['fleet_drift_20y'] = f20
print(f'fleet-weighted drift closing the gap over twenty years: {f20:+.1%} a year; over ten: {fleet:+.1%}')
json.dump(out, open(os.path.join(HERE, '..', 'results', 'earnings_implied_value.json'), 'w'), indent=1)
