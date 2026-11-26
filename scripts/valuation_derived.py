# the valuation again, with the ship-price drift taken from the charter test instead of chosen. valuation_simple.py
# assumed -2% a year forever. here the drift is what closes each segment's gap between price and charter value by the
# time a newbuild ordered today delivers (charter_test_curves.py, 3.7 years), applied to 2029 and the first part of
# 2030, then flat for ever. same cash flows, cost of equity, ROE slope and distributions as valuation_simple.py.
# then three checks a buyer of the stock would ask for: justified price-to-book against the peers, the balance sheet
# with the bulkers marked to what charters pay for, and my numbers against consensus.
import os, json, math
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda f: json.load(open(os.path.join(HERE, '..', 'results', f)))
ms, rw, ct = J('model_summary.json'), J('roe_windows.json'), J('charter_test_curves.json')
sh = 290.169769
px = {r['ticker']: float(r['close_2026_11_25']) for r in rows('prices_2026-11-25.csv')}
k, dist = (4.91 + 0.65 * 5) / 100, ms['dist12']
f27, f28, q4 = ms['fcf27'] / sh, ms['fcf28'] / sh, ms['fcf_q4_26'] / sh; book = ms['eq28'] / sh
pred = lambda e, g: (e * 3128 + g * 7017) / 10145
rc = rw['routine_common']
kk = (pred(rc['Euronav'], rc['Golden Ocean']) - pred(0.067, 0.068)) / ((98 / 76.2) ** (1 / 7) - 1)
r_of = lambda d: pred(0.067, 0.068) + kk * d
T_ON = 3.7 - (2 + 1 / 12)                      # years of the drift left after 2028: Dec 2026 + 3.7 years = Aug 2030
def value_today(d, kq=k, years=T_ON):
    cash = q4 / (1 + kq) ** 0.125 + f27 / (1 + kq) ** 0.625 + f28 / (1 + kq) ** 1.625
    disc = 1 / (1 + kq) ** 1.625
    rd, r0 = r_of(d), r_of(0.0)
    # end-2028 value of book that earns rd for `years`, then r0 for ever, all paid out: book plus the shortfalls
    s, t = 0.0, 0.0
    while t < years - 1e-9:
        dt = min(1.0, years - t); s += (rd - kq) * dt * book / (1 + kq) ** (t + dt); t += dt
    s += (r0 - kq) / kq * book / (1 + kq) ** years
    return cash + (book + s) * disc, cash, book * disc, s * disc
def er(d, kq=k, years=T_ON):
    v = value_today(d, kq, years)[0]; return (v * (1 + kq) - dist + dist) / px['CMBT'] - 1, v * (1 + kq) - dist

fl = ct['fleet']
out = {'drift': {}, 'sens': {}}
print(f'drift from the charter test: Compass curves {fl["drift_compass"]:+.1%}/yr, KOBC {fl["drift_kobc"]:+.1%}, Capesize on the FFA curve {fl["drift_ffa"]:+.1%} (bulkers alone {fl["drift_bulkers"]:+.1%})')
print(f'normal year: {r_of(fl["drift_compass"]):.1%} while the gap closes, {r_of(0):.1%} after, against a cost of equity of {k:.1%}')
for lab, d in (('Compass', fl['drift_compass']), ('KOBC', fl['drift_kobc']), ('FFA', fl['drift_ffa'])):
    e, p = er(d); out['drift'][lab] = {'d': d, 'er': e, 'p12': p}
    print(f'  {lab:8s} drift {d:+.1%}: 12-month value ${p:.2f}, expected total return {e:+.1%} vs SELL line {k-0.05:.1%}')
v, c, a, s = value_today(fl['drift_compass']); p12 = v * (1 + k) - dist; tgt = math.ceil(p12 * 20) / 20
out.update({'cash': c, 'book_pv': a, 'shortfall': s, 'today': v, 'p12': p12, 'target': tgt, 'er': (tgt + dist) / px['CMBT'] - 1})
print(f'published: cash ${c:.2f} + end-2028 book at the cost of equity ${a:.2f} + normal-year shortfall ${s:+.2f} = ${v:.2f} today; '
      f'a year at {k:.1%} ${v*k:+.2f}, distributions -${dist:.2f}: ${p12:.2f} -> target ${tgt:.2f}, expected {out["er"]:+.1%}')
# what the SELL needs: the drift line, and the same with the gap closing over twice as long
lo, hi = -0.10, 0.05
for _ in range(60):
    m = (lo + hi) / 2; lo, hi = (m, hi) if er(m)[0] < k - 0.05 else (lo, m)
out['sens']['drift_line'] = m
e_flat = er(0.0)[0]; e_long = er(fl['drift_compass'] / 2, years=T_ON * 2 + 3.7)[0]
out['sens'].update({'flat': e_flat, 'half_speed': e_long})
print(f'  the SELL holds for any drift below {m:+.2%} while the gap closes; flat ship prices {e_flat:+.1%}; the same gap closed at half the speed {e_long:+.1%}')
for kq in (0.075, 0.0843, 0.094):
    out['sens'][f'k{kq}'] = er(fl['drift_compass'], kq)[0]
    print(f'  cost of equity {kq:.2%}: expected {out["sens"][f"k{kq}"]:+.1%} vs SELL line {kq-0.05:.1%}')

