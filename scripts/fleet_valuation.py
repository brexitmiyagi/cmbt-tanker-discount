# my own fleet valuation, ship by ship, from public broker age curves (Compass Maritime, 16 Nov 2026, plus Clarksons
# 15-year points). no valuation service. each ship: linear interpolation between the age points, straight-line
# extrapolation past the last point. ages as of end-November 2026, assuming each ship was delivered mid-year.
# Newcastlemaxes have no public curve, so they get the Capesize curve scaled by deadweight (210k / 180k);
# Panamaxes get the Kamsarmax curve scaled the same way (75k / 82k). those two are my assumptions.
# then each chartered ship is marked down by the present value of (market rate - charter rate) over what's left
# of its charter. market = the 12-month time charter rate for the first year, then the pre-war Q3 2025 spot rate.
from common import rows
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
NOW = 2026.9
import sys
SRC = sys.argv[1] if len(sys.argv) > 1 else 'secondhand_values_2026-11-16.csv'
print(f'curves: {SRC}')
pts = {}
for r in rows(SRC):
    pts.setdefault(r['type'], []).append((float(r['age']), float(r['value_usd_m'])))
def val(curve, age):
    p = sorted(pts[curve])
    if age <= p[0][0]: return p[0][1]
    for (a0, v0), (a1, v1) in zip(p, p[1:]):
        if age <= a1: return v0 + (v1 - v0) * (age - a0) / (a1 - a0)
    (a0, v0), (a1, v1) = p[-2], p[-1]
    return max(v1 + (v1 - v0) * (age - a1) / (a1 - a0), 0)
scale = {'Newcastlemax': ('Capesize', 210 / 180), 'Capesize': ('Capesize', 1), 'Kamsarmax': ('Kamsarmax', 1), 'Panamax': ('Kamsarmax', 75 / 82)}
db = {}
# the 20-F list (1 April) has 45 Newcastlemaxes; Q3 2026 says 41 on the water plus 5 on order, so the 4 youngest
# 2026-built ones are treated as still on order (they sit in assets under construction at cost)
ncm_skip = 4
for r in sorted(rows('fleet_dry_bulk_20F.csv'), key=lambda x: -int(x['built'])):
    if r['type'] == 'Newcastlemax' and ncm_skip > 0:
        ncm_skip -= 1
        continue
    c, k = scale[r['type']]
    age = max(NOW - (int(r['built']) + 0.5), 0)
    db.setdefault(r['type'], []).append(val(c, age) * k)
tot_db = sum(sum(v) for v in db.values())
for t, v in db.items():
    print(f'{t:13s} {len(v):3d} ships, ${sum(v):,.0f}m, average ${sum(v)/len(v):.1f}m')
print(f'dry bulk, my curves: {sum(len(v) for v in db.values())} ships ${tot_db:,.0f}m vs the company broker figure $7,017m (108 ships on 30 Sep) = {tot_db/7017-1:+.1%}')

m = {r['item']: float(r['value']) for r in rows('market_rates_2026-11-16.csv')}
tk = [r for r in rows('fleet_crude_tankers.csv') if r['status_25_nov_2026'] == 'on the water' and r['type'] in ('VLCC', 'Suezmax')]
vl_ages = [NOW - 2025.5, NOW - 2026.3, NOW - 2026.5, NOW - 2026.7]  # Atrebates 2025, Eburones, Menapii, the 4th 2026 ship
vlcc = [val('VLCC', a) for a in vl_ages]
sz = []
for r in tk:
    if r['type'] == 'Suezmax':
        sz.append((r['vessel'], r['employment_1_apr_2026'], val('Suezmax', NOW - (int(r['built']) + 0.5))))
tot_tk = sum(vlcc) + sum(v for _, _, v in sz)
print(f'VLCCs (4): ${sum(vlcc):,.0f}m; Suezmaxes (14): ${sum(v for _,_,v in sz):,.0f}m; together ${tot_tk:,.0f}m vs company $3,128m for 20 tankers incl. 2 FSOs')
pre = m['tanker_fmv_2025_12_31_usd_m'] / m['tanker_ships_2025_12_31']
now = m['tanker_fmv_2026_09_30_usd_m'] / m['tanker_ships_2026_09_30']
print(f'company tanker value per ship: ${pre:.0f}m at end-2025 (pre-war), ${now:.0f}m at 30 Sep 2026 ({now/pre-1:+.0%}); fleet mix differs')

# charter marks. Suezmax charter average $32,986; market: 1-year TC $136,250 then pre-war spot $48,210. 8%.
def mark(years, rate, mkt1, mktn, r=0.08):
    pv, t = 0.0, 0.0
    while t < years - 1e-9:
        step = min(1.0, years - t)
        mkt = mkt1 if t < 1 else mktn
        pv += (mkt - rate) * 365 * step / 1e6 / (1 + r) ** (t + step / 2)
        t += step
    return pv
known = {'Cap Grace': 9.4, 'Cap Joseph': 9.4}
unknown = [n for n, e, _ in sz if e == 'Time Charter' and n not in known]
res = {}
for label, yrs in (('short', 1.0), ('mid', 3.0), ('long', 5.0)):
    s = sum(mark(known[n], 32986, 136250, 48210) for n in known) + sum(mark(yrs, 32986, 136250, 48210) for n in unknown)
    v = mark(0.6, 85623, 234000, 234000)   # the one-year VLCC charter, about 7 months left
    res[label] = s + v
    print(f'charter marks, other {len(unknown)} Suezmax charters assumed {yrs:.0f} yr left: Suezmax ${s:,.0f}m + VLCC ${v:,.0f}m = ${s+v:,.0f}m')
other_fmv = 844 + 408 + 789   # chemicals, containers, offshore at the company's broker values
vessels_book, hfs_book = 6780.215, 160.48
hfs_value = 160.48 + 74.3 + 56.9   # Donoussa and Bristol: book + announced gain
eq = 3495.006
sh = 290.169769
# no public curve covers the two FSOs, so the tankers stay at the company's $3,128m (which includes them);
# my VLCC + Suezmax figure is shown above as a cross-check. dry bulk uses my curves.
navs = {}
for label in ('long', 'mid', 'short'):
    fleet = tot_db + 3128 - res[label] + other_fmv
    nav = eq + (fleet - vessels_book) + (hfs_value - hfs_book)
    navs[label] = nav
    print(f'NAV, my dry bulk + company tankers less charters ({label}): fleet ${fleet:,.0f}m -> NAV ${nav:,.0f}m = ${nav/sh:.2f} a share; price/NAV {17.54*sh/nav:.2f}x')
print(f'implied value left for the two FSOs if my tanker curves are right: ${3128 - tot_tk:,.0f}m')
if len(sys.argv) == 1:
  json.dump({'tot_db': tot_db, 'tot_tk': tot_tk, 'marks': res, 'navs': navs}, open(os.path.join(HERE, '..', 'results', 'fleet_valuation.json'), 'w'))
