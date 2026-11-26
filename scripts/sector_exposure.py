# who is most exposed if secondhand prices fall back toward newbuild prices. for each owner, fleet value by segment
# (ship counts x today's five-year-old value, or the stated split), the segment's price/newbuild ratio today
# (Intermodal, 20 Nov 2026), and the NAV hit if every ratio went back to 0.85, about the top of the 2014-2024 range
# for VLCC, Suezmax and Capesize (backtest_robust.py; the other segments have no history here). NAV = fleet value
# less net debt from peers_nav.csv; CMB.TECH uses its broker-value NAV. the price/NAV column uses 25 Nov closes.
# a rough screen: five-year-old values stand in for whole fleets of mixed ages.
import os, json
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
S = {r['segment']: r for r in rows('segments_2026-11-20.csv')}
ratio = {k: float(v['five_year_usd_m']) / float(v['newbuild_usd_m']) for k, v in S.items()}
mix = {}
for r in rows('fleet_mix_2026.csv'): mix.setdefault(r['owner'], []).append(r)
nav = {r['ticker']: r for r in rows('peers_nav.csv')}
px = {r['ticker']: float(r['close_2026_11_25']) for r in rows('prices_2026-11-25.csv')}
TARGET = 0.85
out = {}
for o, segs in mix.items():
    if o == 'CMBT':
        w = {'VLCC': 3128 * 0.5, 'Suezmax': 3128 * 0.5}
        dry = {s['segment']: float(s['ships']) * float(S[s['segment']]['five_year_usd_m']) for s in segs if s['basis'] == 'ships'}
        for k, v in dry.items(): w[k] = 7017 * v / sum(dry.values())
        fleet, n = 10145.0, 30.67 * 290.169769; mc = px['CMBT'] * 290.169769
    else:
        fleet = float(nav[o]['fleet_value_usd_m']); n = fleet - float(nav[o]['net_debt_usd_m']); mc = px[o] * float(nav[o]['shares_m'])
        if o == 'SBLK':
            w = {'Capesize': 0.40 * fleet}
            rest = {s['segment']: float(s['ships']) * float(S[s['segment']]['five_year_usd_m']) for s in segs if s['segment'] != 'Capesize'}
            for k, v in rest.items(): w[k] = 0.60 * fleet * v / sum(rest.values())
        else:
            raw = {s['segment']: float(s['ships']) * float(S[s['segment']]['five_year_usd_m']) for s in segs}
            w = {k: fleet * v / sum(raw.values()) for k, v in raw.items()}
    hit = sum(v * (1 - TARGET / ratio[k]) for k, v in w.items() if ratio[k] > TARGET)
    ch = json.load(open(os.path.join(HERE, '..', 'results', 'charter_test.json')))
    chit = sum(v * max(0.0, 1 - ch[k]['worth_1y3y'] / ch[k]['price']) for k, v in w.items())
    wr = sum(v * ratio[k] for k, v in w.items()) / fleet
    out[o] = {'fleet_ratio': wr, 'nav_hit': hit / n, 'charter_hit': chit / n, 'gearing': fleet / n, 'p_nav': mc / n}
print('# charter hit: NAV lost if each segment five-year-old price fell to what the charter market pays for (charter_test.py,')
print('# year 1 at the one-year rate, then the three-year rate), segment by segment, never below zero')
for o, v in sorted(out.items(), key=lambda x: -x[1]['charter_hit']):
    print(f'{o:5s} fleet-weighted price/newbuild {v["fleet_ratio"]:.2f}; fleet/NAV {v["gearing"]:.2f}; NAV hit if ratios go to {TARGET}: {-v["nav_hit"]:.0%}; if prices fall to what charters pay for: {-v["charter_hit"]:.0%}; price/NAV {v["p_nav"]:.2f}')
json.dump(out, open(os.path.join(HERE, '..', 'results', 'sector_exposure.json'), 'w'), indent=1)
