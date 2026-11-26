# the cost of equity uses a beta of 0.65 from one year of daily returns, and that year was mostly the war. check it
# against the months before the war and against peers, daily and weekly (weekly is less hurt by stale prices).
# Nasdaq serves about 18 months of daily history, so the pre-war window is 27 May 2025 to 27 Feb 2026.
import math, os, json
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
P = rows('daily_closes_nasdaq.csv')
def beta(a, b, name, step):
    s = [r for r in P if a <= r['date'] <= b][::step]
    x = [math.log(float(s[i]['SPY']) / float(s[i - 1]['SPY'])) for i in range(1, len(s))]
    y = [math.log(float(s[i][name]) / float(s[i - 1][name])) for i in range(1, len(s))]
    mx, my = sum(x) / len(x), sum(y) / len(y)
    return sum((u - mx) * (v - my) for u, v in zip(x, y)) / sum((u - mx) ** 2 for u in x), len(x)
res = {}
for lab, a, b in (('before the war', '2025-05-27', '2026-02-27'), ('war', '2026-02-27', '2026-11-24'), ('whole 18 months', '2025-05-27', '2026-11-24')):
    for step, fl in ((1, 'daily'), (5, 'weekly')):
        bs = {n: beta(a, b, n, step) for n in ('CMBT', 'DHT', 'FRO', 'SBLK')}
        res[f'{lab}|{fl}'] = {n: v[0] for n, v in bs.items()}
        print(f'{lab:16s} {fl:6s}: ' + ', '.join(f'{n} {v[0]:.2f}' for n, v in bs.items()) + f'  ({bs["CMBT"][1]} obs)')
pw = res['before the war|weekly']
peer = sum(pw[n] for n in ('DHT', 'FRO', 'SBLK')) / 3
print(f'pre-war weekly: CMBT {pw["CMBT"]:.2f}, peer average {peer:.2f}')
for bb in (0.65, pw['CMBT'], peer, 1.0):
    print(f'beta {bb:.2f} -> cost of equity {4.91 + bb * 5:.1f}% (10-year 4.91% + beta x 5%)')
json.dump(res, open(os.path.join(HERE, '..', 'results', 'beta_check.json'), 'w'), indent=1)
