# the obvious objection to earnings_implied_value.py: in the long run rates settle where a new ship pays for itself.
# so what day rate does a newbuild need, over 25 years at 8%, to earn back its cost? if that's close to the rate
# today's secondhand price needs, the earnings test only says "historical rates were below replacement cost".
import json, os
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
ev = json.load(open(os.path.join(HERE, '..', 'results', 'earnings_implied_value.json')))
opex = {r['segment'].split()[0]: float(r['opex']) for r in rows('fixtures.csv')}
tc = json.load(open(os.path.join(HERE, '..', 'results', 'through_cycle.json')))['through_cycle']
LDT = {'VLCC': 42000, 'Suezmax': 22000, 'Capesize': 24000}
nb = {}
for r in rows('newbuild_prices_2026.csv'):
    nb.setdefault(r['type'], float(r['price_usd_m']))     # first row per type is the one I use
def needed(cost, seg, r=0.08, years=25, days=355):
    ann = sum(1 / (1 + r) ** (i + 0.5) for i in range(years))
    scrap = LDT[seg] * 460 / 1e6 / (1 + r) ** years
    return (cost - scrap) / ann / days * 1e6 + opex[seg]
out = {}
for seg in ('VLCC', 'Suezmax', 'Capesize'):
    n = needed(nb[seg], seg)
    out[seg] = {'newbuild': nb[seg], 'rate_newbuild_needs': n, 'rate_5yr_needs': ev[seg]['rate_needed'], 'through_cycle': tc[seg]}
    print(f'{seg:8s} newbuild ${nb[seg]:.1f}m needs ${n:,.0f} a day over 25 years at 8%; today\'s 5-year-old price needs ${ev[seg]["rate_needed"]:,.0f} from year 3; through-cycle ${tc[seg]:,.0f}')
for r in (0.07, 0.09):
    print(f'  at {r:.0%}: Capesize newbuild needs ${needed(nb["Capesize"], "Capesize", r):,.0f}, VLCC ${needed(nb["VLCC"], "VLCC", r):,.0f}')
# the older newbuild prices, same test: what rate did a Capesize newbuild need when it cost $46m (2016) and $61m (2023)?
for y, c in (('2016', 46.0), ('2023', 61.0), ('2025 average', 70.9)):
    print(f'  Capesize newbuild at ${c}m ({y}) needs ${needed(c, "Capesize"):,.0f} a day')
json.dump(out, open(os.path.join(HERE, '..', 'results', 'replacement_cost.json'), 'w'), indent=1)
