# sale gains in the normal year, forward-looking instead of zero. gain_decomposition.py shows 92-124% of the
# 2023-26 gains came from ship prices rising. so I scale normal-year gains with the yearly drift in ship prices,
# calibrated on the last cycle: the predecessors' routine gains added (7.9% - 6.8%) of return on equity while a
# five-year-old VLCC went from $76.2m (Feb 2016) to $98m (Feb 2023) on Signal Ocean's numbers.
import json, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
R = lambda f: json.load(open(os.path.join(HERE, '..', 'results', f)))
rw, ms, hp = R('roe_windows.json'), R('model_summary.json'), R('payoff_both_routes.json')
rc = rw['routine_common']
pred_routine = (rc['Euronav'] * 3128 + rc['Golden Ocean'] * 7017) / 10145
strict = (0.067 * 3128 + 0.068 * 7017) / 10145
drift_hist = (98 / 76.2) ** (1 / 7) - 1
k = (pred_routine - strict) / drift_hist
print(f'calibration: routine gains added {pred_routine-strict:.1%} of ROE while ship prices drifted {drift_hist:+.1%} a year -> {k:.2f} points of ROE per point of yearly drift')
sh, px = 290.169769, 17.54; dist = hp['dist12']
f27, f28, q4 = ms['fcf27'] / sh, ms['fcf28'] / sh, ms['fcf_q4_26'] / sh; book = ms['eq28'] / sh
asset_px = 0.25 * hp['best'] + 0.5 * hp['base'] + 0.25 * hp['bear_avg']
def er(r, kk=0.0816):
    pv3 = q4 / (1 + kk) ** 0.125 + f27 / (1 + kk) ** 0.625 + f28 / (1 + kk) ** 1.625
    v = pv3 + (r * book / kk) / (1 + kk) ** 1.625
    return ((asset_px + v * (1 + kk) - dist) / 2 + dist) / px - 1
# where ship prices go from here: today a five-year-old VLCC is about $215m (Compass, 16 Nov 2026) against $98m in
# Feb 2023 and $76.2m in Feb 2016
for lab, d in (('prices keep rising as 2016-23', drift_hist), ('newbuild cost inflation +2%', 0.02), ('flat from end-2028', 0.0),
               ('drift down -2% a year', -0.02), ('back to Feb 2023 levels over ten years', (98 / 215) ** 0.1 - 1)):
    r = strict + k * d
    print(f'{lab:40s} drift {d:+.1%}/yr -> normal-year return {r:.1%} -> expected 12-month total return {er(r):+.1%} (SELL line 3.2%)')
