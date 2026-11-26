# the dry bulk side, and the deck figures checked against CMB.TECH's own Q3 2026 presentation (deck_check_q3_2026.csv)
from common import rows
d = {r['item']: r for r in rows('deck_check_q3_2026.csv')}
g = {r['item']: float(r['value']) for r in rows('dry_bulk_demand_2026-11.csv')}
v = lambda k: d[k]['value']
print(f'deck, checked: VLCC orderbook {v("vlcc_orderbook_pct")}%, Suezmax {v("suezmax_orderbook_pct")}%, Capesize {v("capesize_orderbook_pct")}%; VLCC fleet growth 2027-29 {v("vlcc_fleet_growth_2027")}/{v("vlcc_fleet_growth_2028")}/{v("vlcc_fleet_growth_2029")}%, Suezmax {v("suezmax_fleet_growth_2027")}/{v("suezmax_fleet_growth_2028")}/{v("suezmax_fleet_growth_2029")}%')
print(f'  VLCCs over 20 years {v("vlcc_over_20_pct")}%; Capesizes over 15 years {v("capesize_over_15_pct")}%; not confirmed and dropped: {[k for k, r in d.items() if r["status"] != "confirmed"]}')
print(f'China crude steel Jan-Oct 2026 {g["china_crude_steel_jan_oct_2026_mt"]}mt ({g["china_crude_steel_jan_oct_yoy_pct"]:+}%), iron ore imports {g["china_iron_ore_imports_jan_oct_2026_bt"]}bn t ({g["china_iron_ore_imports_jan_oct_yoy_pct"]:+}%)')
print(f'Guinea iron ore exports to Oct about {g["guinea_iron_ore_exports_ytd_oct_2026_mt"]:.0f}mt; Simandou export capacity target {v("simandou_export_capacity_end_2027_mt")}mt by end-2027; Guinea-China +{g["guinea_china_tonne_mile_premium_vs_australia_pct"]:.0f}% tonne-miles vs Australia')
print(f'iron ore tonne-miles {v("iron_ore_tonne_mile_2026_pct")}% 2026, {v("iron_ore_tonne_mile_2027_pct")}% 2027 against Capesize fleet growth {v("capesize_fleet_growth_2026_pct")}% and {v("capesize_fleet_growth_2027_pct")}%')
