# valuation: peer multiples by segment, CMB.TECH's own discount history, a sum of the parts and a sensitivity grid.
from common import rows, kv
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
bs = kv('balance_sheet_2026-09-30.csv')
sh = bs['shares_ex_treasury'] / 1e6
px = 17.54
cap = px * sh
fmv = {r['segment']: float(r['fmv_usd_m']) for r in rows('fleet_fair_market_value_2026-09-30.csv')}
nav1, nav2 = 7259.1, 8900.8          # nav_bridge.py
pv_lo, pv_hi = 183.0, 284.0          # tc_drag.py charter markdown

# 1. peers, each on its own disclosed numbers
pm = {}
print('peer price/NAV (NAV = fleet value less net debt):')
for r in rows('peers_nav.csv'):
    c = float(r['close_2026_11_24']) * float(r['shares_m'])
    nav = float(r['fleet_value_usd_m']) - float(r['net_debt_usd_m'])
    pm.setdefault(r['segment'], []).append(c / nav)
    print(f'  {r["ticker"]:5s} {r["segment"]:9s} market cap ${c:,.0f}m, NAV ${nav:,.0f}m, {c/nav:.2f}x  ({r["fleet_value_basis"][:60]})')
m_db = sum(pm['dry bulk']) / len(pm['dry bulk'])
m_tk = sum(pm['tanker']) / len(pm['tanker'])
print(f'average: dry bulk {m_db:.2f}x, tankers {m_tk:.2f}x')

# 2. CMB.TECH's own price/NAV history (route 1, from the value-adjusted equity ratio each quarter)
print('CMB.TECH price/NAV history (route 1):')
hist = []
for r in rows('nav_history.csv'):
    A, E, k = float(r['total_assets_usd_m']), float(r['equity_usd_m']), float(r['value_adjusted_equity_ratio'])
    u = (k * A - E) / (1 - k)
    nps = (E + u) / float(r['shares_ex_treasury_m'])
    hist.append(float(r['close']) / nps)
    print(f'  {r["date"]}: ratio {k:.1%}, NAV ${nps:.2f} a share, close ${float(r["close"]):.2f}, {float(r["close"])/nps:.2f}x')
print(f'  2026-11-24: NAV $25.02, close $17.54, {px/25.02:.2f}x')

# 3. sum of the parts: dry bulk at the dry bulk peer multiple, tankers (charter-adjusted) at the tanker multiple,
#    everything else at broker value (mostly new ships on long charters), less net debt. two NAV bases.
def sotp(nav, pv):
    tank_adj = fmv['Crude tankers'] - pv
    return nav - pv - (1 - m_db) * fmv['Dry bulk'] + (m_tk - 1) * tank_adj
res = {}
for name, nav in (('route 1', nav1), ('route 2', nav2)):
    lo, hi = sotp(nav, pv_hi) / sh, sotp(nav, pv_lo) / sh
    res[name] = (lo, hi)
    print(f'SOTP {name}: ${lo:.2f} to ${hi:.2f} a share')
mid = (sum(res['route 1']) / 2 + sum(res['route 2']) / 2) / 2
print(f'SOTP midpoint ${mid:.2f}; the market price is {px/mid:.2f}x of it, a {1-px/mid:.0%} discount for the structure')
hi_hist = max(hist + [px / 25.02])
print(f'highest CMB.TECH price/NAV in the four points: {hi_hist:.2f}x')

# 4. forward NAV, end-2027, from the model: book equity grows by retained profit, ship uplift held, charters off
ms = json.load(open(os.path.join(HERE, '..', 'results', 'model_summary.json')))
uplift1 = nav1 - 3495.006
fnav = (ms['eq27'] + uplift1 - (pv_lo + pv_hi) / 2) / sh
print(f'forward NAV end-2027 (route 1, uplift held, charter markdown off): ${fnav:.2f}')
for mlt in (0.61, 0.70, 0.76, m_db):
    print(f'  at {mlt:.2f}x: ${fnav*mlt:.2f}')

# 5. sensitivity: value a share by Capesize-equivalent rate (dry bulk deck scaled) and tanker value change.
#    rate effect = one year of extra 2027 FCF (slide 8 slopes), no change in ship values; tanker effect at the tanker multiple.
slope = {'Newcastlemax': 15.51, 'Capesize': 11.26, 'Kamsarmax': 10.56}   # $m per $1,000/day
deck = {'Newcastlemax': 40608, 'Capesize': 31975, 'Kamsarmax': 17050}
base = sum(res['route 1']) / 2   # grid centred on the route 1 sum of the parts, the basis for the target
print(f'grid base (route 1 SOTP midpoint) ${base:.2f}')
print('sensitivity, $ a share (rows: Capesize rate, dry bulk deck scaled with it; columns: tanker values):')
cols = [-0.4, -0.3, -0.2, -0.1, 0.0]
print('  cape $/day ' + ' '.join(f'{c:>7.0%}' for c in cols))
for cape in (25000, 30000, 35000, 40000, 45000):
    f = cape / deck['Capesize'] - 1
    dfcf = sum(slope[k] * deck[k] * f / 1000 for k in slope)
    line = []
    for c in cols:
        dtank = c * (fmv['Crude tankers'] - (pv_lo + pv_hi) / 2) * m_tk
        line.append(base + (dfcf + dtank) / sh)
    print(f'  {cape:>10,} ' + ' '.join(f'{v:7.2f}' for v in line))
json.dump({'m_db': m_db, 'm_tk': m_tk, 'sotp_mid': mid, 'fnav27': fnav, 'hist': hist}, open(os.path.join(HERE, '..', 'results', 'valuation_summary.json'), 'w'))
