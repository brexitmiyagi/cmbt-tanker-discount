import math
# the rating, done so the target and the rating can't disagree. the 12-month target is a price, so each method has
# to produce a 12-month price, probability-weighted, and the expected total return is that price plus 12 months of
# distributions over today's price. the old version averaged the asset view's base case with a DCF value today, and
# the target plus distributions came out above the SELL line it was meant to support.
# rating rule: expected 12-month total return at least 5 points below the cost of equity is a SELL, at least 5 points
# above is a BUY. targets rounded to the nearest 25 cents, never in the direction of the call.
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
R = lambda f: json.load(open(os.path.join(HERE, '..', 'results', f)))
ms, hp, rw = R('model_summary.json'), R('payoff_both_routes.json'), R('roe_windows.json')
sh, px = 290.169769, 17.54
dist = hp['dist12']
f27, f28, q4 = ms['fcf27'] / sh, ms['fcf28'] / sh, ms['fcf_q4_26'] / sh
book = ms['eq28'] / sh

# asset view: bull at the best multiple of the past year, base at today's, bear = reopening in Q1, dry bulk values
# down 20% in total, multiple back to its low (payoff_both_routes.py). weights 25/50/25.
w = (0.25, 0.50, 0.25)
asset_px = w[0] * hp['best'] + w[1] * hp['base'] + w[2] * hp['bear_avg']
print(f'asset view: bull ${hp["best"]:.2f}, base ${hp["base"]:.2f}, bear ${hp["bear_avg"]:.2f} -> probability-weighted 12-month price ${asset_px:.2f}, total return {(asset_px+dist)/px-1:+.1%}')
print(f'  (the old target used the base case, ${hp["base"]:.2f}; with ${dist:.2f} of distributions that alone is {(hp["base"]+dist)/px-1:+.1%})')

def dcf(r, k):
    pv3 = q4 / (1 + k) ** 0.125 + f27 / (1 + k) ** 0.625 + f28 / (1 + k) ** 1.625
    return pv3 + (r * book / k) / (1 + k) ** 1.625
def dcf_px12(r, k):   # a value today grows at the cost of equity for a year, and the distributions leave the share
    return dcf(r, k) * (1 + k) - dist

fleet_t, fleet_d = 3128, 7017   # tanker and dry bulk fleet value, $m, 30 Sep 2026
pred = lambda e, g: (e * fleet_t + g * fleet_d) / (fleet_t + fleet_d)
rc = rw['routine_common']
cases = {
    'predecessors, all gains out (v13)': pred(0.067, 0.068),
    'predecessors, routine gains in': pred(rc['Euronav'], rc['Golden Ocean']),
    'three companies, routine gains in': sum(rc.values()) / 3,
    'Star Bulk, routine gains in': rc['Star Bulk'],
}
coe = {'beta 0.52 (18 months daily)': 4.91 + 0.52 * 5, 'beta 0.65 (1 year daily, v13)': 4.91 + 0.65 * 5,
       'beta 0.89 (18 months weekly)': 4.91 + 0.89 * 5}
out = {}
print('\n12-month target and rating, 50/50 asset view and DCF, by normal-year return and cost of equity:')
for kl, kv in coe.items():
    k = kv / 100
    print(f' cost of equity {kv:.1f}% ({kl}): SELL below {kv-5:.1f}%, BUY above {kv+5:.1f}%')
    for cl, r in cases.items():
        p12 = (asset_px + dcf_px12(r, k)) / 2
        er = (p12 + dist) / px - 1
        rating = 'SELL' if er < k - 0.05 else 'BUY' if er > k + 0.05 else 'between the lines'
        out[f'{kl}|{cl}'] = {'r': r, 'k': k, 'dcf_today': dcf(r, k), 'dcf_px12': dcf_px12(r, k), 'target': p12, 'er': er, 'rating': rating}
        print(f'   {cl:36s} {r:.1%}: DCF ${dcf(r,k):.2f} today, ${dcf_px12(r,k):.2f} in 12 months; target ${p12:.2f} -> {er:+.1%}, {rating}')

# what the price needs, in normal-year return on end-2028 book, at each cost of equity
for kl, kv in coe.items():
    k = kv / 100
    pv3 = q4 / (1 + k) ** 0.125 + f27 / (1 + k) ** 0.625 + f28 / (1 + k) ** 1.625
    need = (px - pv3) * (1 + k) ** 1.625 * k / book
    beat = sum(1 for x in rw['routine'] if x >= need) / len(rw['routine'])
    print(f'cost of equity {kv:.1f}%: the price needs {need:.1%} on end-2028 book; {beat:.0%} of the 17 eight-year windows (routine gains kept) beat that')

# the central case and the SELL/BUY break-evens on it
k = coe['beta 0.65 (1 year daily, v13)'] / 100
c = out['beta 0.65 (1 year daily, v13)|predecessors, routine gains in']
print(f'\ncentral: predecessors with routine gains {c["r"]:.1%}, cost of equity {k:.1%}: target ${c["target"]:.2f} (rounded ${round(c["target"]*4)/4:.2f}), expected total return {c["er"]:+.1%}, {c["rating"]}')
def r_for(er_target):
    lo, hi = -0.05, 0.25
    for _ in range(60):
        m = (lo + hi) / 2
        e = ((asset_px + dcf_px12(m, k)) / 2 + dist) / px - 1
        lo, hi = (m, hi) if e < er_target else (lo, m)
    return m
