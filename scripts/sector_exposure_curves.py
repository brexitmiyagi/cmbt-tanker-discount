# sector_exposure.py again, on the segment age curves (charter_test_curves.py, Compass) instead of the one VLCC
# curve. NAV hit if each segment's five-year-old price fell to what the charter market pays for (year 1 at the
# one-year rate, then the three-year rate), never below zero. same fleet splits and NAVs as sector_exposure.py.
import os, json
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
S = {r['segment']: r for r in rows('segments_2026-11-20.csv')}
ct = json.load(open(os.path.join(HERE, '..', 'results', 'charter_test_curves.json')))['segments']
mix = {}
for r in rows('fleet_mix_2026.csv'): mix.setdefault(r['owner'], []).append(r)
nav = {r['ticker']: r for r in rows('peers_nav.csv')}
px = {r['ticker']: float(r['close_2026_11_25']) for r in rows('prices_2026-11-25.csv')}
out = {}
for o, segs in mix.items():
    if o == 'CMBT':
        w = {'VLCC': 3128 * 0.5, 'Suezmax': 3128 * 0.5}
        dry = {s['segment']: float(s['ships']) * float(S[s['segment']]['five_year_usd_m']) for s in segs if s['basis'] == 'ships'}
        for k, v in dry.items(): w[k] = 7017 * v / sum(dry.values())
        n = 30.67 * 290.169769; mc = px['CMBT'] * 290.169769
    else:
        fleet = float(nav[o]['fleet_value_usd_m']); n = fleet - float(nav[o]['net_debt_usd_m']); mc = px[o] * float(nav[o]['shares_m'])
        if o == 'SBLK':
            w = {'Capesize': 0.40 * fleet}
            rest = {s['segment']: float(s['ships']) * float(S[s['segment']]['five_year_usd_m']) for s in segs if s['segment'] != 'Capesize'}
            for k, v in rest.items(): w[k] = 0.60 * fleet * v / sum(rest.values())
        else:
            raw = {s['segment']: float(s['ships']) * float(S[s['segment']]['five_year_usd_m']) for s in segs}
            w = {k: fleet * v / sum(raw.values()) for k, v in raw.items()}
    hit = sum(v * max(0.0, 1 - ct[k]['Compass_worth'] / ct[k]['price']) for k, v in w.items())
    out[o] = {'charter_hit': hit / n, 'p_nav': mc / n, 'p_nav_after': mc / (n - hit)}
for o, v in sorted(out.items(), key=lambda x: -x[1]['charter_hit']):
    print(f'{o:5s} NAV hit if prices fell to what charters pay for: {-v["charter_hit"]:.0%}; price/NAV {v["p_nav"]:.2f} now, {v["p_nav_after"]:.2f} after')
json.dump(out, open(os.path.join(HERE, '..', 'results', 'sector_exposure_curves.json'), 'w'), indent=1)
