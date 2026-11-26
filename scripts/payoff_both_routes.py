# the payoff on both company NAVs, with the multiple allowed to reset, not held at its best level.
# route 2 = broker basis (book equity + broker fleet value - vessels at book), route 1 = backed out of the
# 58.1% value-adjusted equity ratio. route 1 sits $1,641.7m lower at 30 Sep (uplift $3,764.1m vs $5,405.8m).
# multiples are CMB.TECH's own price/NAV on each route at 31 Dec 2025, 30 Jun, 30 Sep and 24 Nov 2026.
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
sh = 290.169769
hp = json.load(open(os.path.join(HERE, '..', 'results', 'hormuz_paths.json')))
ms = json.load(open(os.path.join(HERE, '..', 'results', 'model_summary.json')))
px, dec_div = 17.54, 0.65
gap = 5405.8 - 3764.1
DRY = 7017.0
mult = {'route 2': {'low': 0.40, 'now': 0.57, 'high': 0.62}, 'route 1': {'low': 0.61, 'now': 0.70, 'high': 0.76}}
W = {'mine': {'A': .20, 'B': .25, 'C': .25, 'D': .30},
     'Kalshi 25 Nov (Apr 1 12%, Jan 1 2028 33%)': {'A': .12, 'B': .21, 'C': 0, 'D': .67},
     'Polymarket 25 Nov (Mar 31 12.5%, Dec 31 2027 35.5%)': {'A': .125, 'B': .23, 'C': 0, 'D': .645}}
dist = ms['dist12']
out = {}
for route, mm in mult.items():
    nav = {k: hp[k]['nav'] - (gap if route == 'route 1' else 0) for k in 'ABCD'}
    print(f'{route}: forward NAV a share A ${nav["A"]/sh:.2f}, B ${nav["B"]/sh:.2f}, C ${nav["C"]/sh:.2f}, D ${nav["D"]/sh:.2f}')
    for wn, w in W.items():
        v = {lvl: sum(w[k] * m * nav[k] for k in 'ABCD') / sh for lvl, m in mm.items()}
        print(f'  weights {wn}: value at {mm["low"]:.2f}x ${v["low"]:.2f}, {mm["now"]:.2f}x ${v["now"]:.2f}, {mm["high"]:.2f}x ${v["high"]:.2f}')
        out[f'{route}|{wn}'] = v
    bear = mm['low'] * (nav['A'] - (0.2 + hp['dry_cut']) * DRY) / sh
    out[f'{route}|bear'] = bear
    print(f'  bear (strait reopens in Q1, dry bulk values -20%, multiple back to {mm["low"]:.2f}x): ${bear:.2f} ({bear/px-1:+.0%}); with 12 months of distributions {(bear+dist)/px-1:+.0%}')
print(f'12-month distributions on the model ${dist:.2f} ({dist/px:.1%}); bought after the 9 Dec ex-date ${dist-dec_div:.2f} ({(dist-dec_div)/px:.1%})')
out['dist12'] = dist; out['dist12_after_exdate'] = dist - dec_div
json.dump(out, open(os.path.join(HERE, '..', 'results', 'payoff_both_routes.json'), 'w'), indent=1)
# the target: Kalshi weights (the deeper market), each route at CMB.TECH's own price/NAV today, averaged.
k = 'Kalshi 25 Nov (Apr 1 12%, Jan 1 2028 33%)'
v = (out[f'route 1|{k}']['now'] + out[f'route 2|{k}']['now']) / 2
target = int(v * 2) / 2
best = (out[f'route 1|{k}']['high'] + out[f'route 2|{k}']['high']) / 2
low = (out[f'route 1|{k}']['low'] + out[f'route 2|{k}']['low']) / 2
bear = (out['route 1|bear'] + out['route 2|bear']) / 2
print(f'target: ${v:.2f} -> ${target:.2f} ({target/px-1:+.1%}); total return with distributions {(target+dist)/px-1:+.1%}, after the ex-date {(target+dist-dec_div)/px-1:+.1%}')
print(f'at the best multiple on each route ${best:.2f}: total {(best+dist)/px-1:+.1%}; at the lowest ${low:.2f}: total {(low+dist)/px-1:+.1%}; bear ${bear:.2f}: total {(bear+dist)/px-1:+.1%}')
d = {k2: (out[f'route 1|{k}']['now'] + out[f'route 2|{k}']['now']) for k2 in ['x']}
# the bull's best path: strait shut through 2027 (path D, Kalshi 67%), each route at today's multiple
pd = (mult['route 1']['now'] * (hp['D']['nav'] - gap) + mult['route 2']['now'] * hp['D']['nav']) / 2 / sh
print(f'path D (shut through 2027) at today\'s multiples: ${pd:.2f}, total {(pd+dist)/px-1:+.1%}')
print(f'(base case already has dry bulk values {hp["dry_cut"]:+.1%} by end-2027; the bear takes them to -20% in total)')
print(f'dry bulk values -20% = ${0.2*DRY:,.0f}m of NAV, ${0.2*DRY*mult["route 2"]["now"]/sh:.2f} a share at the route 2 multiple today')

