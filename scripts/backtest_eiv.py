# does the earnings test point the right way? the same method as earnings_implied_value.py at the dates I have a
# five-year-old price and a one-year charter rate: Feb 2016 (Capesize only) and Feb 2023. through-cycle rates are the
# 2015-2025 averages, which is hindsight for 2016 and 2023; operating costs are today's. then what prices did next.
import json, os
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
opex = {r['segment'].split()[0]: float(r['opex']) for r in rows('fixtures.csv')}
tc = json.load(open(os.path.join(HERE, '..', 'results', 'through_cycle.json')))['through_cycle']
LDT = {'VLCC': 42000, 'Suezmax': 22000, 'Capesize': 24000}
later = {('2016-02', 'Capesize'): [('Feb 2023', 44.5, 7.0), ('Nov 2026', 78, 10.8)],
         ('2023-02', 'VLCC'): [('Nov 2026', 215, 3.75)], ('2023-02', 'Suezmax'): [('Nov 2026', 139, 3.75)], ('2023-02', 'Capesize'): [('Nov 2026', 78, 3.75)]}
def eiv(seg, y1, r=0.08, years=20):
    rates = [y1, (y1 + tc[seg]) / 2] + [tc[seg]] * (years - 2)
    return sum((x - opex[seg]) * 355 / 1e6 / (1 + r) ** (i + 0.5) for i, x in enumerate(rates)) + LDT[seg] * 460 / 1e6 / (1 + r) ** years
res = []
for p in rows('backtest_points.csv'):
    if not p['one_year_tc_usd_day']: print(f'{p["date"]} {p["type"]}: no one-year charter rate found, can\'t test'); continue
    seg, px = p['type'], float(p['five_year_old_usd_m'])
    v = eiv(seg, float(p['one_year_tc_usd_day']))
    call = 'cheap, should rise' if v > px * 1.05 else 'dear, should fall' if v < px * 0.95 else 'about fair'
    line = f'{p["date"]} {seg:8s} 5-year-old ${px}m, earnings value ${v:.0f}m ({v/px-1:+.0%}): {call}; newbuild ${p["newbuild_usd_m"]}m'
    for lab, nxt, yrs in later.get((p['date'], seg), []):
        line += f'; by {lab} ${nxt}m ({(nxt/px)**(1/yrs)-1:+.1%} a year)'
    print(line)
    res.append({'date': p['date'], 'type': seg, 'price': px, 'eiv': v})
right = sum(1 for r in res for lab, nxt, yrs in later[(r['date'], r['type'])][-1:] if (r['eiv'] > r['price']) == (nxt > r['price']))
print(f'direction right in {right} of {len(res)} tests; the miss is Capesize in Feb 2023, where the newbuild price went from $61m to about $75m')
json.dump(res, open(os.path.join(HERE, '..', 'results', 'backtest_eiv.json'), 'w'), indent=1)
