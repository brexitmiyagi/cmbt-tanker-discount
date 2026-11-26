# does the market trade CMBT like a tanker stock or a dry bulk stock? weekly closes from Nasdaq, Jan 2025 to 24 Nov 2026.
from common import rows
import math
w = rows('weekly_closes_nasdaq.csv')
T = ['CMBT', 'FRO', 'DHT', 'SBLK', 'GNK']
px = {t: [float(r[t]) for r in w] for t in T}
dates = [r['week_ending'] for r in w]
ret = {t: [math.log(b / a) for a, b in zip(px[t], px[t][1:])] for t in T}

def corr(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    c = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    return c / math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))

def since(d):
    i = dates.index(d)
    return {t: px[t][-1] / px[t][i] - 1 for t in T}

for lab, d in (('since 3 Jan 2025', '2025-01-03'), ('since the war, 27 Feb 2026', '2026-02-27'), ('since the 9 Oct 2026 week', '2026-10-09')):
    s = since(d)
    print(lab + ': ' + ', '.join(f'{t} {v:+.1%}' for t, v in s.items()))
i0 = dates.index('2026-02-27')
for t in T[1:]:
    print(f'weekly return correlation with CMBT, full period {corr(ret["CMBT"], ret[t]):.2f}, since the war {corr(ret["CMBT"][i0:], ret[t][i0:]):.2f}  ({t})')
