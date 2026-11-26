# the discount as a series, every company on the same date as its own fleet values (quarter-end prices against
# quarter-end broker values), with error bands. peers on enterprise value over fleet value; where a company gives a
# loan-to-value or leverage ratio instead of a fleet value, fleet value = net debt / ratio, and the ratio's rounding
# (+/-0.5 point, +/-0.05 for DHT's one-decimal figure) sets the band. CMB.TECH's segments go on the peer multiples,
# charter marks come off, and the extra discount in the price is solved for on both company NAVs.
# gaps: CMB.TECH's Q1 2026 value-adjusted ratio and fleet split aren't in the release, and no tanker peer gave a
# fleet value or leverage ratio I could find for 30 June 2026, so June brackets tankers with the Dec and Sep multiples.
import json, os, itertools
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
sh = 290.169769
RAT = {'GNK': 0.005, 'DHT': 0.0005}
def mult(r, pick):
    cap = float(r['close']) * float(r['shares_m']); nd = float(r['net_debt_usd_m'])
    if r['fleet_value_usd_m']:
        f = {'mid': float(r['fleet_value_usd_m']), 'lo': float(r['fleet_low']), 'hi': float(r['fleet_high'])}[pick]
    else:
        import re
        x = float(re.search(r'([\d.]+)%', r['basis']).group(1)) / 100; e = RAT[r['ticker']]
        f = nd / {'mid': x, 'lo': x + e, 'hi': x - e}[pick]
    return (cap + nd) / f
peers = rows('peers_quarterly.csv')
M = {}
for r in peers:
    d = r['date']
    for pick in ('mid', 'lo', 'hi'):
        M.setdefault((d, r['segment'], pick), []).append(mult(r, pick))
print('peer EV / fleet value (mid, band):')
for d in sorted({r['date'] for r in peers}):
    for s in ('dry bulk', 'tanker'):
        if (d, s, 'mid') in M:
            v = [sum(M[(d, s, p)]) / len(M[(d, s, p)]) for p in ('mid', 'lo', 'hi')]
            names = ', '.join(f"{r['ticker']} {mult(r, 'mid'):.2f}" for r in peers if r['date'] == d and r['segment'] == s)
            print(f'  {d} {s:8s} {v[0]:.2f} ({min(v):.2f}-{max(v):.2f})  [{names}]')
pv_pre = sum((48576 - 33455) * 365 * 0.25 / 1e6 / 1.08 ** (q * 0.25 + 0.125) for q in range(12)) * 8
MARKS = {'2025-12-31': pv_pre, '2026-06-30': 304.0, '2026-09-30': 304.0}
def seg(d, s, p):
    k = (d, s, p)
    if k in M: return sum(M[k]) / len(M[k])
    if s == 'tanker' and d == '2026-06-30':   # bracket with Dec and Sep
        a, b = seg('2025-12-31', s, 'mid'), seg('2026-09-30', s, 'mid')
        return {'mid': (a + b) / 2, 'lo': min(a, b), 'hi': max(a, b)}[p]
out = {}
for c in rows('cmbt_quarterly.csv'):
    d = c['date']; px = float(c['close']); cap = px * sh
    dry, tank, fleet = float(c['dry_bulk_fmv']), float(c['tanker_fmv']), float(c['fleet_fmv']); other = fleet - dry - tank
    for route in ('1', '2'):
        nav = float(c[f'nav_route{route}_ps']) * sh
        vals = []
        for pd, pt, po in itertools.product(('mid', 'lo', 'hi'), ('mid', 'lo', 'hi'), ('dry', 'one')):
            md, mt = seg(d, 'dry bulk', pd), seg(d, 'tanker', pt); mo = md if po == 'dry' else 1.0
            peq = nav - (1 - md) * dry - (1 - mt) * tank - (1 - mo) * other - MARKS[d]
            vals.append(1 - cap / peq)
        md, mt = seg(d, 'dry bulk', 'mid'), seg(d, 'tanker', 'mid')
        peq = nav - (1 - md) * (dry + other) - (1 - mt) * tank - MARKS[d]
        mid = 1 - cap / peq
        out[f'{d} route {route}'] = {'mid': mid, 'lo': min(vals), 'hi': max(vals)}
        print(f'{d} route {route}: CMB.TECH extra discount {mid:.0%} (band {min(vals):.0%} to {max(vals):.0%})')
