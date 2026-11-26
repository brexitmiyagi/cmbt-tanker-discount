# the published valuation, one method: discounted cash flow. Q4 2026 to 2028 free cash flow from model.py, then a
# normal year for ever as a return on end-2028 book equity, at an 8.2% cost of equity. the normal year is the
# predecessors' 6.8% with no sale gains, plus sale gains scaled to ship-price drift (0.31 points of return on equity
# per point of yearly drift, forward_gains.py) at -2% a year: 6.1%. the 12-month price is today's value grown a year
# at the cost of equity, less 12 months of distributions. the asset view and Hormuz paths are a cross-check
# (rating_v19.py), not part of the target.
import json, os, math
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda f: json.load(open(os.path.join(HERE, '..', 'results', f)))
ms, rw, rv = J('model_summary.json'), J('roe_windows.json'), J('rating_v19.json')
sh = 290.169769
px = {r['ticker']: float(r['close_2026_11_25']) for r in rows('prices_2026-11-25.csv')}['CMBT']
k, dist = (4.91 + 0.65 * 5) / 100, ms['dist12']
f27, f28, q4 = ms['fcf27'] / sh, ms['fcf28'] / sh, ms['fcf_q4_26'] / sh; book = ms['eq28'] / sh
pred = lambda e, g: (e * 3128 + g * 7017) / 10145
rc = rw['routine_common']
kk = (pred(rc['Euronav'], rc['Golden Ocean']) - pred(0.067, 0.068)) / ((98 / 76.2) ** (1 / 7) - 1)
r_of = lambda d: pred(0.067, 0.068) + kk * d
def parts(r, kq=k):
    cash = q4 / (1 + kq) ** 0.125 + f27 / (1 + kq) ** 0.625 + f28 / (1 + kq) ** 1.625
    at_k = book / (1 + kq) ** 1.625                     # a normal year that earns exactly the cost of equity is worth book
    short = (r - kq) / kq * book / (1 + kq) ** 1.625    # what earning less than the cost of equity takes off
    return cash, at_k, short
def p12(r, kq=k):
    c, a, s = parts(r, kq); return (c + a + s) * (1 + kq) - dist
r = r_of(-0.02)
c, a, s = parts(r)
today = c + a + s; t12 = today * (1 + k) - dist; tgt = math.ceil(t12 * 20) / 20
print(f'cash Q4 2026-2028 ${c:.2f} + end-2028 book at the cost of equity ${a:.2f} = ${c+a:.2f}; normal year {r:.1%} vs cost of equity {k:.1%}: ${s:+.2f}')
print(f'value today ${today:.2f}; a year at {k:.1%} ${today*k:+.2f}; distributions -${dist:.2f}; 12-month ${t12:.2f} -> target ${tgt:.2f} (rounded up)')
print(f'expected 12-month total return at ${px}: {(tgt+dist)/px-1:+.1%} vs SELL line {k-0.05:.1%}')
lo, hi = -0.05, 0.25
for _ in range(60):
    m = (lo + hi) / 2; lo, hi = (m, hi) if (c + a + (m - k) / k * a) < px else (lo, m)
print(f'the price today needs a normal year of {m:.1%} on end-2028 book')
for lab, d in (('flat', 0.0), ('+3.7% (2016-23)', (98 / 76.2) ** (1 / 7) - 1), ('-4.5%', -0.045)):
    print(f'  drift {lab}: normal year {r_of(d):.1%}, expected {(p12(r_of(d))+dist)/px-1:+.1%}')
for kq in (0.075, 0.0843, 0.094):
    print(f'  cost of equity {kq:.2%}: expected {(p12(r, kq)+dist)/px-1:+.1%} vs SELL line {kq-0.05:.1%}')
lo, hi = -0.06, 0.06
for _ in range(60):
    m2 = (lo + hi) / 2; lo, hi = (m2, hi) if (p12(r_of(m2)) + dist) / px - 1 < k - 0.05 else (lo, m2)
print(f'  the SELL holds for any drift below {m2:+.2%} a year')
nav = J('earnings_nav.json')['H']['nav2']
print(f'bridge from the earnings NAV: through-cycle earnings NAV ${nav:.2f}; the cash view with a normal year at the cost of equity ${c+a:.2f}; less the shortfall ${s:.2f} = ${today:.2f}')
print(f'cross-check: asset view across the Hormuz paths ${rv["asset"]:.2f} in 12 months (rating_v19.py); averaged with this, ${rv["target"]:.2f}')
json.dump({'cash': c, 'book_pv': a, 'shortfall': s, 'today': today, 'p12': t12, 'target': tgt, 'er': (tgt + dist) / px - 1, 'r': r, 'r_needed': m, 'drift_line': m2},
          open(os.path.join(HERE, '..', 'results', 'valuation_simple.json'), 'w'), indent=1)
