# the same signal as backtest_capesize.py, done more carefully: a chain of observations at least a year apart, each
# outcome running only to the next link, so no two outcomes overlap. series: Intermodal (broker_weekly_intermodal.csv) and Allied plus two 2014 Intermodal reports
# (broker_weekly_allied_extra.csv). Allied gives tanker values for 2017-2020, which the Intermodal PDFs didn't.
# mixing two brokers adds noise; they agree within a few percent where both report the same week (Feb 2023).
import math, os, json
from datetime import date
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
obs = {'VLCC': {}, 'Suezmax': {}, 'Capesize': {}}
cols = {'VLCC': ('vlcc_5yr_value', 'vlcc_nb', 'vlcc_5yr'), 'Suezmax': ('suez_5yr_value', 'suez_nb', 'suez_5yr'), 'Capesize': ('cape_5yr_value', 'cape_nb', 'cape_5yr')}
for f, dk in (('broker_weekly_intermodal.csv', 'report_date'), ('broker_weekly_allied_extra.csv', 'data_date')):
    for r in rows(f):
        dt = date.fromisoformat(r[dk])
        for seg, (c1, c2, c3) in cols.items():
            v = r.get(c1) or r.get(c3)
            if v and r[c2]: obs[seg].setdefault(dt.year, []).append((dt, float(v), float(r[c2])))
pairs = []
for seg, by in obs.items():
    allo = sorted(x for v in by.values() for x in v)
    i = 0
    while i < len(allo):
        j = next((k for k in range(i + 1, len(allo)) if (allo[k][0] - allo[i][0]).days >= 365), None)
        if j is None: break
        oa, ob = allo[i], allo[j]; t = (ob[0] - oa[0]).days / 365.25
        if t <= 3.5 and oa[0].year < 2026:
            pairs.append((seg, oa[0], oa[1] / oa[2], (ob[1] / oa[1]) ** (1 / t) - 1, t))
        i = j
for p in pairs: print(f'  {p[0]:8s} {p[1]} price/newbuild {p[2]:.2f} -> next {p[4]:.1f} yrs {p[3]:+.1%}/yr')
def stats(P):
    x = [p[2] for p in P]; y = [p[3] for p in P]; n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y)); sxx = sum((a - mx) ** 2 for a in x); syy = sum((b - my) ** 2 for b in y)
    rr = sxy / math.sqrt(sxx * syy); t = rr * math.sqrt((n - 2) / (1 - rr * rr))
    return n, rr, t, sxy / sxx, my - sxy / sxx * mx
res = {}
for lab, P in (('all segments', pairs), ('Capesize', [p for p in pairs if p[0] == 'Capesize']), ('tankers', [p for p in pairs if p[0] != 'Capesize'])):
    n, rr, t, b, a = stats(P); res[lab] = {'n': n, 'r': rr, 't': t}
    print(f'{lab:13s}: {n} non-overlapping pairs, correlation {rr:+.2f}, t-stat {t:+.1f}; slope {b:+.2f} per point of price/newbuild')
hi = max(p[2] for p in pairs)
print(f'highest price/newbuild in these pairs {hi:.2f}; today VLCC 1.67, Suezmax 1.65, Capesize 1.02')
json.dump(res, open(os.path.join(HERE, '..', 'results', 'backtest_robust.json'), 'w'), indent=1)
