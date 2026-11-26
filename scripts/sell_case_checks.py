# the rest of what a SELL on CMB.TECH has to answer, all off the published case (house_view_checks.py):
#  - one blended expected return: Hormuz odds from Kalshi and Polymarket, tanker sales at the pace since the war
#  - what a short actually makes: price move, distributions it pays, and the bid tail
#  - my 2028 EPS against the whole consensus range
#  - the tankers on my 2028 rates: if the three-year charter is too high, are tankers overpriced too?
#  - the chemical, container and offshore ships my model holds in one flat line
import os, json, subprocess, sys, tempfile
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda f: json.load(open(os.path.join(HERE, '..', 'results', f)))
hv, fb = J('house_view_checks.json'), J('forward_bias.json')
sh, px, k, dist = 290.169769, 17.72, (4.91 + 0.65 * 5) / 100, J('model_summary.json')['dist12']
base_er = hv['cases']['my 2028 (published)']['er']
reopen_er = hv['reopening, tanker deck halves']['er']
per4 = hv['tanker_sales']['dv']                        # value of four sales, $ a share
pts_per_dollar = (1 + k) / px
out = {}

# Hormuz: normal traffic before 2028, Kalshi 32.5% (mid of 0.31/0.34) and Polymarket 34.5%; I use the average
p_open = (0.325 + 0.345) / 2
# tanker sales since the war started (data/tanker_sales_2026.csv, before_war = no): six ships, 19 May to 13 Oct 2026
sales = [r for r in rows('tanker_sales_2026.csv') if r['before_war'] == 'no']
n_sold = sum(int(r['type'].split(' x')[1]) if ' x' in r['type'] else 1 for r in sales)
# after Q4 deliveries: 17 crude tankers; 9 Suezmaxes are on time charter (IR, 26 Nov 2026), so 8 are free to sell
free = 17 - 9
for n in (4, free):
    sale_pts = per4 / 4 * n * pts_per_dollar
    blend = p_open * reopen_er + (1 - p_open) * (base_er + sale_pts)      # no sales at war prices if the strait reopens
    out[f'blend_{n}'] = blend
    print(f'blended expected return, {p_open:.1%} reopening, {n} tanker sales if it stays shut: {blend:+.1%} (SELL line {k-0.05:.1%})')
print(f'  pace since the war: {n_sold} tankers sold in five months; 8 of the 17 left after Q4 are not on time charter')

# the short: at the target, the stock falls $2.02 but the short pays $2.35 of distributions
tgt = 15.70
pnl_tgt = px - tgt - dist
pnl_bid = px - 25.02 - dist * 0.5
out['short'] = {'at_target': pnl_tgt, 'at_bid_half_year': pnl_bid}
print(f'short at $17.72: at the ${tgt:.2f} target it makes ${px-tgt:.2f} on price and pays ${dist:.2f} of distributions, net ${pnl_tgt:+.2f} ({pnl_tgt/px:+.1%}) before borrow; '
      f'a bid at $25.02 six months in costs ${-pnl_bid:.2f} ({pnl_bid/px:+.1%})')

# 2028 EPS against the whole consensus range (Seeking Alpha, 25 Nov 2026: 3 analysts, $1.09 to $2.44, mean $1.91)
mine = hv['eps28_bridge']['mine']
print(f'2028 EPS: mine ${mine:.2f}, below the lowest of three estimates ($1.09); mean $1.91, high $2.44; on market prices ${hv["eps28_bridge"]["market_prices"]:.2f}')

# the tanker loop: the charter test again, with years 2 to 3.7 at my 2028 rate instead of the three-year charter
S = {r['segment']: r for r in rows('segments_2026-11-20.csv')}
op = {r['segment'].split()[0]: float(r['opex']) for r in rows('fixtures.csv')}
ct = J('charter_test_curves.json')
mine28 = {'VLCC': (122500 + 37786.27) / 2, 'Suezmax': (77500 + 32776.91) / 2}
def worth(seg, y1, rest, nb, d, wait=3.7, r=0.08):
    pv, t, i = 0.0, 0.0, 0
    while t < wait - 1e-9:
        dtt = min(1.0, wait - t); x = y1 if i == 0 else rest
        pv += (x - op[seg]) * 365 * 0.97 * dtt / 1e6 / (1 + r) ** (t + dtt / 2); t += dtt; i += 1
    return pv + nb * d ** ((5 + wait) / 5) / (1 + r) ** wait
for seg in ('VLCC', 'Suezmax'):
    pxs, nb, y1 = float(S[seg]['five_year_usd_m']), float(S[seg]['newbuild_usd_m']), float(S[seg]['tc_1y'])
    w = worth(seg, y1, mine28[seg], nb, ct['curves']['Compass'][seg])
    out[f'tanker_{seg}'] = {'worth': w, 'premium': pxs / w - 1}
    print(f'{seg}: on my 2028 rate after year one (${mine28[seg]:,.0f}), a five-year-old is worth ${w:.1f}m against ${pxs:.1f}m, price {pxs/w-1:+.0%} above it '
          f'(on the three-year charter: {pxs/ct["segments"][seg]["Compass_worth"]-1:+.0%})')

# the other segments: chemicals, containers, offshore. broker value 30 Sep 2026 (fleet_fair_market_value_2026-09-30.csv)
fmv = {r['segment']: float(r['fmv_usd_m']) for r in rows('fleet_fair_market_value_2026-09-30.csv')}
other = fmv['Container'] + fmv['Chemical'] + fmv['Offshore energy']
total = sum(fmv.values())
nd = 4870.3
# what everything outside tankers and dry bulk earned in Q3 2026: the model's calibrated residual, $12.7m a quarter,
# which also carries unallocated G&A and JV income, so it understates the segments themselves
resid_q = 12.7
earn_val = resid_q * 4 / k
fmv_val = other * (1 - nd / total)                  # broker value less a pro-rata share of net debt
out['other'] = {'fmv': other, 'share': other / total, 'earnings_value': earn_val, 'broker_value_less_debt': fmv_val}
gap = (fmv_val - earn_val) / sh
print(f'chemicals, containers, offshore: ${other:,.0f}m of broker value, {other/total:.0%} of the fleet. on what they earned in Q3 (with unallocated costs) '
      f'${earn_val:,.0f}m (${earn_val/sh:.2f} a share); at broker value less pro-rata debt ${fmv_val:,.0f}m (${fmv_val/sh:.2f}). '
      f'if the second is right, {gap:+.2f} a share, {gap*pts_per_dollar*100:+.1f} points on the expected return')
print('  not in the model: 8 chemical, 4 CSOV, 3 CTV and 1 container newbuilds (Q3 2026 release); CSOVs 100% fixed at 26% utilisation in Q4 to date')
json.dump(out, open(os.path.join(HERE, '..', 'results', 'sell_case_checks.json'), 'w'), indent=1)
