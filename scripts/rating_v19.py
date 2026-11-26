# the rating re-priced at the 25 Nov 2026 close ($17.72) with Kalshi read on 26 Nov (normal traffic before 1 Apr 2027
# 12%, before 1 Jan 2028 32.5%, mid of bid and ask), plus the bridge from the earnings NAV to the target.
# same machinery as rating.py's v17 block: the asset view is end-2027 NAV across the four Hormuz paths at CMB.TECH's
# price/NAV (today's multiple for the base, the best of the past year for the bull, the pre-war low for the bear),
# with -2% a year of ship-price drift applied to path D tankers; the cash view is the DCF at a 6.1% normal year.
# today's multiples move with the price; the best and lowest multiples are history and don't.
import json, os, math
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda f: json.load(open(os.path.join(HERE, '..', 'results', f)))
hp, ms, rw, en = J('hormuz_paths.json'), J('model_summary.json'), J('roe_windows.json'), J('earnings_nav.json')
sh = 290.169769
px = {r['ticker']: float(r['close_2026_11_25']) for r in rows('prices_2026-11-25.csv')}['CMBT']
old = 17.54
K = {r['contract']: (float(r['yes_bid']) + float(r['yes_ask'])) / 2 for r in rows('kalshi_2026-11-26.csv')}
pA = K['normal traffic before 1 Apr 2027']; pAB = K['normal traffic before 1 Jan 2028']
W = {'A': pA, 'B': pAB - pA, 'C': 0.0, 'D': 1 - pAB}
gap, DRY, TANK = 5405.8 - 3764.1, 7017.0, 3128.0
mult = {'route 2': {'low': 0.40, 'now': 0.57 * px / old, 'high': 0.62}, 'route 1': {'low': 0.61, 'now': 0.70 * px / old, 'high': 0.76}}
dist = ms['dist12']
def asset(drift, wb):
    cum = 1 - (1 + drift) ** 1.25
    dry_extra = max(0.0, cum - abs(hp['dry_cut']))
    vals = {'now': 0, 'high': 0, 'bear': 0}
    for route, mm in mult.items():
        nav = {k: hp[k]['nav'] - (gap if route == 'route 1' else 0) for k in 'ABCD'}
        nav['D'] -= TANK * cum
        for k in 'ABCD': nav[k] -= DRY * dry_extra
        vals['now'] += sum(W[k] * mm['now'] * nav[k] for k in 'ABCD') / sh / 2
        vals['high'] += sum(W[k] * mm['high'] * nav[k] for k in 'ABCD') / sh / 2
        vals['bear'] += mm['low'] * (hp['A']['nav'] - (gap if route == 'route 1' else 0) - (0.2 + hp['dry_cut']) * DRY) / sh / 2
    a = 0.25 * vals['high'] + (0.75 - wb) * vals['now'] + wb * vals['bear']
    return a, vals
fleet_t, fleet_d = 3128, 7017
pred = lambda e, g: (e * fleet_t + g * fleet_d) / (fleet_t + fleet_d)
rc = rw['routine_common']
kk = (pred(rc['Euronav'], rc['Golden Ocean']) - pred(0.067, 0.068)) / ((98 / 76.2) ** (1 / 7) - 1)
f27, f28, q4 = ms['fcf27'] / sh, ms['fcf28'] / sh, ms['fcf_q4_26'] / sh; book = ms['eq28'] / sh
def dcf12(r, k):
    pv3 = q4 / (1 + k) ** 0.125 + f27 / (1 + k) ** 0.625 + f28 / (1 + k) ** 1.625
    return (pv3 + (r * book / k) / (1 + k) ** 1.625) * (1 + k) - dist
k = (4.91 + 0.65 * 5) / 100
def er(drift=-0.02, wb=pAB, kq=k):
    a, v = asset(drift, wb); d = dcf12(pred(0.067, 0.068) + kk * drift, kq)
    p12 = (a + d) / 2
    return p12, (p12 + dist) / px - 1, a, d, v
p12, e, a, d, v = er()
t = math.ceil(p12 * 20) / 20
print(f'price ${px} (was ${old}); Kalshi: before 1 Apr 2027 {pA:.1%}, before 1 Jan 2028 {pAB:.1%} -> bear weight {pAB:.1%}')
print(f'asset view: bull ${v["high"]:.2f}, base ${v["now"]:.2f}, bear ${v["bear"]:.2f} -> ${a:.2f}; DCF in 12 months ${d:.2f}')
print(f'target ${p12:.2f} -> ${t:.2f} (rounded up), expected {(t+dist)/px-1:+.1%} vs SELL line {k-0.05:.1%}')
for lab, dr in (('flat', 0.0), ('+3.7% (2016-23)', (98 / 76.2) ** (1 / 7) - 1), ('-4.5%', -0.045)):
    print(f'  drift {lab}: expected {er(dr)[1]:+.1%}')
for kq in (0.075, 0.0843, 0.094):
    print(f'  cost of equity {kq:.2%}: expected {er(kq=kq)[1]:+.1%} vs SELL line {kq-0.05:.1%}')
lo, hi = -0.06, 0.06
for _ in range(60):
    m = (lo + hi) / 2; lo, hi = (m, hi) if er(m)[1] < k - 0.05 else (lo, m)
print(f'  the SELL holds for any drift below {m:+.2%} a year')
lo, hi = 0.0, 0.75
for _ in range(60):
    m = (lo + hi) / 2; lo, hi = (m, hi) if er(wb=m)[1] > k - 0.05 else (lo, m)
print(f'  the SELL holds while the bear carries more than {m:.1%}; at 25% expected {er(wb=0.25)[1]:+.1%}')

# the bridge: why a stock at 0.90 times its through-cycle earnings NAV can still be a SELL.
# compare like with like: the target plus 12 months of distributions, discounted back a year at the cost of equity,
# is what the target says the share is worth today. the gap to the earnings NAV splits into the reopening risk
# (the bear weight times the bear's tanker cut, at today's broker values, per share) and what's left, which is the
# discount the target applies to CMB.TECH as a holding company.
navE = en['H']['nav2']
pv_t = (t + dist) / (1 + k)
reopen = pAB * TANK * 0.31 / sh
resid = navE - reopen - pv_t
print(f'\nbridge: through-cycle earnings NAV ${navE:.2f} (price/NAV {px/navE:.2f}); target + distributions discounted a year ${pv_t:.2f}')
print(f'  reopening risk {pAB:.1%} x 31% of $3,128m tankers = -${reopen:.2f}; what is left -${resid:.2f} = {resid/(navE-reopen):.0%} discount after the reopening risk')
print(f'  the price today is {px/(navE-reopen):.2f} times the earnings NAV after the reopening risk; the target is {pv_t/(navE-reopen):.2f} times')
pe = J('peer_earnings_nav.json')
print('  peers on the same through-cycle earnings basis: ' + ', '.join(f'{t2} {pe[t2]["through-cycle"]:.2f}' for t2 in ('SBLK', 'GNK', 'DHT')))
json.dump({'px': px, 'target': t, 'er': (t + dist) / px - 1, 'pv_t': pv_t, 'navE': navE, 'reopen': reopen, 'resid': resid,
           'bull': v['high'], 'base': v['now'], 'bear': v['bear'], 'asset': a, 'dcf': d, 'wb': pAB},
          open(os.path.join(HERE, '..', 'results', 'rating_v19.json'), 'w'), indent=1)
