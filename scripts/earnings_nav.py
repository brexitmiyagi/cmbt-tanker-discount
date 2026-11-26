# CMB.TECH's NAV with the fleet marked on earnings instead of broker values. every ship on the water (fleet lists in
# data/), valued with the earnings_implied_value.py method at its own age: one year at today's one-year charter, a
# year halfway down, then a long-run rate until scrap at 25. two long-run rates: (H) the 2015-2025 through-cycle
# averages, (R) the rate a newbuild needs to earn back its cost (replacement_cost.py). broker value by age is the
# Compass/Clarksons curve, straight lines between the points and down to scrap at 25. Kamsarmaxes and Panamaxes take
# the Capesize ratio, Newcastlemaxes are treated as Capesizes. the segment ratios are applied to the company's own
# broker fleet values ($3,128m tankers, $7,017m dry bulk, 30 Sep 2026).
import json, os
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda f: json.load(open(os.path.join(HERE, '..', 'results', f)))
tc, rc = J('through_cycle.json')['through_cycle'], J('replacement_cost.json')
mr = {r['item']: float(r['value']) for r in rows('market_rates_2026-11-16.csv')}
y1 = {'VLCC': mr['vlcc_1yr_tc'], 'Suezmax': mr['suezmax_1yr_tc'], 'Capesize': mr['capesize_1yr_tc']}
opex = {r['segment'].split()[0]: float(r['opex']) for r in rows('fixtures.csv')}
LDT = {'VLCC': 42000, 'Suezmax': 22000, 'Capesize': 24000}
curve = {}
for r in rows('secondhand_values_2026-11-16.csv'):
    curve.setdefault(r['type'], {})[int(r['age'])] = float(r['value_usd_m'])
def broker(seg, age):
    c = dict(curve[seg]); c[25] = LDT[seg] * 460 / 1e6
    pts = sorted(c)
    for a, b in zip(pts, pts[1:]):
        if a <= age <= b: return c[a] + (c[b] - c[a]) * (age - a) / (b - a)
    return c[pts[-1]]
def eiv(seg, age, lr, r=0.08):
    n = max(1, 25 - age)
    rates = ([y1[seg], (y1[seg] + lr) / 2] + [lr] * (n - 2))[:n]
    return sum((x - opex[seg]) * 355 / 1e6 / (1 + r) ** (i + 0.5) for i, x in enumerate(rates)) + LDT[seg] * 460 / 1e6 / (1 + r) ** n
ships = []
for r in rows('fleet_crude_tankers.csv'):
    if r['type'] in ('VLCC', 'Suezmax') and r['status_25_nov_2026'].startswith(('on the water', 'one on the water')):
        ships.append((r['type'], max(0, 2026 - int(r['built'][:4]))))
for r in rows('fleet_dry_bulk_20F.csv'):
    ships.append(('Capesize', max(0, 2026 - int(r['built']))))
seg_of = lambda s: 'tankers' if s in ('VLCC', 'Suezmax') else 'dry bulk'
out = {}
for case, lr in (('H', tc), ('R', {s: rc[s]['rate_newbuild_needs'] for s in rc})):
    tot = {'tankers': [0, 0], 'dry bulk': [0, 0]}
    for s, a in ships:
        tot[seg_of(s)][0] += broker(s, a); tot[seg_of(s)][1] += eiv(s, a, lr[s])
    ratio = {k: v[1] / v[0] for k, v in tot.items()}
    adj = 3128 * (ratio['tankers'] - 1) + 7017 * (ratio['dry bulk'] - 1)
    sh = 290.169769
    n2, n1 = 30.67 + adj / sh, 25.02 + adj / sh
    out[case] = {'ratio': ratio, 'adj': adj, 'nav2': n2, 'nav1': n1}
    lab = 'through-cycle rates' if case == 'H' else 'replacement-cost rates'
    print(f'({case}) {lab}: tankers on earnings {ratio["tankers"]:.0%} of broker value, dry bulk {ratio["dry bulk"]:.0%}; fleet ${adj:+,.0f}m;'
          f' NAV route 2 ${n2:.2f} (price/NAV {17.54/n2:.2f}), route 1 ${n1:.2f} ({17.54/n1:.2f})')
print(f'{len(ships)} ships marked; broker NAVs $30.67 (price/NAV {17.54/30.67:.2f}) and $25.02 ({17.54/25.02:.2f})')
json.dump(out, open(os.path.join(HERE, '..', 'results', 'earnings_nav.json'), 'w'), indent=1)
