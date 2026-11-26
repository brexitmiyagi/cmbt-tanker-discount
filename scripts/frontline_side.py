# the 24 VLCCs Euronav sold to Frontline in 2023-24, from Frontline's side: what it paid (Euronav's disposal notes),
# against what the same ships are worth now on the Compass/Clarksons curve at their 2026 age. assumes Frontline still
# owns them all, which I haven't checked ship by ship, and ignores what they earned in between.
import os, json
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
sales = {r['vessel']: r for r in rows('vessel_sales_2023_2026.csv') if r['frontline_fleet_sale'] == 'yes'}
built = {r['vessel']: r for r in rows('vessel_sales_built.csv')}
c = {int(r['age']): float(r['value_usd_m']) for r in rows('secondhand_values_2026-11-16.csv') if r['type'] == 'VLCC'}
c[25] = 42000 * 460 / 1e6
def val(age):
    pts = sorted(c)
    for a, b in zip(pts, pts[1:]):
        if a <= age <= b: return c[a] + (c[b] - c[a]) * (age - a) / (b - a)
paid = now = 0; n = 0; ages = []
for v, s in sales.items():
    if v not in built: continue
    age = 2026.9 - (int(built[v]['built']) + 0.5)
    paid += float(s['sale_price_usd_k']) / 1000; now += val(age); n += 1; ages.append(age)
print(f'{n} of the {len(sales)} Frontline VLCCs matched to build years: paid ${paid:,.0f}m, worth about ${now:,.0f}m now (ages {min(ages):.0f}-{max(ages):.0f}), {now/paid-1:+.0%}, ${now-paid:,.0f}m')
print(f'  CMB.TECH booked ${sum(float(s["gain_usd_k"]) for s in sales.values())/1000:,.0f}m of gains selling them; Frontline holds ${now-paid:,.0f}m on paper since')
json.dump({'paid': paid, 'now': now, 'n': n}, open(os.path.join(HERE, '..', 'results', 'frontline_side.json'), 'w'), indent=1)
