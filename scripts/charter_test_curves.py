# the charter test again, with each segment's own age curve instead of one VLCC curve for everything.
# charter_test.py valued the 8.7-year-old in 2030 off Signal Ocean's 2023 VLCC ratio (0.755 per five years). for a
# Capesize that residual is most of the answer, so it matters which curve. here the 10-year/5-year ratio comes from
# the same broker for each segment: Compass 16 Nov 2026, with KOBC 1 Oct 2026 as a second house. Intermodal only
# publishes five-year-old values, so it can't give a curve. Aframax and MR borrow the Suezmax curve, Ultramax the
# Kamsarmax one (no published 10-year value). then: how much does the answer move with the residual, what the
# Capesize premium looks like on the forward curve instead of the three-year charter, and what yearly drift in
# five-year-old prices closes each gap by the time a newbuild ordered today delivers.
import os, json
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
S = {r['segment']: r for r in rows('segments_2026-11-20.csv')}
op = {r['segment'].split()[0]: float(r['opex']) for r in rows('fixtures.csv')}
opex = {'VLCC': op['VLCC'], 'Suezmax': op['Suezmax'], 'Aframax': op['Suezmax'], 'MR': op['Suezmax'],
        'Capesize': op['Capesize'], 'Kamsarmax': op['Kamsarmax/Panamax'], 'Ultramax': op['Kamsarmax/Panamax']}
WAIT, R = 3.7, 0.08
curves = {}
for c in rows('age_curves_2026-11.csv'):
    curves.setdefault(c['source'].split()[0], {})[c['segment']] = float(c['ten_year_usd_m']) / float(c['five_year_usd_m'])
borrow = {'Aframax': 'Suezmax', 'MR': 'Suezmax', 'Ultramax': 'Kamsarmax'}
def d5(house, seg): return curves[house][borrow.get(seg, seg)]

def worth(seg, rates, nb, d):
    # rates: one $/day figure per year, the last one carried to the end of the wait
    pv, t, i = 0.0, 0.0, 0
    while t < WAIT - 1e-9:
        dt = min(1.0, WAIT - t); x = rates[min(i, len(rates) - 1)]
        pv += (x - opex[seg]) * 365 * 0.97 * dt / 1e6 / (1 + R) ** (t + dt / 2); t += dt; i += 1
    resid = nb * d ** ((5 + WAIT) / 5)
    return pv + resid / (1 + R) ** WAIT, pv, resid / (1 + R) ** WAIT

out = {'curves': curves, 'segments': {}}
print('10-year/5-year value ratios:', {h: {k: round(v, 3) for k, v in c.items()} for h, c in curves.items()}, '(the old test used 0.755 for all)')
for seg, s in S.items():
    px, nb, y1, y3 = (float(s[k]) for k in ('five_year_usd_m', 'newbuild_usd_m', 'tc_1y', 'tc_3y'))
    res = {}
    for house in ('Compass', 'KOBC'):
        w, pv, rd = worth(seg, [y1, y3], nb, d5(house, seg))
        res[house] = {'worth': w, 'charters': pv, 'residual': rd, 'premium': px / w - 1}
    w, pv, rd = res['Compass']['worth'], res['Compass']['charters'], res['Compass']['residual']
    # how much the answer moves with the residual: the residual value 10% either way
    lo = px / (w - 0.1 * rd) - 1; hi = px / (w + 0.1 * rd) - 1
    # the yearly fall in five-year-old prices that brings price to worth by the time a newbuild ordered today arrives
    drift = (w / px) ** (1 / WAIT) - 1
    out['segments'][seg] = {'price': px, 'nb': nb, **{f'{h}_{k}': v for h, d in res.items() for k, v in d.items()},
                            'residual_share': rd / w, 'premium_resid_minus10': lo, 'premium_resid_plus10': hi, 'drift': min(0.0, drift), 'drift_raw': drift}
    print(f'{seg:9s} price ${px:6.1f}m; worth ${w:6.1f}m on Compass curve ({px/w-1:+.0%}), ${res["KOBC"]["worth"]:6.1f}m on KOBC ({res["KOBC"]["premium"]:+.0%}); '
          f'residual is {rd/w:.0%} of worth; residual -/+10% gives {lo:+.0%} / {hi:+.0%}; drift to close by 2030 {drift:+.1%}/yr')

