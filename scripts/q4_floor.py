# a floor for Q4 2026, built only from fixtures CMB.TECH has already booked.
# spot ship counts: slide 11 shows 8 tankers trading spot (+1 newbuild). Q3 time charter days (VLCC 184, Suezmax 717)
# put about 2 VLCCs and 8 Suezmaxes on time charter, so I take 2 VLCCs and 6 Suezmaxes on spot. that split is my inference.
# dry bulk: 41 Newcastlemax, 37 Capesize, 30 Kamsarmax/Panamax on the water; slide 11 has 100 of 108 bulkers on spot,
# so I haircut dry bulk spot days by 100/108.
# only the booked share of days gets the Q4 rate; the unbooked share is assumed to earn the Q3 rate. ships sold but
# still trading until delivery (Donoussa, Bristol) are ignored, which is why this is a floor.
from common import rows, kv
fx = {r['segment']: r for r in rows('fixtures.csv')}
inc = kv('income_q3_2026.csv', 'item', 'usd_thousands')
gains_q4 = sum(float(r['gain_usd_m']) for r in rows('tanker_sales_2026.csv') if r['delivery'] == '2026Q4')
sh = 290.169769
days = 92
ships = {'VLCC spot': 2, 'Suezmax spot': 6, 'Newcastlemax spot': 41 * 100 / 108, 'Capesize spot': 37 * 100 / 108,
         'Kamsarmax/Panamax spot': 30 * 100 / 108}
up = 0
for s, n in ships.items():
    f = fx[s]
    d = n * days * float(f['fixed_pct']) * (float(f['q4_2026_to_date']) - float(f['q3_2026'])) / 1e6
    up += d
    print(f'{s:24s} {n:5.1f} ships, {float(f["fixed_pct"]):.0%} booked: +${d:6.1f}m vs Q3')
q3_ex = (inc['net_profit'] - inc['gain_on_disposal']) / 1000
q4 = q3_ex + up + gains_q4
print(f'Q3 profit ex disposal gains ${q3_ex:,.1f}m; booked uplift +${up:,.1f}m; Q4 gains already announced ${gains_q4:.1f}m')
print(f'Q4 2026 profit floor ${q4:,.1f}m = ${q4/sh:.2f} a share; at the 50% payout that is about ${q4/sh/2:.2f} a share')
print(f'Q4 floor ex gains ${q4-gains_q4:,.1f}m = ${(q4-gains_q4)/sh:.2f} a share')
