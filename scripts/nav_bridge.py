# what is the company worth if you mark the ships to market, using CMB.TECH's own numbers?
# two routes: (1) back out the value uplift from the 58.1% value-adjusted equity ratio on slide 5,
# (2) take the $12.2bn broker FMV on slide 4 against the book value of the vessels.
from common import kv, rows
bs = kv('balance_sheet_2026-09-30.csv')
ratio = {r['item']: float(r['value']) for r in rows('company_ratios.csv')}
mkt = {r['item']: float(r['value']) for r in rows('market_2026-11-24.csv')}
fmv = {r['segment']: float(r['fmv_usd_m']) for r in rows('fleet_fair_market_value_2026-09-30.csv')}

A = bs['total_assets'] / 1000
E = bs['equity_owners'] / 1000
sh = bs['shares_ex_treasury'] / 1e6
r = ratio['value_adjusted_equity_to_total_assets']
debt = sum(bs[k] for k in ['bank_loans_noncurrent', 'other_borrowings_noncurrent', 'bank_loans_current', 'other_borrowings_current',
                           'lease_liabilities_noncurrent', 'lease_liabilities_current']) / 1000
net_debt = debt - bs['cash'] / 1000

print(f'book equity ${E:,.1f}m = ${E/sh:.2f} a share on {sh:,.2f}m shares (ex treasury)')
print(f'gross debt incl leases ${debt:,.1f}m, cash ${bs["cash"]/1000:,.1f}m, net debt ${net_debt:,.1f}m')

# route 1: (E + U) / (A + U) = r  ->  U = (r*A - E) / (1 - r)
U = (r * A - E) / (1 - r)
nav1 = E + U
print(f'route 1, value-adjusted equity {r:.1%}: uplift ${U:,.1f}m, NAV ${nav1:,.1f}m = ${nav1/sh:.2f} a share')

# route 2: broker FMV of the ships on the water vs their book value
fmv_total = sum(fmv.values())
U2 = fmv_total - bs['vessels'] / 1000
nav2 = E + U2
print(f'route 2, broker FMV ${fmv_total:,.0f}m vs vessels at book ${bs["vessels"]/1000:,.1f}m: uplift ${U2:,.1f}m, NAV ${nav2:,.1f}m = ${nav2/sh:.2f} a share')

price = mkt['cmbt_close']
cap = price * sh
print(f'market cap at ${price:.2f}: ${cap:,.1f}m; price/NAV route 1 {price/(nav1/sh):.2f}, route 2 {price/(nav2/sh):.2f}')

tank = fmv['Crude tankers']
for lab, nav in (('route 1', nav1), ('route 2', nav2)):
    gap = nav - cap
    print(f'{lab}: gap to market cap ${gap:,.1f}m = {gap/tank:.1%} of the ${tank:,.0f}m tanker FMV')
for c in rows('secondhand_15yr_values.csv'):
    if c['ten_year_avg_usd_m']:
        t, a = float(c['today_usd_m']), float(c['ten_year_avg_usd_m'])
        print(f'15-year-old {c["class"]}: ${t:.0f}m today vs ${a:.0f}m 10-year average, {a/t-1:.1%} to get back to average')
# NAV if the tankers alone go back to decade-average values (use the VLCC discount, the bigger one)
vl = rows('secondhand_15yr_values.csv')[0]
cut = 1 - float(vl['ten_year_avg_usd_m']) / float(vl['today_usd_m'])
for k in (cut, cut / 2):
    n = nav1 - tank * k
    print(f'route 1 NAV with tankers marked down {k:.1%}: ${n:,.1f}m = ${n/sh:.2f} a share')
# what a dry bulk markdown does to route 1
for k in (0.10, 0.20, 0.30):
    n = nav1 - fmv['Dry bulk'] * k
    print(f'route 1 NAV with dry bulk marked down {k:.0%} (tankers at broker value): ${n/sh:.2f} a share')
both = nav1 - tank * cut - fmv['Dry bulk'] * 0.20
print(f'route 1 NAV with tankers at decade average and dry bulk down 20%: ${both/sh:.2f} a share')