# the Capesize on the forward curve instead of one three-year quote
ffa = {r['period']: float(r['usd_day']) for r in rows('capesize_ffa_2026-10-26.csv') if r['period'].startswith('Cal')}
cs = S['Capesize']; px, nb = float(cs['five_year_usd_m']), float(cs['newbuild_usd_m'])
f_rates = [ffa['Cal 2027'], ffa['Cal 2028'], ffa['Cal 2029']]
wf, pvf, rdf = worth('Capesize', f_rates, nb, d5('Compass', 'Capesize'))
wf1, _, _ = worth('Capesize', [float(cs['tc_1y'])] + f_rates[1:], nb, d5('Compass', 'Capesize'))
avg = (f_rates[0] + f_rates[1] + f_rates[2] * 1.7) / 3.7
lo, hi = 0.0, 2e5
for _ in range(60):
    m = (lo + hi) / 2; lo, hi = (m, hi) if worth('Capesize', [m], nb, d5('Compass', 'Capesize'))[0] < px else (lo, m)
out['capesize_ffa'] = {'worth': wf, 'premium': px / wf - 1, 'worth_y1_at_1yr_tc': wf1, 'premium_y1': px / wf1 - 1, 'ffa_avg': avg, 'rate_needed': m}
print(f'Capesize on the FFA curve (Cal27 ${f_rates[0]:,.0f}, Cal28 ${f_rates[1]:,.0f}, Cal29 ${f_rates[2]:,.0f}; 3.7-yr average ${avg:,.0f}): worth ${wf:.1f}m, '
      f'price {px/wf-1:+.0%} above it; with year 1 at the ${float(cs["tc_1y"]):,.0f} one-year rate, {px/wf1-1:+.0%}. the price needs ${m:,.0f}/day flat for 3.7 years')

# CMB.TECH: the drift in its fleet's five-year-old prices that closes the gaps, weighted by fleet value
# tankers half VLCC half Suezmax ($3,128m); dry bulk $7,017m split by ship count at five-year-old values
# (82 Newcastlemax/Capesize, 30 Kamsarmax/Panamax, fleet_mix_2026.csv)
seg = out['segments']
dry = {'Capesize': 82 * float(S['Capesize']['five_year_usd_m']), 'Kamsarmax': 30 * float(S['Kamsarmax']['five_year_usd_m'])}
w = {'VLCC': 3128 * 0.5, 'Suezmax': 3128 * 0.5, **{k: 7017 * v / sum(dry.values()) for k, v in dry.items()}}
tot = sum(w.values())
def fleet_drift(get): return sum(w[k] * get(k) for k in w) / tot
d_compass = fleet_drift(lambda k: seg[k]['drift'])
d_kobc = fleet_drift(lambda k: min(0.0, (1 / (1 + seg[k]['KOBC_premium'])) ** (1 / WAIT) - 1))
d_ffa = fleet_drift(lambda k: min(0.0, (1 / (1 + out['capesize_ffa']['premium_y1'])) ** (1 / WAIT) - 1) if k == 'Capesize' else seg[k]['drift'])
d_bulk = sum(w[k] * seg[k]['drift'] for k in ('Capesize', 'Kamsarmax')) / sum(w[k] for k in ('Capesize', 'Kamsarmax'))
bulk_gap = sum(w[k] * seg[k]['Compass_premium'] / (1 + seg[k]['Compass_premium']) for k in ('Capesize', 'Kamsarmax')) / 7017
out['fleet'] = {'weights': w, 'drift_compass': d_compass, 'drift_kobc': d_kobc, 'drift_ffa': d_ffa, 'drift_bulkers': d_bulk, 'bulker_value_above_charters': bulk_gap}
print(f'CMB.TECH fleet: bulkers {bulk_gap:.0%} of their value above what charters pay for; closing it by 2030 is {d_bulk:+.1%}/yr on the bulkers, '
      f'{d_compass:+.1%}/yr across the fleet (tankers at zero where charters cover them); KOBC curve {d_kobc:+.1%}; Capesize on the FFA curve {d_ffa:+.1%}')
json.dump(out, open(os.path.join(HERE, '..', 'results', 'charter_test_curves.json'), 'w'), indent=1)
