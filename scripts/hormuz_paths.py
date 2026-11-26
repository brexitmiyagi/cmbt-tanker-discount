# four Hormuz paths on ONE basis:
#   NAV = book equity at end-2027 (model.py) + the broker uplift (30 Sep fleet value $12,186m less vessels at book),
#         + the tanker value change in that path (on the $3,128m charter-free tanker value)
#         + the retained half of the change in 2027 tanker profit vs the company deck
#         - the charter markdown for that path (what the chartered ships give up against that path's market rates)
#   value a share = NAV x CMB.TECH's own price/NAV on the same broker basis (best observed: 0.62x on 30 Sep 2026)
# the broker basis is the one I could check independently (fleet_valuation.py: dry bulk within 1.4%).
import json, os
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
sh = 290.169769
ms = json.load(open(os.path.join(HERE, '..', 'results', 'model_summary.json')))
eq27 = ms['eq27']
uplift = 12186 - 6780.215
TANK, DRY = 3128.0, 7017.0
m = {r['item']: float(r['value']) for r in rows('market_rates_2026-11-16.csv')}
cut = (m['tanker_fmv_2025_12_31_usd_m'] / m['tanker_ships_2025_12_31']) / (m['tanker_fmv_2026_09_30_usd_m'] / m['tanker_ships_2026_09_30']) - 1
# end-2027 values look at 2028, which is halfway back to through-cycle rates, so dry bulk values go halfway back to
# their end-2025 level per ship (fleet mix differs, so it's approximate)
dry_cut = 0.5 * ((m['drybulk_fmv_2025_12_31_usd_m'] / m['drybulk_ships_2025_12_31']) / (m['drybulk_fmv_2026_09_30_usd_m'] / m['drybulk_ships_2026_09_30']) - 1)
days = {'VLCC': 1633, 'Suezmax': 2839}
deck = {'VLCC': 122500, 'Suezmax': 77500}
_t = rows('cmbt_tanker_tce_2025.csv')
pre = {'VLCC': sum(float(r['vlcc_spot']) for r in _t) / 4, 'Suezmax': sum(float(r['suezmax_spot']) for r in _t) / 4}   # 2025 average
tc1y = {'VLCC': 234000, 'Suezmax': 136250}

def pv(years, rate, segments, r=0.08):
    # segments: list of (length in years, market rate); after the last segment the pre-war rate applies
    out, t = 0.0, 0.0
    sched = []
    for ln, mk in segments:
        sched.append((t, t + ln, mk)); t += ln
    t = 0.0
    while t < years - 1e-9:
        step = min(0.25, years - t)
        mid = t + step / 2
        mk = next((x for a, b, x in sched if a <= mid < b), None)
        out += ((mk if mk is not None else rate[1]) - rate[0]) * 365 * step / 1e6 / (1 + r) ** mid
        t += step
    return out

import datetime as _dt
CHARTERS = os.environ.get('CHARTERS', 'actual')   # the real book from investor relations (cleared to cite 26 Nov 2026)
def _book():
    # the actual Suezmax charter book (investor relations, 26 Nov 2026): years left from 30 Nov 2026, with the
    # charterer's extension options assumed exercised (they are worth exercising at any rate above the base).
    t0 = _dt.date(2026, 11, 30); out = []
    for r in rows('suezmax_charter_book_ir_2026-11-26.csv'):
        end = _dt.date.fromisoformat(r['end']); left = max((end - t0).days / 365.25, 0) + float(r['options_years'])
        out.append((r['vessel'], left, 'profit' in r['contract']))
    return out
def marks(path, unknown_years=3.0, split=0.5):
    if CHARTERS == 'actual':
        sz = {'A': [(0.25, 136250)], 'B': [(0.75, 136250)], 'C': [(1.0, 77500)], 'D': [(1.0, 136250), (1.0, 77500)]}[path]
        vl = {'A': [(0.25, 234000)], 'B': [(0.6, 234000)], 'C': [(0.6, 122500)], 'D': [(0.6, 234000)]}[path]
        s = sum((1 - split if ps else 1.0) * pv(left, (32986, pre['Suezmax']), sz) for _, left, ps in _book())
        return s + pv(0.6, (85623, pre['VLCC']), vl)
    return _marks_assumed(path, unknown_years)
def _marks_assumed(path, unknown_years=3.0):
    # 10 chartered Suezmaxes: Cap Grace and Cap Joseph ~9.4 years left, the other 8 unknown; average $32,986/day.
    # 1 VLCC on a 1-year charter, ~0.6 years left; VLCC charter average $85,623.
    sz = {'A': [(0.25, 136250)], 'B': [(0.75, 136250)], 'C': [(1.0, 77500)], 'D': [(1.0, 136250), (1.0, 77500)]}[path]
    vl = {'A': [(0.25, 234000)], 'B': [(0.6, 234000)], 'C': [(0.6, 122500)], 'D': [(0.6, 234000)]}[path]
    s = 2 * pv(9.4, (32986, pre['Suezmax']), sz) + 8 * pv(unknown_years, (32986, pre['Suezmax']), sz)
    v = pv(0.6, (85623, pre['VLCC']), vl)
    return s + v

def dprofit(frac_pre=0.0, frac_tc=0.0):
    return sum(days[k] * (frac_pre * (pre[k] - deck[k]) + frac_tc * (tc1y[k] - deck[k])) for k in days) / 1e6