# the anomaly, same-date basis: hold the Dec 2025 discount (route 1) and solve the tanker multiple at 30 Sep
c = {r['date']: r for r in rows('cmbt_quarterly.csv')}['2026-09-30']
dry, tank, fleet = 7017, 3128, 12186; other = fleet - dry - tank
for route in ('1', '2'):
    res = []
    for d0 in (out[f'2025-12-31 route {route}'][k] for k in ('mid', 'lo', 'hi')):
        need = 18.93 * sh / (1 - d0)
        md = seg('2026-09-30', 'dry bulk', 'mid')
        rest = float(c[f'nav_route{route}_ps']) * sh - (1 - md) * (dry + other) - MARKS['2026-09-30']
        res.append(1 - (rest - need) / (tank - MARKS['2026-09-30']))
    mt = seg('2026-09-30', 'tanker', 'mid')
    print(f'route {route}, 30 Sep: holding the Dec discount, tankers implied at {res[0]:.2f}x (band {min(res):.2f}-{max(res):.2f}) vs tanker peers {mt:.2f}x ({res[0]/mt-1:+.0%}; band {min(res)/mt-1:+.0%} to {max(res)/mt-1:+.0%})')
    out[f'implied tanker route {route}'] = res
json.dump(out, open(os.path.join(HERE, '..', 'results', 'holdco_series.json'), 'w'), indent=1)
# independent anchor: today's (30 Sep) peer-implied equity less each route's average discount over the series
c = {r['date']: r for r in rows('cmbt_quarterly.csv')}['2026-09-30']
for route in ('1', '2'):
    avg = sum(out[f'{d} route {route}']['mid'] for d in ('2025-12-31', '2026-06-30', '2026-09-30')) / 3
    md, mt = seg('2026-09-30', 'dry bulk', 'mid'), seg('2026-09-30', 'tanker', 'mid')
    peq = float(c[f'nav_route{route}_ps']) * sh - (1 - md) * (7017 + 2041) - (1 - mt) * 3128 - 304
    print(f'anchor route {route}: peer-implied equity ${peq/sh:.2f} a share at 30 Sep, less the {avg:.0%} average discount = ${peq*(1-avg)/sh:.2f} (price then $18.93)')
    out[f'anchor route {route}'] = peq * (1 - avg) / sh
json.dump(out, open(os.path.join(HERE, '..', 'results', 'holdco_series.json'), 'w'), indent=1)
# carry the 30 Sep anchors to today's price in proportion (CMB.TECH and its peers have moved together since)
for route in ('1', '2'):
    c9 = {r['date']: r for r in rows('cmbt_quarterly.csv')}['2026-09-30']
    md, mt = seg('2026-09-30', 'dry bulk', 'mid'), seg('2026-09-30', 'tanker', 'mid')
    peq = float(c9[f'nav_route{route}_ps']) * sh - (1 - md) * (7017 + 2041) - (1 - mt) * 3128 - 304
    for lab, dd in (('pre-war discount', out[f'2025-12-31 route {route}']['mid']), ('average discount', sum(out[f'{d} route {route}']['mid'] for d in ('2025-12-31', '2026-06-30', '2026-09-30')) / 3)):
        v = peq * (1 - dd) / sh
        print(f'route {route} at its {lab} ({dd:.0%}): ${v:.2f} at 30 Sep = {v/18.93:.3f}x the price then; on $17.54 today that is ${17.54*v/18.93:.2f}')
