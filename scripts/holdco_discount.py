# is the discount in the tankers, or in the whole company? value each CMB.TECH segment at what listed peers
# trade at (enterprise value over broker fleet value), keep everything else at the company's NAV, and solve for
# the extra discount the share price implies. do it before the war (31 Dec 2025) and now, on both company NAVs.
# Star Bulk gives no fleet value at 31 Dec 2025, so pre-war dry bulk rests on Genco alone.
import json, os
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
sh = 290.169769

def evx(r, px_col):
    cap = float(r[px_col]) * float(r['shares_m'])
    return (cap + float(r['net_debt_usd_m'])) / float(r['fleet_value_usd_m'])

def seg_mult(file, px_col):
    out = {}
    for r in rows(file):
        m = evx(r, px_col)
        print(f'  {r["ticker"]:5s} {r["segment"]:9s} EV/fleet value {m:.2f}')
        out.setdefault(r['segment'], []).append(m)
    return {k: sum(v) / len(v) for k, v in out.items()}

# CMB.TECH: fleet by segment (company broker values), NAV on both routes, charter marks on the chartered tankers
cases = {
    'pre-war, 31 Dec 2025': dict(file='peers_nav_2025-12-31.csv', px='close_2025_12_31', close=9.65,
                                 dry=6329, tank=2383, fleet=10686, nav1=15.78 * sh, nav2=24.07 * sh, marks=None),
    'now, 24 Nov 2026 price on 30 Sep values': dict(file='peers_nav.csv', px='close_2026_11_24', close=17.54,
                                 dry=7017, tank=3128, fleet=12186, nav1=7259.1, nav2=8900.8, marks=304.0),
}
# pre-war charter marks: 8 Suezmaxes on charter at the 2025 charter average ($33,455) against the pre-war market
# rate used in the model ($48,210), 3 years left, 8%. Cap Grace and Cap Joseph hadn't delivered yet.
pv = sum((48210 - 33455) * 365 * 0.25 / 1e6 / 1.08 ** (q * 0.25 + 0.125) for q in range(12)) * 8
cases['pre-war, 31 Dec 2025']['marks'] = pv
res = {}
for name, c in cases.items():
    print(name)
    m = seg_mult(c['file'], c['px'])
    md, mt = m['dry bulk'], m['tanker']
    other = c['fleet'] - c['dry'] - c['tank']
    cap = c['close'] * sh
    out = {'m_dry': md, 'm_tank': mt, 'marks': c['marks']}
    for route in ('nav1', 'nav2'):
        for mo, lab in ((md, 'other at dry bulk multiple'), (1.0, 'other at 1.0x')):
            peer_eq = c[route] - (1 - md) * c['dry'] - (1 - mt) * c['tank'] - (1 - mo) * other - c['marks']
            d = 1 - cap / peer_eq
            out[f'{route} {lab}'] = {'peer_equity': peer_eq, 'discount': d}
            print(f'  route {route[-1]}, {lab}: peer-implied equity ${peer_eq:,.0f}m (${peer_eq/sh:.2f}); market cap ${cap:,.0f}m; holdco discount {d:.0%}')
    res[name] = out
    print(f'  segment multiples: dry bulk {md:.2f}, tankers {mt:.2f}; charter marks ${c["marks"]:,.0f}m')

# isolate the tankers: keep the pre-war holdco discount on everything, value dry bulk and other at today's dry
# bulk peer multiple, and solve for the tanker multiple today's price implies (tankers net of charter marks).
pre, now = res['pre-war, 31 Dec 2025'], res['now, 24 Nov 2026 price on 30 Sep values']
c = cases['now, 24 Nov 2026 price on 30 Sep values']
other = c['fleet'] - c['dry'] - c['tank']
for route in ('nav1', 'nav2'):
    d0 = pre[f'{route} other at dry bulk multiple']['discount']
    need = c['close'] * sh / (1 - d0)
    rest = c[route] - (1 - now['m_dry']) * (c['dry'] + other) - c['marks']
    mt_implied = 1 - (rest - need) / (c['tank'] - c['marks'])
    res[f'implied tanker multiple {route}'] = mt_implied
    print(f'route {route[-1]}: with the pre-war holdco discount ({d0:.0%}), today\'s price implies tankers (net of charter marks) at {mt_implied:.2f}x vs tanker peers {now["m_tank"]:.2f}x ({mt_implied/now["m_tank"]-1:+.0%})')
json.dump(res, open(os.path.join(HERE, '..', 'results', 'holdco_discount.json'), 'w'), indent=1)
# if the pre-war holdco discount came back, at today's peer multiples, what's the share worth?
for route in ('nav1', 'nav2'):
    for lab in ('other at dry bulk multiple', 'other at 1.0x'):
        d0 = pre[f'{route} {lab}']['discount']
        v = now[f'{route} {lab}']['peer_equity'] * (1 - d0) / sh
        print(f'route {route[-1]}, {lab}: pre-war discount {d0:.0%} on today\'s peer-implied equity = ${v:.2f} a share')
