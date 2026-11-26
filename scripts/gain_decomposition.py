# the test the call turns on: do CMB.TECH's ship sale gains need ship prices to rise, or would they come anyway
# because the books depreciate ships faster than the market does?
# for every tanker sold 2023 to mid-2026, split the gain (sale price less book, both from the company's disposal notes):
#   depreciation part = what the ship would be worth at its age if ship prices had stayed where they were when it was
#                       bought, less book value. positive if the books write ships down faster than the market does.
#   price part        = sale price less that flat-price value. this is the part that needs prices to have risen.
# accounting: 20-year straight line to residual = lightweight x $460/ldt (20-F 2025 depreciation policy).
# economics: a ship loses a fixed share of value each year, set from the ratio of a 10-year-old to a 5-year-old VLCC.
# Signal Ocean (via Breakwave) gives 52.7/76.2 = 0.69 in Feb 2016 and 74/98 = 0.755 in Feb 2023; 0.80 as a high case.
# cost is backed out of book value with the depreciation policy, which treats every ship as bought new. ships bought
# second-hand (some of the older Euronav VLCCs) are a caveat: for them the price part is measured from an implied cost.
import csv, os, json
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
LDT = {'VLCC': 42000, 'Suezmax': 22000}        # lightweight tonnes, my estimate for modern VLCCs and Suezmaxes
SCRAP = 460                                     # $/ldt, 20-F 2025
sales = {r['vessel']: r for r in rows('vessel_sales_2023_2026.csv')}
built = {r['vessel']: r for r in rows('vessel_sales_built.csv')}

def split(rho, verbose=False):
    d = rho ** (1 / 5)
    tot = {'gain': 0, 'dep': 0, 'price': 0}
    by = {}
    for v, b in built.items():
        if b['type'] not in LDT: continue
        s = sales[v]
        age = float(b['sale_date_approx']) - (int(b['built']) + 0.5)
        if age >= 19: continue                  # at the end of book life the policy can't be inverted
        R = LDT[b['type']] * SCRAP / 1e6
        B, P = float(s['book_value_usd_k']) / 1000, float(s['sale_price_usd_k']) / 1000
        C = R + (B - R) * 20 / (20 - age)       # cost implied by the 20-year straight-line policy
        flat = max(C * d ** age, R)
        dep, price = flat - B, P - flat
        tot['gain'] += P - B; tot['dep'] += dep; tot['price'] += price
        grp = 'Frontline block' if s['frontline_fleet_sale'] == 'yes' else ('2026 pre-war' if s['period'] == '2026H1' else 'other 2023-25')
        g = by.setdefault(grp, {'gain': 0, 'dep': 0, 'price': 0, 'n': 0})
        g['gain'] += P - B; g['dep'] += dep; g['price'] += price; g['n'] += 1
        if verbose:
            print(f'  {v:11s} {b["type"]:7s} built {b["built"]} age {age:4.1f}: cost~${C:5.1f}m book ${B:5.1f}m flat-price ${flat:5.1f}m sold ${P:5.1f}m -> depreciation {dep:+6.1f}, price {price:+6.1f}')
    return tot, by

print('ship by ship, at the 2023 age curve (10-year/5-year 0.755):')
split(0.755, verbose=True)
res = {}
for rho in (0.69, 0.755, 0.80):
    tot, by = split(rho)
    res[rho] = tot
    print(f'\n10-year/5-year value ratio {rho}: {sum(g["n"] for g in by.values())} tankers, gains ${tot["gain"]:,.0f}m = depreciation ${tot["dep"]:,.0f}m ({tot["dep"]/tot["gain"]:.0%}) + price ${tot["price"]:,.0f}m ({tot["price"]/tot["gain"]:.0%})')
    for k, g in by.items():
        print(f'  {k:16s} {g["n"]:2d} ships: gains ${g["gain"]:6.0f}m, depreciation ${g["dep"]:+6.0f}m, price ${g["price"]:+6.0f}m')

# the 2026 sales after the strait shut, where the company gives only gains. Brest, Brugge and Bristol were built for
# $66.4m each (20-F 2023). book estimated from that cost and the policy; sale price = book + gain.
print('\nSuezmaxes built 2023-24 and sold in 2026 (gains from the HY 2026 report and Q3 release; prices estimated):')
R = LDT['Suezmax'] * SCRAP / 1e6
for names, delivered, sold, gain, n in (('Brest + Brugge', 2023.7, 2026.6, 100.2, 2), ('Bristol', 2024.1, 2026.8, 56.9, 1)):
    age = sold - delivered
    book = 66.4 - (66.4 - R) * age / 20
    px_est = book + gain / n
    flat = 66.4 * 0.755 ** (age / 5)
    print(f'  {names}: age {age:.1f}, book about ${book:.1f}m each, implied sale about ${px_est:.0f}m each against a ${66.4:.1f}m build cost; '
          f'flat-price value ${flat:.1f}m, so depreciation {flat-book:+.1f} and price {px_est-flat:+.1f} a ship ({(px_est-flat)/(gain/n):.0%} of the gain is price)')
json.dump({str(k): v for k, v in res.items()}, open(os.path.join(HERE, '..', 'results', 'gain_decomposition.json'), 'w'), indent=1)

# the lightweight tonnages are my estimates. move them 15% either way, across the three age curves, and see how much
# of the gain is price.
base_ldt = dict(LDT); shares = []
for f in (0.85, 1.0, 1.15):
    for t in base_ldt: LDT[t] = base_ldt[t] * f
    for rho in (0.69, 0.755, 0.80):
        tot, _ = split(rho); shares.append(tot['price'] / tot['gain'])
LDT.update(base_ldt)
print(f'\nlightweight 15% either way, all three age curves: price part {min(shares):.0%} to {max(shares):.0%} of the gains')
