# CMB.TECH's own FY2027 free cash flow slide (after capex, before vessel sales) gives each division at three rate decks.
# the step from base to +10% tells me how many $m each $1,000/day is worth, and so where each division breaks even.
# then I rerun 2027 with rates set to what the company actually earned in Q3 2025, before the war.
# straight-line extrapolation outside the company's range is my simplification, flagged in the README.
from common import rows
fcf = {r['division']: r for r in rows('fcf_2027_by_division.csv')}
rate = {r['rate']: r for r in rows('fcf_2027_rate_assumptions.csv')}
fx = {r['segment']: r for r in rows('fixtures.csv')}
mkt = {r['item']: float(r['value']) for r in rows('market_2026-11-24.csv')}
sh = 290.169769

link = {'VLCC': ('VLCC', 'VLCC spot'), 'Suezmax': ('Suezmax', 'Suezmax spot'), 'Newcastlemax': ('Newcastlemax', 'Newcastlemax spot'),
        'Capesize': ('Capesize', 'Capesize spot'), 'Kamsarmax': ('Kamsarmax', 'Kamsarmax/Panamax spot')}
slope, be = {}, {}
print('division  base $m  $m per $1k/day  cash breakeven $/day  (company P&L breakeven)')
for d, (rk, fk) in link.items():
    b, p = float(fcf[d]['base']), float(fcf[d]['plus10'])
    rb, rp = float(rate[rk]['base']), float(rate[rk]['plus10'])
    slope[d] = (p - b) / ((rp - rb) / 1000)
    be[d] = rb - b / slope[d] * 1000
    print(f'{d:12s} {b:6.0f}   {slope[d]:6.2f}          {be[d]:9,.0f}              {float(fx[fk]["pnl_breakeven"]):,.0f}')
fixed = sum(float(fcf[d]['base']) for d in ('FSO', 'Chemical', 'Container', 'CSOV'))
print(f'divisions held flat (FSO, chemical, container, CSOV): ${fixed:.0f}m')

def run(r):
    return fixed + sum(slope[d] * (r[d] - float(rate[link[d][0]]['base'])) / 1000 + float(fcf[d]['base']) for d in link)

base = {d: float(rate[link[d][0]]['base']) for d in link}
q325 = {d: float(fx[link[d][1]]['q3_2025']) for d in link}
cap = mkt['cmbt_close'] * sh
sc = {
    'company base deck': base,
    'tankers at Q3 2025 rates, dry bulk at company base': {**base, 'VLCC': q325['VLCC'], 'Suezmax': q325['Suezmax']},
    'everything at Q3 2025 rates': q325,
}
for k, r in sc.items():
    v = run(r)
    print(f'{k}: FY2027 FCF ${v:,.0f}m = ${v/sh:.2f} a share, {v/cap:.1%} of the ${cap:,.0f}m market cap')
