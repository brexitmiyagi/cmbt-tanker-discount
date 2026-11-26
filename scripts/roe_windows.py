# what shipowners actually earned on their equity, without picking the window. every 8-year window each company's
# filings allow, the common 2015-2024 window, reported and adjusted (impairments added back, disposal gains taken out).
# return = sum of net income / sum of average equity over the window.
import json, os
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
H = {}
for r in rows('roe_history.csv'):
    H.setdefault(r['company'], {})[int(r['year'])] = r
f = lambda x: float(x) if x not in ('', None) else 0.0
def roe(co, a, b, adj):
    h = H[co]; ni = ae = 0.0
    for y in range(a, b + 1):
        n = f(h[y]['net_income_usd_m'])
        if adj: n += f(h[y]['impairment_usd_m']) - f(h[y]['disposal_gain_usd_m'])
        ni += n; ae += (f(h[y]['equity_end_usd_m']) + f(h[y - 1]['equity_end_usd_m'])) / 2
    return ni / ae
allw = {'reported': [], 'adjusted': []}
for co, h in H.items():
    ys = sorted(y for y in h if h[y]['net_income_usd_m'] not in ('', None))
    print(f'{co} ({ys[0]}-{ys[-1]}):')
    for adj, lab in ((False, 'reported'), (True, 'adjusted')):
        ws = [(a, a + 7, roe(co, a, a + 7, adj)) for a in ys if a + 7 <= ys[-1]]
        allw[lab] += [x[2] for x in ws]
        print(f'  {lab}: full span {roe(co, ys[0], ys[-1], adj):.1%}; 8-year windows ' + ', '.join(f'{a}-{b} {x:.1%}' for a, b, x in ws))
for adj, lab in ((False, 'reported'), (True, 'adjusted')):
    c = {co: roe(co, 2015, 2024, adj) for co in H}
    print(f'common window 2015-2024, {lab}: ' + ', '.join(f'{k} {v:.1%}' for k, v in c.items()))
for lab, v in allw.items():
    v = sorted(v)
    print(f'all 8-year windows, {lab}: {len(v)} windows, range {v[0]:.1%} to {v[-1]:.1%}, median {v[len(v)//2]:.1%}')
json.dump({k: sorted(v) for k, v in allw.items()}, open(os.path.join(HERE, '..', 'results', 'roe_windows.json'), 'w'))

# third version, after building the sale ledger (vessel_sales.py): keep routine sale gains, because selling 15-year-old
# ships above depreciated book happens every cycle, but take out the one-off 2023-24 break-up sale of 24 VLCCs to
# Frontline, which was priced on broker valuations and came out of a shareholder settlement, not trading.
# impairments still added back.
fl = {}
for r in rows('vessel_sales_2023_2026.csv'):
    if r['frontline_fleet_sale'] == 'yes':
        fl[int(r['period'])] = fl.get(int(r['period']), 0) + float(r['gain_usd_k']) / 1000
def roe_routine(co, a, b):
    h = H[co]; ni = ae = 0.0
    for y in range(a, b + 1):
        n = f(h[y]['net_income_usd_m']) + f(h[y]['impairment_usd_m'])
        if co == 'Euronav': n -= fl.get(y, 0)
        ni += n; ae += (f(h[y]['equity_end_usd_m']) + f(h[y - 1]['equity_end_usd_m'])) / 2
    return ni / ae
rt = {co: roe_routine(co, 2015, 2024) for co in H}
print('common window 2015-2024, routine gains kept, Frontline break-up sale and impairments out: ' + ', '.join(f'{k} {v:.1%}' for k, v in rt.items()))
print(f'Frontline break-up gains taken out: 2023 ${fl.get(2023,0):.1f}m, 2024 ${fl.get(2024,0):.1f}m')
allr = []
for co, h in H.items():
    ys = sorted(y for y in h if h[y]['net_income_usd_m'] not in ('', None))
    allr += [roe_routine(co, a, a + 7) for a in ys if a + 7 <= ys[-1]]
allr = sorted(allr)
print(f'all 8-year windows, routine gains kept: {len(allr)} windows, range {allr[0]:.1%} to {allr[-1]:.1%}, median {allr[len(allr)//2]:.1%}')
d = json.load(open(os.path.join(HERE, '..', 'results', 'roe_windows.json')))
d['routine'] = allr; d['routine_common'] = rt
json.dump(d, open(os.path.join(HERE, '..', 'results', 'roe_windows.json'), 'w'))
