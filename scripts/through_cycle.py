# what a normal year looks like, from the companies' own reported rates and returns, not from one year.
# rates: Euronav/CMB.TECH realised spot and time charter averages 2015-2025 (data/euronav_realised_rates.csv).
# Capesize: Clarksons says 2025 was "circa 40%" above the 10-year average, so I put the 10-year Capesize average at
# the 2025 Baltic 5TC average ($21,297) / 1.4. different index bases, so that one is approximate.
import json, os
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
r = rows('euronav_realised_rates.csv')
avg = lambda k: sum(float(x[k]) for x in r) / len(r)
tc = {'VLCC': avg('vlcc_spot'), 'Suezmax': avg('suezmax_spot'), 'Capesize': 21297 / 1.4}
print(f'2015-2025 averages: VLCC spot ${tc["VLCC"]:,.0f} (2025: $46,353), Suezmax spot ${tc["Suezmax"]:,.0f} (2025: $48,576); Capesize 10-year about ${tc["Capesize"]:,.0f} (2025: $21,297)')
print('so 2025 was an above-average year for all three. Clarksons: VLCC earnings in 2025 were "the highest level in 10 years"')
print('charter book, full cycle (time charter minus spot, $/day):')
for x in r:
    print(f'  {x["year"]}: VLCC {float(x["vlcc_tc"])-float(x["vlcc_spot"]):+8,.0f}   Suezmax {float(x["suezmax_tc"])-float(x["suezmax_spot"]):+8,.0f}')
dv = sum(float(x['vlcc_tc']) - float(x['vlcc_spot']) for x in r) / len(r)
ds = sum(float(x['suezmax_tc']) - float(x['suezmax_spot']) for x in r) / len(r)
yrs_s = sum(1 for x in r if float(x['suezmax_tc']) > float(x['suezmax_spot']))
yrs_v = sum(1 for x in r if float(x['vlcc_tc']) > float(x['vlcc_spot']))
print(f'  average 2015-2025: VLCC charters {dv:+,.0f}/day against spot (above spot in {yrs_v} of {len(r)} years); Suezmax charters {ds:+,.0f}/day (above spot in {yrs_s} of {len(r)} years)')
roe = {}
print('returns on equity by window are in roe_windows.py')
json.dump({'through_cycle': tc, 'roe': roe}, open(os.path.join(HERE, '..', 'results', 'through_cycle.json'), 'w'), indent=1)
