# the institutional version: short CMB.TECH against long DHT. both hand similar war money to charterers per share
# (war_money_screen.py), so the pair mostly isolates CMB.TECH's dry bulk and its structure, with some tanker
# exposure left over because DHT is all VLCCs. hedge ratio from a year of daily returns.
import json, os
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
p = {r['item']: float(r['value']) for r in rows('pair_inputs.csv')}
ms = json.load(open(os.path.join(HERE, '..', 'results', 'model_summary.json')))
w = rows('weekly_closes_nasdaq.csv')
def ratio(d): r = next(x for x in w if x['week_ending'] == d); return float(r['CMBT']) / float(r['DHT'])
r0, rw, r1 = ratio('2025-01-03'), ratio('2026-02-27'), ratio('2026-11-24')
print(f'CMBT/DHT price ratio: {r0:.3f} (3 Jan 2025), {rw:.3f} (27 Feb 2026, war starts), {r1:.3f} (24 Nov 2026); since the war {r1/rw-1:+.0%}, since Jan 2025 {r1/r0-1:+.0%}')
rs = [float(x['CMBT']) / float(x['DHT']) for x in w]
print(f'weekly ratio range since Jan 2025: {min(rs):.3f} to {max(rs):.3f}')
h = p['beta_cmbt_on_dht_daily_1y']
print(f'hedge ratio {h:.2f} (daily, 1 year); correlation {p["corr_cmbt_dht_daily_1y"]:.2f}; pair volatility {p["vol_pair_hedged_annual"]:.0%} vs {p["vol_cmbt_annual"]:.0%} for CMBT alone')
dht_ttm = sum(p[k] for k in ('dht_div_q4_2025', 'dht_div_q1_2026', 'dht_div_q2_2026', 'dht_div_q3_2026'))
dy = dht_ttm / p['dht_close_2026_11_24']
for lab, cm in (('before the 9 Dec ex-date', ms['dist12']), ('after it', ms['dist12'] - 0.65)):
    c = -cm / p['cmbt_close_2026_11_24'] + h * dy
    print(f'carry per $1 short CMBT, {lab}: pay {cm/p["cmbt_close_2026_11_24"]:.1%}, receive {h:.2f} x DHT trailing yield {dy:.1%} = {c:+.1%} a year before borrow cost')
print(f'DHT trailing four dividends ${dht_ttm:.2f}; DHT pays out most of its profit, so this falls if VLCC rates do')
