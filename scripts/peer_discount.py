# cross-check: dry bulk stocks trade below NAV too. Star Bulk is the cleanest listed comparable that
# gives a fleet market value and net debt on its own call. I value CMB.TECH's non-tanker NAV at Star Bulk's
# discount and see what the market is left paying for the tankers.
# Star Bulk NAV here = fleet value minus net debt, nothing else, which is rough but on the same basis for both.
from common import rows, kv
p = {r['item']: float(r['value']) for r in rows('peer_star_bulk.csv')}
bs = kv('balance_sheet_2026-09-30.csv')
fmv = {r['segment']: float(r['fmv_usd_m']) for r in rows('fleet_fair_market_value_2026-09-30.csv')}
mkt = {r['item']: float(r['value']) for r in rows('market_2026-11-24.csv')}
sh = bs['shares_ex_treasury'] / 1e6
sb_nav = p['fleet_market_value_usd_m'] - p['net_debt_usd_m']
sb_cap = p['close_2026_11_24'] * p['diluted_shares_m']
disc = sb_cap / sb_nav
print(f'Star Bulk: fleet ${p["fleet_market_value_usd_m"]:,.0f}m less net debt ${p["net_debt_usd_m"]:,.0f}m = NAV ${sb_nav:,.0f}m; market cap ${sb_cap:,.0f}m; price/NAV {disc:.2f}')
nav1 = 7259.1  # route 1 from nav_bridge.py
tank = fmv['Crude tankers']
rest = nav1 - tank
cap = mkt['cmbt_close'] * sh
implied = cap - disc * rest
print(f'CMB.TECH NAV ex tankers ${rest:,.1f}m at Star Bulk price/NAV {disc:.2f} = ${disc*rest:,.0f}m')
print(f'left for the tankers in a ${cap:,.0f}m market cap: ${implied:,.0f}m = {implied/tank:.0%} of the ${tank:,.0f}m broker value')
print(f'CMB.TECH whole-company NAV at Star Bulk price/NAV: route 1 ${disc*nav1/sh:.2f}, route 2 ${disc*8900.8/sh:.2f} a share')
