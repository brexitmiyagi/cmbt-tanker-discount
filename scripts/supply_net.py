# the bull's reply to the orderbook: old ships get scrapped and the shadow fleet is out of the market anyway. so net
# deliveries against scrapping, three ways, for 2027-2029. capacity growth is CMB.TECH's Q3 deck (orderbook.py); I
# can't tell from the write-up whether it is gross deliveries or already net of an assumed scrapping rate. if it's
# already net, the scrapping offset below is double-counted and the net figures are too low.
from common import rows
d = {r['item']: float(r['value']) for r in rows('vlcc_supply_2026.csv')}
o = {r['item']: float(r['value']) for r in rows('orderbook_2026.csv')}
g = 1
for y in (2027, 2028, 2029): g *= 1 + o[f'vlcc_capacity_growth_{y}_pct'] / 100
gross = g - 1
fleet = d['vlcc_fleet_ships']
pace = d['vlcc_scrapped_2022_may2026'] / 4.4 / fleet       # VLCCs scrapped a year as a share of the fleet
cases = {'scrapping at the 2022-26 pace': pace * 3, 'every VLCC over 20 today scrapped (125)': d['vlcc_20plus_high'] / fleet,
         'every VLCC over 20 by 2029 scrapped (21% of fleet)': d['vlcc_20plus_share_2029_ti']}
print(f'VLCC capacity 2027-29 from the deck: +{gross:.0%}; fleet about {fleet:.0f} ships, about {fleet*gross:.0f} ship-equivalents added')
for k, s in cases.items():
    print(f'  {k:52s}: scrapping {s:.0%} of the fleet -> net growth {(1+gross)*(1)-s-1:+.0%}')
shadow = (d['vlcc_sanctioned'] + d['vlcc_sanctioned_barrels']) / fleet
main = 1 - shadow
print(f'shadow/sanctioned VLCCs about {shadow:.0%} of the fleet; if every new ship joins the mainstream fleet and every shadow ship is scrapped,')
print(f'  mainstream capacity grows {gross/main:+.0%} on its own base before mainstream scrapping')
print(f'if sanctions end and the ~{d["vlcc_sanctioned"]:.0f} sanctioned VLCCs rejoin compliant trade, mainstream supply rises another {d["vlcc_sanctioned"]/fleet/main:+.0%}')
print(f'the +{d["ti_effective_growth_3y"]:.0%} effective-growth estimate (Tankers International, Apr 2025) predates the 2026 orders')