# justified price-to-book. CMB.TECH's price over book, against what its normal year justifies (ROE over cost of
# equity, no growth, everything paid out) plus the cash it earns above that before 2029. the peers on the same line:
# their 2016-2025 reported return on equity (SEC XBRL; DHT 2017-2025) at the same cost of equity. a screen, not a
# valuation: tanker owners' prices carry this year's war earnings, which a ten-year average doesn't.
bk = {r['ticker']: r for r in rows('peer_book_2026-09-30.csv')}
hist = {}
for r in rows('peer_roe_xbrl.csv'): hist.setdefault(r['ticker'], {})[int(r['year'])] = (float(r['net_income_usd_m']), float(r['equity_end_usd_m']))
pb = {}
for t, b in bk.items():
    p_b = px[t] * float(b['shares_m']) / float(b['equity_usd_m'])
    if t == 'CMBT':
        roe = r_of(0.0)
    else:
        h = hist[t]; ys = [y for y in range(2016, 2026) if y in h and y - 1 in h]
        roe = sum(h[y][0] for y in ys) / sum((h[y][1] + h[y - 1][1]) / 2 for y in ys)
    pb[t] = {'pb': p_b, 'roe10': roe, 'justified': roe / k}
    print(f'{t:5s} price/book {p_b:.2f}; ten-year ROE {roe:.1%}; justified on that at {k:.1%}: {roe/k:.2f}; excess {p_b/(roe/k)-1:+.0%}')
cm = pb['CMBT']; near = (c - a * 0) / (float(bk['CMBT']['equity_usd_m']) / sh)
print(f'  CMB.TECH: of its {cm["pb"]:.2f}x book, {c/(float(bk["CMBT"]["equity_usd_m"])/sh):.2f}x is cash to 2028 and the rest is end-2028 book valued on the normal year')
out['pb'] = pb

# the balance sheet with the bulkers at charter value (Q3 2026 release; covenant per the 20-F and the $1.4bn bridge)
B = {r['line']: float(r['usd_thousands']) / 1000 for r in rows('balance_sheet_2026-09-30.csv')}
cr = {r['item']: r['value'] for r in rows('company_ratios.csv')}
debt = sum(B[x] for x in ('bank_loans_noncurrent', 'other_borrowings_noncurrent', 'lease_liabilities_noncurrent', 'bank_loans_current', 'other_borrowings_current', 'lease_liabilities_current'))
nd = debt - B['cash']; fmv = float(cr['fair_market_value_usd_m'])
cut = fl['bulker_value_above_charters'] * 7017
ltv0, ltv1 = nd / fmv, nd / (fmv - cut)
counted = 3764.0                                   # ship value over book that the covenant counts at 30 Sep (nav_covenant.py)
cov0 = (B['equity_owners'] + counted) / (B['total_assets'] + counted)
cov1 = (B['equity_owners'] + counted - cut) / (B['total_assets'] + counted - cut)
brk = (B['equity_owners'] + counted - 0.30 * (B['total_assets'] + counted)) / 0.70
capex_left = sum(float(r['usd_m']) for r in rows('capex_schedule.csv'))
print(f'net debt ${nd:,.0f}m; loan-to-value {ltv0:.0%} on broker values (${fmv:,.0f}m), {ltv1:.0%} with the bulkers ${cut:,.0f}m lower at charter value')
print(f'covenant (value-adjusted equity / assets, floor 30% from 2027): {cov0:.0%} on my rebuild (company reports {float(cr["value_adjusted_equity_to_total_assets"]):.1%}), '
      f'{cov1:.0%} at charter value; it takes ${brk:,.0f}m off ship values, {brk/7017:.0%} of the bulker fleet, to reach 30%')
print(f'capex still to pay Q4 2026 to Q2 2029: ${capex_left:,.0f}m; liquidity ${float(cr["liquidity_usd_m"]):,.0f}m (Q3 slides)')
fcf12 = ms['fcf_q4_26'] + 0.75 * ms['fcf27']; proceeds = 160.48 + 74.3 + 56.9
print(f'next 12 months: free cash flow about ${fcf12:,.0f}m (${fcf12-proceeds:,.0f}m without the Q4 sale proceeds) against ${dist*sh:,.0f}m of distributions, '
      f'{(fcf12-proceeds)/(dist*sh):.1f}x covered without the sales')
out['bs'] = {'nd': nd, 'ltv': ltv0, 'ltv_charter': ltv1, 'cov': cov0, 'cov_charter': cov1, 'cov_break': brk, 'capex_left': capex_left, 'cover_ex_sales': (fcf12 - proceeds) / (dist * sh)}

# against consensus
cs = {r['item']: r for r in rows('consensus_2026-11.csv')}
for y, mine in ((2027, ms['fy27_eps']), (2028, ms['fy28_eps'])):
    c_ = float(cs[f'consensus_eps_{y}']['value']); print(f'{y} EPS: mine ${mine:.2f}, consensus ${c_:.2f} ({mine/c_-1:+.0%})')
print(f'average target {cs["target_avg_sp_global"]["value"]} ({cs["target_avg_sp_global"]["source"]})')
json.dump(out, open(os.path.join(HERE, '..', 'results', 'valuation_derived.json'), 'w'), indent=1)

# how much of the bulker fleet is on time charter (Q3 2026 charter days, model.py; 41 Newcastlemax, 37 Capesize,
# 30 Kamsarmax/Panamax for 92 days)
tc_days = {'Newcastlemax': 24, 'Capesize': 435, 'Kamsarmax/Panamax': 286}
print(f'Q3 2026 bulker days on time charter: {sum(tc_days.values())} of {108*92}, {sum(tc_days.values())/(108*92):.1%} (Newcastlemax {24/(41*92):.1%})')
