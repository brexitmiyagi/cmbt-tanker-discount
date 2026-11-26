# does the period charter market justify the premium of a five-year-old ship over a newbuild?
# a buyer has two choices: buy the five-year-old now, or order a newbuild that delivers when the yards have a slot
# (3.7 years ahead, Danish Ship Finance, Nov 2026). the used ship earns for those 3.7 years and then is an 8.7-year-old
# ship next to a brand-new one. so it's worth: the earnings it can lock in on period charter for 3.7 years, plus what
# an 8.7-year-old is worth in 2030 if a newbuild still costs what it does today (age discount from Signal Ocean's 2023
# 10-year/5-year ratio, 0.755 per five years), all at 8%. opex from CMB.TECH (fixtures.csv; Aframax and MR use the
# Suezmax figure, Kamsarmax and Ultramax the Kamsarmax figure). if the price is above that, the premium is more than
# the charter market pays for.
import os, json
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
S = {r['segment']: r for r in rows('segments_2026-11-20.csv')}
op = {r['segment'].split()[0]: float(r['opex']) for r in rows('fixtures.csv')}
opex = {'VLCC': op['VLCC'], 'Suezmax': op['Suezmax'], 'Aframax': op['Suezmax'], 'MR': op['Suezmax'], 'Capesize': op['Capesize'], 'Kamsarmax': op['Kamsarmax/Panamax'] if 'Kamsarmax/Panamax' in op else op['Kamsarmax'], 'Ultramax': op['Kamsarmax/Panamax'] if 'Kamsarmax/Panamax' in op else op['Kamsarmax']}
WAIT, r, d5 = 3.7, 0.08, 0.755
def worth(seg, y1, y3, nb):
    pv = 0.0; t = 0.0
    while t < WAIT - 1e-9:
        dt = min(1.0, WAIT - t); rate = y1 if t == 0 else y3
        pv += (rate - opex[seg]) * 365 * 0.97 * dt / 1e6 / (1 + r) ** (t + dt / 2); t += dt
    resid = nb * d5 ** ((5 + WAIT) / 5)
    return pv + resid / (1 + r) ** WAIT, pv, resid
out = {}
for seg, s in S.items():
    px, nb, y1, y3 = (float(s[k]) for k in ('five_year_usd_m', 'newbuild_usd_m', 'tc_1y', 'tc_3y'))
    w3, e3, res = worth(seg, y3, y3, nb)          # three-year rate throughout
    w13, _, _ = worth(seg, y1, y3, nb)            # one-year rate for year 1, then three-year
    lo, hi = 0.0, 1e6                             # three-year rate the price needs
    for _ in range(60):
        m = (lo + hi) / 2; lo, hi = (m, hi) if worth(seg, m, m, nb)[0] < px else (lo, m)
    out[seg] = {'price': px, 'nb': nb, 'worth_3y': w3, 'worth_1y3y': w13, 'rate_needed': m, 'tc_3y': y3}
    print(f'{seg:9s} 5-yr ${px:6.1f}m vs newbuild ${nb:5.1f}m; on the 3-yr charter it\'s worth ${w3:6.1f}m ({px/w3-1:+.0%} premium over that), '
          f'${w13:6.1f}m with year 1 at the 1-yr rate ({px/w13-1:+.0%}); the price needs ${m:,.0f}/day for 3.7 yrs vs 3-yr TC ${y3:,.0f}')
json.dump(out, open(os.path.join(HERE, '..', 'results', 'charter_test.json'), 'w'), indent=1)