print(f'SELL needs a normal-year return below {r_for(k-0.05):.1%}; BUY needs above {r_for(k+0.05):.1%}')
json.dump(out, open(os.path.join(HERE, '..', 'results', 'rating.json'), 'w'), indent=1)

# the published call, on the strict basis: no sale gains in the normal year (all out, as in roe_windows 'adjusted'),
# cost of equity 8.2%. reasoning for the strict basis is in the post: the predecessors' routine gains came from older
# ships bought over a decade of rising prices; CMB.TECH's book is now mostly newbuilds bought at today's prices.
s = out['beta 0.65 (1 year daily, v13)|predecessors, all gains out (v13)']
t = s['target']
t_pub = math.ceil(t * 20) / 20          # nearest 5 cents, rounded up, against the call
er_pub = (t_pub + dist) / px - 1
print(f'\npublished: SELL on the strict basis. target ${t:.2f} -> ${t_pub:.2f} (rounded up, against the call), expected total return {er_pub:+.1%} vs SELL line {k-0.05:.1%}')
print(f'  12-month prices: asset view ${asset_px:.2f}, DCF ${s["dcf_px12"]:.2f}; distributions ${dist:.2f}')
n_sell = sum(1 for v in out.values() if v['rating'] == 'SELL'); n_buy = sum(1 for v in out.values() if v['rating'] == 'BUY')
print(f'  across the {len(out)} combinations above: {n_sell} SELL, {n_buy} BUY, {len(out)-n_sell-n_buy} between the lines')
# how much bear weight the published call needs, with bull held at 25%
def er_w(wb):
    ap = 0.25 * hp['best'] + (0.75 - wb) * hp['base'] + wb * hp['bear_avg']
    return ((ap + s['dcf_px12']) / 2 + dist) / px - 1
lo, hi = 0.0, 0.75
for _ in range(60):
    m = (lo + hi) / 2
    lo, hi = (m, hi) if er_w(m) > k - 0.05 else (lo, m)
print(f'  the call stays a SELL while the bear case carries more than {m:.1%} (bull at 25%); I use 25%, Kalshi gives a reopening before 2028 about 33%')

# after gain_decomposition.py: the strict basis is no longer a choice. the remaining soft inputs, at their midpoints:
kmid = (coe['beta 0.52 (18 months daily)'] + coe['beta 0.89 (18 months weekly)']) / 200
pm = (asset_px + dcf_px12(0.068, kmid)) / 2
erm = (pm + dist) / px - 1
print(f'\ncost of equity at the middle of the beta range ({kmid:.2%}): strict case target ${pm:.2f}, expected {erm:+.1%} vs SELL line {kmid-0.05:.1%}')
for wb in (0.216, 0.25, 0.33):
    ap = 0.25 * hp['best'] + (0.75 - wb) * hp['base'] + wb * hp['bear_avg']
    e = ((ap + s['dcf_px12']) / 2 + dist) / px - 1
    print(f'  bear weight {wb:.0%} (bull 25%) at 8.2%: expected {e:+.1%}')
lo, hi = -0.05, 0.25
for _ in range(60):
    m = (lo + hi) / 2
    e = ((asset_px + dcf_px12(m, kmid)) / 2 + dist) / px - 1
    lo, hi = (m, hi) if e < kmid - 0.05 else (lo, m)
print(f'  at {kmid:.2%} the SELL needs a normal-year return below {m:.1%}')

# v16: the published case. normal-year return = no sale gains (6.8%) plus forward sale gains scaled by the drift in
# ship prices (forward_gains.py), with prices drifting down 2% a year from decade highs. charter book: actual.
_rc = rw['routine_common']; _pr = (_rc['Euronav'] * 3128 + _rc['Golden Ocean'] * 7017) / 10145
_kk = (_pr - pred(0.067, 0.068)) / ((98 / 76.2) ** (1 / 7) - 1)
r_pub = pred(0.067, 0.068) + _kk * (-0.02)
p12 = (asset_px + dcf_px12(r_pub, k)) / 2
t_up = math.ceil(p12 * 20) / 20
print(f'\nv16 published: normal-year return {r_pub:.2%} (6.8% with no sale gains, ship prices -2% a year); DCF ${dcf(r_pub, k):.2f} today, ${dcf_px12(r_pub, k):.2f} in 12 months;'
      f' asset view ${asset_px:.2f}; target ${p12:.2f} -> ${t_up:.2f} (rounded up), expected {(t_up+dist)/px-1:+.1%} vs SELL line {k-0.05:.1%}')
def er_w2(wb):
    ap = 0.25 * hp['best'] + (0.75 - wb) * hp['base'] + wb * hp['bear_avg']
    return ((ap + dcf_px12(r_pub, k)) / 2 + dist) / px - 1
