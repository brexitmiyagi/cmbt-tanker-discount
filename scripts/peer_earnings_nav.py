# the earnings NAV for the peers, as far as public data allows. each fleet is marked at its average age with the
# same method as earnings_nav.py (Capesize curve and rates for the bulkers, which flatters nothing for Star Bulk and
# Genco, whose fleets are more than half Ultramax/Supramax/Kamsarmax; VLCC for DHT). ages: Star Bulk 12.7 years and
# 138 ships (Q3 2026 call), Genco 12.9 years and 44 ships (Q3 2026 release). DHT's age is not verified: 9.4 years in
# Jan 2024 (LWS Research), so about 11.4 now if the fleet were unchanged, which it isn't. International Seaways gives
# no average age and is mostly product tankers with no public curve here, so it's left out.
import json, os
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda f: json.load(open(os.path.join(HERE, '..', 'results', f)))
tc, rc = J('through_cycle.json')['through_cycle'], J('replacement_cost.json')
mr = {r['item']: float(r['value']) for r in rows('market_rates_2026-11-16.csv')}
y1 = {'VLCC': mr['vlcc_1yr_tc'], 'Capesize': mr['capesize_1yr_tc']}
opex = {r['segment'].split()[0]: float(r['opex']) for r in rows('fixtures.csv')}
LDT = {'VLCC': 42000, 'Capesize': 24000}
curve = {}
for r in rows('secondhand_values_2026-11-16.csv'):
    curve.setdefault(r['type'], {})[int(r['age'])] = float(r['value_usd_m'])
def broker(seg, age):
    c = dict(curve[seg]); c[25] = LDT[seg] * 460 / 1e6; p = sorted(c)
    for a, b in zip(p, p[1:]):
        if a <= age <= b: return c[a] + (c[b] - c[a]) * (age - a) / (b - a)
def eiv(seg, age, lr, r=0.08):
    n = max(1, round(25 - age)); rates = ([y1[seg], (y1[seg] + lr) / 2] + [lr] * n)[:n]
    return sum((x - opex[seg]) * 355 / 1e6 / (1 + r) ** (i + 0.5) for i, x in enumerate(rates)) + LDT[seg] * 460 / 1e6 / (1 + r) ** n
px = {r['ticker']: float(r['close_2026_11_25']) for r in rows('prices_2026-11-25.csv')}
nav = {r['ticker']: r for r in rows('peers_nav.csv')}
peers = {'SBLK': ('Capesize', 12.7), 'GNK': ('Capesize', 12.9), 'DHT': ('VLCC', 11.4)}
out = {}
for t, (seg, age) in peers.items():
    fv, nd, shs = float(nav[t]['fleet_value_usd_m']), float(nav[t]['net_debt_usd_m']), float(nav[t]['shares_m'])
    mc = px[t] * shs; bnav = fv - nd
    res = {'broker': mc / bnav}
    for lab, lr in (('through-cycle', tc[seg]), ('replacement', rc[seg]['rate_newbuild_needs'])):
        ratio = eiv(seg, age, lr) / broker(seg, age)
        res[lab] = mc / (fv * ratio - nd)
    out[t] = res
    print(f'{t:5s} ({seg} curve, age {age}): price/NAV on broker values {res["broker"]:.2f}, on through-cycle earnings {res["through-cycle"]:.2f}, on replacement-cost earnings {res["replacement"]:.2f}')
en = J('earnings_nav.json'); p = px['CMBT']
print(f'CMBT at ${p}: broker {p/30.67:.2f}, through-cycle earnings {p/en["H"]["nav2"]:.2f}, replacement-cost earnings {p/en["R"]["nav2"]:.2f} (route-2 NAVs from earnings_nav.py)')
out['CMBT'] = {'broker': p / 30.67, 'through-cycle': p / en['H']['nav2'], 'replacement': p / en['R']['nav2']}
json.dump(out, open(os.path.join(HERE, '..', 'results', 'peer_earnings_nav.json'), 'w'), indent=1)
