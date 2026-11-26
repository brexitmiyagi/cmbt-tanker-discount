# the supply side: how much is on order against the fleet now, and what happened the last time the tanker orderbook
# was this big. CMB.TECH's own Q3 2026 deck for today's ratios, Signal Ocean for VLCC deliveries, and Euronav's 2015
# prospectus and Poten for the 2008 episode.
from common import rows
d = {r['item']: float(r['value']) for r in rows('orderbook_2026.csv')}
print(f'orderbook as a share of the fleet, Q3 2026: VLCC {d["vlcc_orderbook_pct_fleet"]:.1f}%, Suezmax {d["suezmax_orderbook_pct_fleet"]:.1f}%, Capesize {d["capesize_orderbook_pct_fleet"]:.1f}%')
print(f'VLCC capacity growth: 2026 {d["vlcc_capacity_growth_2026_pct"]}%, 2027 {d["vlcc_capacity_growth_2027_pct"]}%, 2028 {d["vlcc_capacity_growth_2028_pct"]}%, 2029 {d["vlcc_capacity_growth_2029_pct"]}%')
g = 1
for y in (2027, 2028, 2029): g *= 1 + d[f'vlcc_capacity_growth_{y}_pct'] / 100
print(f'  VLCC capacity 2027-29 compounded: +{g-1:.0%} before scrapping')
print(f'VLCC deliveries (Signal Ocean): ' + ', '.join(f'{y} {d[f"vlcc_deliveries_{y}"]:.0f}' for y in range(2026, 2031)))
print(f'Q1 2028 alone: {d["deliveries_q1_2028_vlcc_suezmax"]:.0f} VLCCs and Suezmaxes')
a, b = d['vlcc_newbuild_2008_peak_usd_m'], d['vlcc_newbuild_jan_2015_usd_m']
yrs = 2015.05 - 2008.5
print(f'last time: crude tanker orderbook about {d["crude_tanker_orderbook_pct_2008_peak"]:.0f}% of the fleet at the 2008 peak, {d["crude_tanker_orderbook_pct_dec_2014"]}% by Dec 2014;'
      f' VLCC newbuild ${a}m (2008 peak) to ${b}m (Jan 2015), {b/a-1:+.0%}, {(b/a)**(1/yrs)-1:+.1%} a year; five-year-old ${d["vlcc_5yr_feb_2016_usd_m"]}m by Feb 2016')
print(f'Euronav bought 15 Maersk VLCCs in 2014 at an average ${d["euronav_maersk_vlcc_avg_2014_usd_m"]}m, the cost basis behind its 2016-18 gains')
