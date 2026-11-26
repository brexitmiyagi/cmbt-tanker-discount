# every ship Euronav / CMB.TECH sold from 2023 to mid-2026, with the sale price, book value and gain the company
# itself discloses (20-F for 2025, HY 2026 report). the question: are the sale gains a skill, selling above the
# market, or just the market being above depreciated book? if it's the second, they come back every cycle only as
# far as ship prices do.
import os, json
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
S = rows('vessel_sales_2023_2026.csv')
k = lambda r, c: float(r[c]) / 1000
for p in ('2023', '2024', '2025', '2026H1'):
    s = [r for r in S if r['period'] == p]
    pr, bk, g = (sum(k(r, c) for r in s) for c in ('sale_price_usd_k', 'book_value_usd_k', 'gain_usd_k'))
    print(f'{p}: {len(s)} ships, sold ${pr:,.0f}m against book ${bk:,.0f}m, gain ${g:,.0f}m ({g/bk:.0%} over book)')
tot_g = sum(k(r, 'gain_usd_k') for r in S)
fl = [r for r in S if r['frontline_fleet_sale'] == 'yes']
flp, flg = sum(k(r, 'sale_price_usd_k') for r in fl), sum(k(r, 'gain_usd_k') for r in fl)
print(f'\nall {len(S)} ships: gains ${tot_g:,.0f}m')
print(f'the 24 VLCCs sold to Frontline in 2023-24: ${flp:,.0f}m (Euronav announced $2.35bn), gains ${flg:,.0f}m, {flg/tot_g:.0%} of all the gains here')
print('  price basis, per Euronav on 9 Oct 2023: "an average of three broker valuations"; a second broker for the')
print('  independent directors was "in line". In October 2024 the FSMA raised CMB\'s bid price by $0.52 a share; Maritime')
print('  Executive reported the vessel pricing "implied certain special benefits to Frontline". So the biggest block of gains')
print('  was sold at broker value or a little under it, not above.')

# the ships sold just before the war, against what the same ages fetch now (Compass Maritime, 16 Nov 2026; the
# 15-year point is Clarksons via CMB.TECH's Q3 deck). straight line between the 10- and 15-year points.
curve = {r['age']: float(r['value_usd_m']) for r in rows('secondhand_values_2026-11-16.csv') if r['type'] == 'VLCC'}
def now_value(built):
    age = 2026 - built
    if age <= 10: return curve['10']
    if age <= 15: return curve['10'] + (curve['15'] - curve['10']) * (age - 10) / 5
    return None
built = {'Dia': 2015, 'Antigone': 2015, 'Aegean': 2016, 'Hojo': 2013, 'Hirado': 2011, 'Ingrid': 2012, 'Ilma': 2012, 'Daishan': 2007}
print('\nVLCCs agreed in January and February 2026, before the strait shut, against today\'s broker curve:')
sold = later = 0
for r in S:
    if r['period'] == '2026H1' and r['vessel'] in built:
        v = now_value(built[r['vessel']]); p = k(r, 'sale_price_usd_k')
        if v is None:
            print(f'  {r["vessel"]:9s} built {built[r["vessel"]]}: sold ${p:.0f}m, no broker point past 15 years'); continue
        sold += p; later += v
        print(f'  {r["vessel"]:9s} built {built[r["vessel"]]}: sold ${p:.0f}m, same age now about ${v:.0f}m')
print(f'  seven ships with a curve point: sold ${sold:,.0f}m, worth about ${later:,.0f}m at today\'s values, ${later-sold:,.0f}m more')
print('  Signal Ocean (via Breakwave, 2 Mar 2026) had 10-year-old VLCCs "above USD 100 million" at the time, so the 2015-16')
print('  ships went at about the market then. The sales tracked the market; they didn\'t beat it.')
json.dump({'frontline_gain': flg, 'all_gain': tot_g, 'prewar_sold': sold, 'prewar_now': later},
          open(os.path.join(HERE, '..', 'results', 'vessel_sales.json'), 'w'), indent=1)

# the sales agreed after the strait shut, where only gains are disclosed so far (tanker_sales_2026.csv)
late = [r for r in rows('tanker_sales_2026.csv') if r['before_war'] == 'no' and 'Sienna' not in r['vessels']]
for r in late:
    print(f'  after the strait shut: {r["vessels"]} ({r["type"]}, built {r["built"]}): gain ${float(r["gain_usd_m"]):.1f}m, delivery {r["delivery"]}')
print(f'  total ${sum(float(r["gain_usd_m"]) for r in late):.1f}m of gains on sales agreed June to October 2026, prices not yet disclosed')