lo, hi = 0.0, 0.75
for _ in range(60):
    m = (lo + hi) / 2
    lo, hi = (m, hi) if er_w2(m) > k - 0.05 else (lo, m)
print(f'  v16: the SELL holds while the bear case carries more than {m:.1%} (bull 25%)')
for kq in (0.075, kmid, 0.094):
    pp = (asset_px + dcf_px12(r_pub, kq)) / 2
    print(f'  v16 at cost of equity {kq:.2%}: expected {(pp+dist)/px-1:+.1%} vs SELL line {kq-0.05:.1%}')
print(f'  v16 at Kalshi\'s 33% bear weight (bull 25%): expected {er_w2(0.33):+.1%}')

# v17. two changes. (1) the asset view carries the same ship-price drift as the cash view: end-2027 is 15 months from
# the 30 Sep 2026 marks, so tanker values in path D (strait shut, values held flat) take the drift; paths A-C already
# cut tankers 15-31%, and dry bulk already falls 2.7% by end-2027 in every path (hormuz_paths.py), so dry bulk only
# takes whatever drift goes beyond that. (2) bear weight from the market: Kalshi 33% for normal traffic before 2028,
# which in my paths means tankers back to pre-war values by end-2027 (A or B). bull stays 25%, base takes the rest.
# the drift itself now comes from earnings_implied_value.py: closing the gap between price and earnings-implied value
# over 10 to 20 years gives -4.5% to -2.3% a year for CMB.TECH's fleet mix. I publish -2%, below that range.
hpj = json.load(open(os.path.join(HERE, '..', 'results', 'hormuz_paths.json')))
ev = json.load(open(os.path.join(HERE, '..', 'results', 'earnings_implied_value.json')))
TANK, DRYV = 3128.0, 7017.0
wD = 0.67   # Kalshi weight on path D in payoff_both_routes.py
am_now, am_high = (0.70 + 0.57) / 2, (0.76 + 0.62) / 2
def asset_v17(drift, wts):
    cum = 1 - (1 + drift) ** 1.25
    dry_extra = max(0.0, cum - abs(hpj['dry_cut']))
    cut_base = (wD * TANK * cum + DRYV * dry_extra) * am_now / sh
    cut_best = (wD * TANK * cum + DRYV * dry_extra) * am_high / sh
    b, s_, br = hp['best'] - cut_best, hp['base'] - cut_base, hp['bear_avg']
    return wts[0] * b + wts[1] * s_ + wts[2] * br, (b, s_, br)
def r_of(drift): return pred(0.067, 0.068) + _kk * drift
def er17(drift, wts, kq=k):
    a, _ = asset_v17(drift, wts)
    p = (a + dcf_px12(r_of(drift), kq)) / 2
    return p, (p + dist) / px - 1
W17 = (0.25, 0.42, 0.33)
a17, (b17, s17, br17) = asset_v17(-0.02, W17)
p17, e17 = er17(-0.02, W17)
t17 = math.ceil(p17 * 20) / 20
print(f'\nv17 published: drift -2.0% a year (evidence range {ev["fleet_drift_20y"]:+.1%} to {ev["fleet_drift"]:+.1%}), weights 25/42/33 (Kalshi bear)')
print(f'  asset view: bull ${b17:.2f}, base ${s17:.2f}, bear ${br17:.2f} -> ${a17:.2f}; DCF in 12 months ${dcf_px12(r_of(-0.02), k):.2f}')
print(f'  target ${p17:.2f} -> ${t17:.2f} (rounded up), expected {(t17+dist)/px-1:+.1%} vs SELL line {k-0.05:.1%}')
for lab, d_ in (('flat', 0.0), ('-2.3% (20-year close)', ev['fleet_drift_20y']), ('-4.5% (10-year close)', ev['fleet_drift']), ('+3.7% (2016-23)', (98 / 76.2) ** (1 / 7) - 1)):
    for wl, ww in (('25/42/33', W17), ('25/50/25', (0.25, 0.5, 0.25))):
        print(f'  v17 drift {lab:22s} weights {wl}: expected {er17(d_, ww)[1]:+.1%}')
for kq in (0.075, kmid, 0.094):
    print(f'  v17 at cost of equity {kq:.2%}: expected {er17(-0.02, W17, kq)[1]:+.1%} vs SELL line {kq-0.05:.1%}')
lo, hi = -0.06, 0.06
for _ in range(60):
    m = (lo + hi) / 2
    lo, hi = (m, hi) if er17(m, W17)[1] < k - 0.05 else (lo, m)
print(f'  v17: the SELL holds for any drift below {m:+.2%} a year')
lo, hi = 0.0, 0.75
for _ in range(60):
    m = (lo + hi) / 2
    lo, hi = (m, hi) if er17(-0.02, (0.25, 0.75 - m, m))[1] > k - 0.05 else (lo, m)
print(f'  v17: at -2% drift the SELL holds while the bear carries more than {m:.1%}')
print(f'  v17 at -2% drift, weights 25/50/25: expected {er17(-0.02, (0.25, 0.5, 0.25))[1]:+.1%}')
