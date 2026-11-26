# how I get to $21, and how much room the loan covenants leave.
from common import rows, kv
bs = kv('balance_sheet_2026-09-30.csv')
sh = bs['shares_ex_treasury'] / 1e6
nav1, nav2, uplift = 7259.1, 8900.8, 3764.1   # from nav_bridge.py
assets_va = bs['total_assets'] / 1000 + uplift
fleet_fmv = sum(float(r['fmv_usd_m']) for r in rows('fleet_fair_market_value_2026-09-30.csv'))
print(f'value-adjusted assets ${assets_va:,.1f}m, equity ${nav1:,.1f}m, ratio {nav1/assets_va:.1%}')
for k in (0.275, 0.30):
    x = (nav1 - k * assets_va) / (1 - k)
    print(f'covenant {k:.1%}: ship values can fall ${x:,.0f}m before it binds = {x/fleet_fmv:.0%} of the ${fleet_fmv:,.0f}m fleet')
# Q4: half of the floor profit stays in the company, the Q3 distribution goes out
q4, payout, q3dist = 635.5, 0.5, 0.65
net = q4 * (1 - payout) - q3dist * sh
print(f'Q4 retained ${q4*(1-payout):,.1f}m less Q3 distribution ${q3dist*sh:,.1f}m = ${net:,.1f}m = ${net/sh:+.2f} a share of NAV')
p = {r['item']: float(r['value']) for r in rows('peer_star_bulk.csv')}
disc = p['close_2026_11_24'] * p['diluted_shares_m'] / (p['fleet_market_value_usd_m'] - p['net_debt_usd_m'])
print(f'at Star Bulk price/NAV {disc:.2f}: route 1 ${disc*nav1/sh:.2f}, route 2 ${disc*nav2/sh:.2f}, midpoint ${disc*(nav1+nav2)/2/sh:.2f}')
print(f'withholding: $0.21 interim at 30% Belgian tax = ${0.21*0.30:.3f} withheld, $0.65 nets ${0.65-0.21*0.30:.3f} before any treaty claim')