# expected value: bull = best multiple on each route, base = today's multiple, bear = the bear case. 25/50/25.
cases = {'bull': best, 'base': v, 'bear': bear}
P3 = {'bull': .25, 'base': .50, 'bear': .25}
ev = sum(P3[k] * (cases[k] + dist) for k in cases) / px - 1
ev_x = sum(P3[k] * (cases[k] + dist - dec_div) for k in cases) / px - 1
rf, beta, erp = 4.91, 0.65, 5.0   # 10-year Treasury 24 Nov 2026 (Treasury; FRED 4.92 on 23 Nov); beta = 1y daily vs SPY; ERP is my assumption
coe = rf + beta * erp
print(f'expected 12-month total return (25/50/25): {ev:+.1%} before the ex-date, {ev_x:+.1%} after; cost of equity {coe:.1f}% (4.91% + 0.65 x 5.0%)')
for w in ((.35, .50, .15), (.25, .50, .25), (.15, .50, .35)):
    e = (w[0] * (best + dist) + w[1] * (v + dist) + w[2] * (bear + dist)) / px - 1
    print(f'  weights bull/base/bear {w[0]:.0%}/{w[1]:.0%}/{w[2]:.0%}: {e:+.1%}')
json.dump({**out, 'target': target, 'ev': ev, 'ev_after_ex': ev_x, 'coe': coe, 'best': best, 'base': v, 'bear_avg': bear, 'low': low}, open(os.path.join(HERE, '..', 'results', 'payoff_both_routes.json'), 'w'), indent=1)

# charter-mark sensitivity: 1 to 5 years left on the eight charters with no disclosed end date, instead of 3
wk = W['Kalshi 25 Nov (Apr 1 12%, Jan 1 2028 33%)']
mid_m = sum(wk[k] * hp[k]['marks'] for k in 'ABCD')
lo_m = sum(wk[k] * hp[k + '_marks_range'][0] for k in 'ABCD' if k + '_marks_range' in hp)
hi_m = sum(wk[k] * hp[k + '_marks_range'][1] for k in 'ABCD' if k + '_marks_range' in hp)
am = (mult['route 1']['now'] + mult['route 2']['now']) / 2
print(f'charter marks, Kalshi-weighted: ${mid_m:,.0f}m with 3 years assumed, ${lo_m:,.0f}m-${hi_m:,.0f}m with 1-5 years: target moves {(mid_m-hi_m)*am/sh:+.2f} to {(mid_m-lo_m)*am/sh:+.2f} a share')

# how much the Hormuz paths matter: each path on both routes at today's multiples, averaged
pv_ = {k: (mult['route 1']['now'] * (hp[k]['nav'] - gap) + mult['route 2']['now'] * hp[k]['nav']) / 2 / sh for k in 'ABCD'}
print('Hormuz paths at today\'s multiples: ' + ', '.join(f'{k} ${v:.2f}' for k, v in pv_.items()) + f'; range ${max(pv_.values())-min(pv_.values()):.2f}')

# rating robustness: the SELL line is cost of equity minus 5 points. with the bull weight held at 25%, what bear
# weight puts the expected return exactly on the line? and with bull = bear, what weight?
line = coe / 100 - 0.05
def evw(pb, pr):
    return ((pb * (best + dist) + (1 - pb - pr) * (v + dist) + pr * (bear + dist)) / px - 1)
lo, hi = 0.0, 0.75
for _ in range(60):
    mid = (lo + hi) / 2
    if evw(0.25, mid) > line: lo = mid
    else: hi = mid
print(f'SELL line {line:.1%}: with bull at 25%, the call is a SELL if the bear case is weighted above {lo:.1%}')
lo2, hi2 = 0.0, 0.5
for _ in range(60):
    mid = (lo2 + hi2) / 2
    if evw(mid, mid) > line: lo2 = mid
    else: hi2 = mid
print(f'with bull and bear weighted equally, it is a SELL above {lo2:.1%} each; base case alone {(v+dist)/px-1:+.1%}')
