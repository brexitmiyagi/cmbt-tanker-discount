# the two company NAVs don't agree, and the gap moves around. route 1 = backed out of the value-adjusted equity
# ratio on slide 5; route 2 = book equity + broker fleet value (slide 4) - vessels at book. same dates, same balance sheet.
from common import rows
sh = 290.169769
data = [  # date, total assets, equity, ratio, fleet value (broker), vessels at book, assets under construction, close
    ('2025-12-31', 8405.574, 2623.320, 0.442, 10686, 6323.773, 739.373, 9.65),
    ('2026-06-30', 8827.889, 3120.994, 0.515, 11185, 6875.419, 532.660, 13.99),
    ('2026-09-30', 8730.076, 3495.006, 0.581, 12186, 6780.215, 572.189, 18.93),
]
for d, A, E, k, F, V, auc, px in data:
    u = (k * A - E) / (1 - k)
    n1, n2 = (E + u) / sh, (E + F - V) / sh
    print(f'{d}: route 1 ${n1:.2f}, route 2 ${n2:.2f}, gap ${n2-n1:.2f} a share (${(n2-n1)*sh:,.0f}m); price/NAV route 1 {px/n1:.2f}x, route 2 {px/n2:.2f}x; newbuilds at book ${auc/sh:.2f} a share')
print('candidate explanations at 30 Sep: charter marks $458m-$600m ($1.58-$2.07 a share, fleet_valuation.py); '
      'newbuilds counted at value in the fleet figure but at cost on the balance sheet would be at most $1.97 a share. '
      'together up to ~$4.04 of the $5.65 gap, and neither explains a $8.29 gap at the end of 2025.')
