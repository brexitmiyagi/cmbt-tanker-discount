# the tankers CMB.TECH still owns are mostly not earning the war rate.
# slide 11: 8 tankers spot, 12 on time charter. the Suezmax time charter average has sat at ~$31k-35k a day
# through the whole war. this prints what that costs, using only the company's own numbers.
# brokers value ships charter-free, so the $3,128m tanker FMV on slide 4 assumes a buyer gets market rates.
# a ship tied up on a fixed charter is worth less than that until the charter ends.
from common import rows
t = {r['item']: float(r['value']) for r in rows('tanker_time_charters.csv')}
sh = 290.169769
q = ['q1_2025', 'q2_2025', 'q3_2025', 'q1_2026', 'q2_2026', 'q3_2026']
print('Suezmax time charter average, $/day: ' + ', '.join(f'{k} {t["suezmax_tc_rate_"+k]:,.0f}' for k in q))
d, tc = t['suezmax_tc_days_q3_2026'], t['suezmax_tc_rate_q3_2026']
gap3 = d * (t['suezmax_spot_q3_2026'] - tc) / 1e6
print(f'Q3 2026: {d:.0f} Suezmax time charter days earned ${d*tc/1e6:.1f}m; at the Q3 spot rate ${d*t["suezmax_spot_q3_2026"]/1e6:.1f}m; gap ${gap3:.1f}m = ${gap3/sh:.2f} a share')
gap4 = d * (t['suezmax_spot_q4_2026_to_date'] - tc) / 1e6
print(f'Q4 2026 if time charter days match Q3: ${d*tc/1e6:.1f}m on charter vs ${d*t["suezmax_spot_q4_2026_to_date"]/1e6:.1f}m at the Q4-to-date spot rate; gap ${gap4:.1f}m = ${gap4/sh:.2f} a share')
# 2027 spot days backed out of slide 8: FCF step from base to +10% divided by the +10% rate step
s_spot = (t['suezmax_fcf_2027_plus10'] - t['suezmax_fcf_2027_base']) * 1e6 / (0.10 * t['suezmax_base_2027'])
s_tc = t['suezmax_on_water'] * 365 - s_spot
v_spot = (t['vlcc_fcf_2027_plus10'] - t['vlcc_fcf_2027_base']) * 1e6 / (0.10 * t['vlcc_base_2027'])
v_tc = t['vlcc_on_water_2027'] * 365 - v_spot
print(f'2027 Suezmax spot days implied by slide 8: {s_spot:,.0f} ({s_spot/365:.1f} ships); on charter {s_tc:,.0f} ({s_tc/365:.1f} ships)')
print(f'2027 VLCC spot days implied: {v_spot:,.0f}; on charter {v_tc:,.0f} (about {v_tc/30.4:.1f} months of one ship, consistent with the 1-year VLCC charter from June 2026)')
drag27 = (s_tc * (t['suezmax_base_2027'] - tc) + v_tc * (t['vlcc_base_2027'] - t['vlcc_tc_rate_q3_2026'])) / 1e6
print(f'2027 cost of the charters against the company base deck: ${drag27:.1f}m = ${drag27/sh:.2f} a share')
# after 2027: Suezmax charters against the pre-war spot rate (Q3 2025), for 3 or 8 more years, at 8%
yr = s_tc * (t['suezmax_spot_q3_2025'] - tc) / 1e6
print(f'after 2027 at the pre-war Suezmax spot rate the charters still cost ${yr:.1f}m a year')
for n in (3, 8):
    pv = drag27 / 1.08 + sum(yr / 1.08 ** k for k in range(2, n + 2))
    print(f'charter-adjusted markdown, {n} more years after 2027: ${pv:,.0f}m = ${pv/sh:.2f} a share')
# what the charters do to the valuation
pb = {r['item']: float(r['value']) for r in rows('peer_star_bulk.csv')}
disc = pb['close_2026_11_24'] * pb['diluted_shares_m'] / (pb['fleet_market_value_usd_m'] - pb['net_debt_usd_m'])
nav1, nav2, tank_fmv = 7259.1, 8900.8, 3128.0
cap = 17.54 * sh
for n, pv in (('3 yrs', drag27 / 1.08 + sum(yr / 1.08 ** k for k in range(2, 5))), ('8 yrs', drag27 / 1.08 + sum(yr / 1.08 ** k for k in range(2, 10)))):
    a1, a2 = (nav1 - pv) / sh, (nav2 - pv) / sh
    print(f'{n}: charter-adjusted tanker value ${tank_fmv-pv:,.0f}m, market pays ${cap - disc*(nav1 - tank_fmv):,.0f}m = {(cap - disc*(nav1 - tank_fmv))/(tank_fmv-pv):.0%} of it; NAV route 1 ${a1:.2f}, route 2 ${a2:.2f}; at Star Bulk 0.76x ${disc*a1:.2f} / ${disc*a2:.2f}, midpoint ${disc*(a1+a2)/2:.2f}')
sold = {'Ilma': 'TI Pool', 'Ingrid': 'TI Pool', 'Donoussa': 'Time Charter', 'Sienna': 'Spot', 'Stella': 'Spot', 'Brest': 'Spot', 'Brugge': 'Spot', 'Bristol': 'Spot'}
print(f'tankers on the 1 Apr 2026 20-F list sold since: {len(sold)}, of which on time charter: {sum(v=="Time Charter" for v in sold.values())}')
# the half-markdown route from nav_bridge.py ($21.13) less the charter markdown
for n, pv in (('3 yrs', 183.0), ('8 yrs', 284.0)):
    print(f'half decade-average tanker markdown less charters ({n}): ${21.13 - pv/sh:.2f}')
