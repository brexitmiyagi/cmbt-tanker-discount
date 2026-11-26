# the published valuation with Q4 2026 taken from q4_preview.py instead of model.py. model.py holds the chemical,
# container and offshore businesses flat at their Q3 level; the preview has the CSOVs repositioning in Q4. the
# difference flows into Q4 free cash flow, the Q4 distribution (half of profit, paid in Q1 2027, inside the 12 months)
# and the half that stays in book equity. everything else as valuation_derived.py.
import os, json, math
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda f: json.load(open(os.path.join(HERE, '..', 'results', f)))
ms, rw, ct, q4 = J('model_summary.json'), J('roe_windows.json'), J('charter_test_curves.json'), J('q4_preview.json')['base']
sh, px, k = 290.169769, 17.72, (4.91 + 0.65 * 5) / 100
pred = lambda e, g: (e * 3128 + g * 7017) / 10145
rc = rw['routine_common']
kk = (pred(rc['Euronav'], rc['Golden Ocean']) - pred(0.067, 0.068)) / ((98 / 76.2) ** (1 / 7) - 1)
r_of = lambda d: pred(0.067, 0.068) + kk * d
T_ON = 3.7 - (2 + 1 / 12); drift = ct['fleet']['drift_compass']
dq4 = q4['profit'] - ms['q4_profit']
adj = dict(ms); adj['fcf_q4_26'] += dq4; adj['eq28'] += dq4 * 0.5; adj['dist12'] += dq4 * 0.5 / sh
def value(m, kq=k):
    a, b, c, book = m['fcf_q4_26'] / sh, m['fcf27'] / sh, m['fcf28'] / sh, m['eq28'] / sh
    cash = a / (1 + kq) ** 0.125 + b / (1 + kq) ** 0.625 + c / (1 + kq) ** 1.625
    rd, r0, s, t = r_of(drift), r_of(0.0), 0.0, 0.0
    while t < T_ON - 1e-9:
        dt_ = min(1.0, T_ON - t); s += (rd - kq) * dt_ * book / (1 + kq) ** (t + dt_); t += dt_
    s += (r0 - kq) / kq * book / (1 + kq) ** T_ON
    return cash + (book + s) / (1 + kq) ** 1.625
v0, v1 = value(ms), value(adj)
p0, p1 = v0 * (1 + k) - ms['dist12'], v1 * (1 + k) - adj['dist12']
t1 = math.ceil(p1 * 20) / 20
out = {'dq4': dq4, 'dist12': adj['dist12'], 'value': v1, 'p12': p1, 'target': t1, 'er_target': (t1 + adj['dist12']) / px - 1, 'er_value': v1 * (1 + k) / px - 1,
       'q4_dist': q4['eps'] / 2}
print(f'Q4 profit: model ${ms["q4_profit"]:.1f}m, preview ${q4["profit"]:.1f}m ({dq4:+.1f}m); Q4 distribution ${q4["eps"]/2:.2f} instead of ${ms["q4_profit"]/sh/2:.2f}')
print(f'value today ${v0:.2f} -> ${v1:.2f}; 12-month distributions ${ms["dist12"]:.2f} -> ${adj["dist12"]:.2f}; 12-month price ${p0:.2f} -> ${p1:.2f}; target ${t1:.2f}; '
      f'expected total return at the target {out["er_target"]:+.1%} (on the unrounded value {out["er_value"]:+.1%})')
json.dump(out, open(os.path.join(HERE, '..', 'results', 'valuation_aligned.json'), 'w'), indent=1)