P = {'A': ('A. Reopens in Q1 2027', dprofit(frac_pre=0.75), cut),
     'B': ('B. Reopens in H2 2027', dprofit(frac_pre=0.5), cut),
     'C': ('C. Opens, mines and attacks keep risk high', 0.0, cut / 2),
     'D': ('D. Stays shut through 2027', dprofit(frac_tc=1.0), 0.0)}
MULT = 0.62
print(f'dry bulk value change by end-2027 {dry_cut:+.1%} (${dry_cut*DRY:,.0f}m)'); print(f'pre-war tanker value per ship vs 30 Sep: {cut:+.0%}; broker uplift ${uplift:,.1f}m; book equity end-2027 ${eq27:,.1f}m')
res = {}
for k, (name, dp, c) in P.items():
    mk = {u: marks(k, u) for u in (1.0, 3.0, 5.0)}
    nav = eq27 + uplift + c * TANK + 0.5 * dp - mk[3.0] + dry_cut * DRY
    navb = nav - (0.2 + dry_cut) * DRY   # bear: dry bulk values 20% below 30 Sep in total
    res[k + '_marks_range'] = (mk[1.0], mk[5.0])
    res[k] = {'name': name, 'dprofit': dp, 'cut': c, 'marks': mk[3.0], 'nav': nav, 'value': MULT * nav / sh, 'bear': MULT * navb / sh,
              'sens': {x: x * nav / sh for x in (0.55, 0.62, 0.70)}}
    print(f'{name:45s} tanker profit {dp:+5.0f}m, values {c:+.0%}, charter marks ${mk[3.0]:.0f}m (1-5 yrs left: ${mk[1.0]:.0f}m-${mk[5.0]:.0f}m), NAV ${nav/sh:.2f}; value ${MULT*nav/sh:.2f} (0.55x ${0.55*nav/sh:.2f}, 0.70x ${0.70*nav/sh:.2f}); dry bulk -20%: ${MULT*navb/sh:.2f}')
W = {'mine (Sameer)': {'A': .20, 'B': .25, 'C': .25, 'D': .30},
     # read 25 Nov 2026 ~15:00 UTC. both settle on the IMF PortWatch 7-day average of Hormuz transit calls reaching 60.
     # A = normal by end-March 2027, B = by end-2027 but not by March, D = not by end-2027. no market prices path C.
     'Polymarket ladder (Mar 31 12.5%, Dec 31 2027 35.5%)': {'A': .125, 'B': .23, 'C': 0, 'D': .645},
     'Kalshi (before Apr 1 2027 12%, before Jan 1 2028 33%)': {'A': .12, 'B': .21, 'C': 0, 'D': .67}}
for wn, w in W.items():
    v = sum(w[k] * res[k]['value'] for k in 'ABCD' if isinstance(res[k], dict)); b = sum(w[k] * res[k]['bear'] for k in 'ABCD')
    s55 = sum(w[k] * res[k]['sens'][0.55] for k in 'ABCD'); s70 = sum(w[k] * res[k]['sens'][0.70] for k in 'ABCD')
    print(f'weights {wn:32s}: value ${v:.2f} (0.55x ${s55:.2f}, 0.70x ${s70:.2f}); bear (dry bulk -20%) ${b:.2f}')
    res['w_' + wn] = {'value': v, 'bear': b, 's55': s55, 's70': s70}
# reverse: at 0.62x, what tanker value change does $17.54 imply, with path C's charter marks and the deck rates?
need = 17.54 / MULT * sh - (eq27 + uplift - res['C']['marks'] + dry_cut * DRY)
res['dry_cut'] = dry_cut
print(f'at 0.62x forward NAV (deck rates, path C charter marks), $17.54 implies tanker values {need/TANK:+.0%} vs 30 Sep')
json.dump(res, open(os.path.join(HERE, '..', 'results', 'hormuz_paths.json'), 'w'))

# sensitivity grid on the same basis: rows = 2027 Capesize rate (whole dry bulk deck scaled with it; half the extra
# profit retained, as in the paths), columns = tanker value change; path C charter marks; 0.62x.
slope = {'Newcastlemax': 15.51, 'Capesize': 11.26, 'Kamsarmax': 10.56}
dk = {'Newcastlemax': 40608, 'Capesize': 31975, 'Kamsarmax': 17050}
cols = [-0.4, -0.3, -0.2, -0.1, 0.0]
print('grid, $ a share (rows: 2027 Capesize $/day; columns: tanker values vs 30 Sep)')
print('  cape $/day ' + ' '.join(f'{c:>7.0%}' for c in cols))
grid = {}
for cape in (25000, 30000, 35000, 40000, 45000):
    f = cape / dk['Capesize'] - 1
    dp = sum(slope[k] * dk[k] * f / 1000 for k in slope)
    line = [MULT * (eq27 + uplift - res['C']['marks'] + dry_cut * DRY + c * TANK + 0.5 * dp) / sh for c in cols]
    grid[cape] = line
    print(f'  {cape:>10,} ' + ' '.join(f'{v:7.2f}' for v in line))
json.dump(res, open(os.path.join(HERE, '..', 'results', 'hormuz_paths.json'), 'w'))
