# every number the rating rests on, rerun with Q4 2026 from the Q4 preview (model.py with Q4_OTHER=1), so the
# valuation, the Q4 preview and the distributions all use the same Q4. same methods as house_view_checks.py and
# sell_case_checks.py.
import os, json, math, subprocess, sys, tempfile
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda f: json.load(open(os.path.join(HERE, '..', 'results', f)))
rw, ct = J('roe_windows.json'), J('charter_test_curves.json')
sh, px, k = 290.169769, 17.72, (4.91 + 0.65 * 5) / 100
pred = lambda e, g: (e * 3128 + g * 7017) / 10145
rc = rw['routine_common']
kk = (pred(rc['Euronav'], rc['Golden Ocean']) - pred(0.067, 0.068)) / ((98 / 76.2) ** (1 / 7) - 1)
r_of = lambda d: pred(0.067, 0.068) + kk * d
T_ON = 3.7 - (2 + 1 / 12); drift = ct['fleet']['drift_compass']
def run(**env):
    f = os.path.join(tempfile.mkdtemp(), 'ms.json')
    subprocess.run([sys.executable, os.path.join(HERE, 'model.py')], env={**os.environ, 'Q4_OTHER': '1', **{a: str(b) for a, b in env.items()}, 'MODEL_OUT': f}, capture_output=True, check=True)
    return json.load(open(f))
def value(m, kq=k, extra=0.0):
    a, b, c, book = m['fcf_q4_26'] / sh, m['fcf27'] / sh, m['fcf28'] / sh, m['eq28'] / sh
    cash = a / (1 + kq) ** 0.125 + b / (1 + kq) ** 0.625 + c / (1 + kq) ** 1.625 + extra
    rd, r0, s, t = r_of(drift), r_of(0.0), 0.0, 0.0
    while t < T_ON - 1e-9:
        dt_ = min(1.0, T_ON - t); s += (rd - kq) * dt_ * book / (1 + kq) ** (t + dt_); t += dt_
    s += (r0 - kq) / kq * book / (1 + kq) ** T_ON
    v = cash + (book + s) / (1 + kq) ** 1.625
    return v, v * (1 + kq) / px - 1
ffa = {r['period']: float(r['usd_day']) for r in rows('capesize_ffa_2026-10-26.csv') if r['period'].startswith('Cal')}
seg = {r['segment']: r for r in rows('segments_2026-11-20.csv')}
tc = J('through_cycle.json')['through_cycle']
DECK = {'VLCC': 122500, 'Suezmax': 77500}; mine28 = {s: (DECK[s] + tc[s]) / 2 for s in DECK}; days = {'VLCC': 1633, 'Suezmax': 2839}
base = run(); fwd = run(CAPE27=ffa['Cal 2027'], CAPE28=ffa['Cal 2028']); deck = run(CAPE27=ffa['Cal 2027'], CAPE28=ffa['Cal 2028'], TANK28='deck')
w = sum(days[s] * (float(seg[s]['tc_3y']) - mine28[s]) for s in DECK) / sum(days[s] * (DECK[s] - mine28[s]) for s in DECK)
both = {x: fwd[x] + w * (deck[x] - fwd[x]) for x in fwd}
v, e = value(base); p12 = v * (1 + k) - base['dist12']; tgt = math.ceil(p12 * 20) / 20
out = {'q4_profit': base['q4_profit'], 'q4_eps': base['q4_profit'] / sh, 'dist12': base['dist12'], 'value': v, 'p12': p12, 'target': tgt, 'er_target': (tgt + base['dist12']) / px - 1, 'er': e}
print(f'Q4 profit ${base["q4_profit"]:.1f}m (EPS ${base["q4_profit"]/sh:.2f}); 12-month distributions ${base["dist12"]:.2f}; value today ${v:.2f}; 12-month ${p12:.2f} -> target ${tgt:.2f}; '
      f'expected at the target {out["er_target"]:+.1%}, on the value {e:+.1%}; SELL line {k-0.05:.1%}')
for lab, m in (('dry bulk at the forward curve', fwd), ('both at market forward prices', both)):
    out[lab] = value(m)[1]; print(f'  {lab}: {out[lab]:+.1%}; 2028 EPS ${m["fy28_eps"]:.2f}')
# war and sales, as house_view_checks.py
for lab, r27 in (('reopening', {s: DECK[s] / 2 for s in DECK}), ('rates hold', {s: float(seg[s]['tc_1y']) for s in DECK})):
    dni = sum(days[s] * (r27[s] - DECK[s]) for s in DECK) / 1e6
    out[lab] = value(base, extra=dni / (1 + k) ** 0.625 / sh)[1]; print(f'  2027 {lab}: {out[lab]:+.1%}')
per4 = J('house_view_checks.json')['tanker_sales']['dv']
out['sales4'] = value(base, extra=per4)[1]; print(f'  four more tanker sales: {out["sales4"]:+.1%}')
p_open = (0.325 + 0.345) / 2
for n in (4, 8):
    sale_pts = per4 / 4 * n * (1 + k) / px
    out[f'blend{n}'] = p_open * out['reopening'] + (1 - p_open) * (e + sale_pts)
    print(f'  blended ({p_open:.1%} reopening, {n} sales if shut): {out[f"blend{n}"]:+.1%}')
oth = J('q4_preview.json')
yr = 79.0                                                     # q4_preview.py: other businesses at Q3 rates, $m a year
gap = (2041 * (1 - 4870.3 / 12186) - yr / k) / sh               # broker value less pro-rata debt, against Q3 earnings at the cost of equity
out['other_bv'] = e + gap * (1 + k) / px; print(f'  other businesses at broker value: {out["other_bv"]:+.1%}')
lo, hi = 0.06, 0.10
for _ in range(60):
    m = (lo + hi) / 2; lo, hi = (lo, m) if value(base, m)[1] < m - 0.05 else (m, hi)
out['coe_flip'] = m; print(f'  on the SELL line at a cost of equity of {m:.2%}')
for kq in (0.0723, 0.0825, 0.0917):
    out[f'k{kq}'] = value(base, kq)[1]; print(f'  cost of equity {kq:.2%}: {out[f"k{kq}"]:+.1%} vs line {kq-0.05:.1%}')
json.dump(out, open(os.path.join(HERE, '..', 'results', 'valuation_v26.json'), 'w'), indent=1)
