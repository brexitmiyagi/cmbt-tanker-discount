# the mechanism behind "no sale gains in the normal year": how much of the fleet was bought at today's prices.
# fleet lists from the 2025 20-F (dry bulk as of 1 April 2026) and the tanker list in fleet_crude_tankers.csv.
from common import rows
db = rows('fleet_dry_bulk_20F.csv')
new_db = sum(1 for r in db if int(r['built']) >= 2023)
print(f'dry bulk: {new_db} of {len(db)} ships built 2023-2026')
ct = [r for r in rows('fleet_crude_tankers.csv') if 'sold' not in r['status_25_nov_2026'] and r['type'] in ('VLCC', 'Suezmax') and r['built']]
vl = [r for r in ct if r['type'] == 'VLCC' and not r['vessel'].startswith('(')]
sz = [r for r in ct if r['type'] == 'Suezmax']
print(f'VLCCs still owned: ' + ', '.join(f'{r["vessel"]} ({r["built"]})' for r in vl) + ' -- every one a 2025-27 delivery')
print(f'Suezmaxes still owned: {len(sz)}, of which built 2022 or later: {sum(1 for r in sz if r["built"][:4] >= "2022")}')
cap = sum(float(r['usd_m']) for r in rows('capex_schedule.csv'))
auc = float(next(r for r in rows('balance_sheet_2026-09-30.csv') if r['line'] == 'assets_under_construction')['usd_thousands']) / 1000
print(f'assets under construction at 30 Sep 2026 ${auc:,.0f}m, plus ${cap:,.0f}m of capex scheduled Q4 2026 to Q2 2029')
nb = next(r for r in rows('secondhand_15yr_values.csv') if r['class'] == 'VLCC newbuild')
print(f'a VLCC newbuild costs ${nb["today_usd_m"]}m today (CMB.TECH Q3 2026 release); the VLCCs sold in 2023-24 had implied costs of')
print('about $77m to $100m (gain_decomposition.py). sale gains on the new ships need resale prices to stay above what they cost.')
