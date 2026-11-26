# why the two company NAVs differ, from the loan documents. the value-adjusted ratio is a covenant measure: its
# "Excess Value" counts only vessels "fully owned by a member of the Group within pre-agreed segments". ships under
# sale-and-leaseback (legally owned by the lessor, still on CMB.TECH's balance sheet under IFRS), joint-venture ships
# and anything outside the agreed segments add nothing to route 1, but their broker value is in route 2.
from common import rows
for r in rows('covenant_definitions.csv'):
    print(f'{r["item"]}: {r["text"]}')
sh = 290.169769
gaps = {'2025-12-31': 8.29, '2026-06-30': 4.72, '2026-09-30': 5.66}
up2 = 12186 - 6780.215
for d, g in gaps.items():
    print(f'{d}: route 2 - route 1 = ${g:.2f} a share = ${g*sh:,.0f}m of ship value over book that the covenant measure leaves out')
rt = [(d, eq, ratio, fmv, vb, gg) for d, eq, ratio, fmv, vb, gg in [('2025-12-31', 2623.320, 0.442, 10686, 6323.773, 8.29), ('2026-06-30', 3120.994, 0.515, 11185, 6875.419, 4.72), ('2026-09-30', 3495.006, 0.581, 12186, 6780.215, 5.66)]]
ta = {'2025-12-31': 8405.574, '2026-06-30': 8827.889, '2026-09-30': 8730.076}
for d, eq, ratio, fmv, vb, gg in rt:
    u1 = (ratio * ta[d] - eq) / (1 - ratio); u2 = fmv - vb
    print(f'{d}: uplift on route 2 ${u2:,.0f}m, counted by the covenant ${u1:,.0f}m, left out {1-u1/u2:.0%}')
print('the leaseback deals fit the end-2025 peak, but nothing I can find in the Q1 or Q2 2026 releases (no refinancing or leaseback buy-back) explains the drop to about 30% by June. correction: the bridge was not repaid in Q4 2025. $122.5m was still drawn at 31 Dec 2025 and nil at 30 Jun 2026 (debt tables), and the $2bn facility was repriced in the same half. see covenant_timeline.py.')
g = 5.66 * sh
print(f'30 Sep: that is {g/up2:.0%} of the ${up2:,.0f}m total uplift. at the fleet-wide uplift ratio ({up2/12186:.0%} of value), it would take about ${g/(up2/12186):,.0f}m of ships ({g/(up2/12186)/12186:.0%} of the fleet) outside the definition')
print('known candidates: 20 ex-Golden Ocean bulkers put into sale-and-leaseback in Dec 2025, 4 Newcastlemaxes (2022, 2023), 8 Capesizes from 2015, JV Newcastlemaxes. the Dec 2025 deal lines up with the biggest gap ($8.29 at end-2025).')
print('so route 2 is the economic NAV (the leased ships come back to CMB.TECH through purchase obligations and options), and route 1 is the lenders\' measure.')
