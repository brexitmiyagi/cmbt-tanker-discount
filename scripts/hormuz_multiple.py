# does CMB.TECH's price carry the war? weekly closes against Kalshi's odds that Hormuz traffic is back to normal
# before 1 January 2027 (contract KXHORMUZNORM-26MAR17-B270101, daily mid of bid and ask, from Kalshi's public API).
# if the price rises as the odds of a reopening fall, a reopening takes it back.
import math, os
from common import rows
k = {r['date']: float(r['mid_close']) for r in rows('kalshi_hormuz_daily.csv') if r['contract'] == 'B270101' and r['mid_close']}
w = [r for r in rows('weekly_closes_nasdaq.csv') if r['week_ending'] >= '2026-03-20']
def odds(d):
    ks = sorted(x for x in k if x <= d)
    return k[ks[-1]] if ks else None
pts = [(r['week_ending'], odds(r['week_ending']), float(r['CMBT']), float(r['DHT']), float(r['SBLK'])) for r in w]
pts = [p for p in pts if p[1] is not None]
def corr(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    c = sum((x - ma) * (y - mb) for x, y in zip(a, b)); return c / math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))
o = [p[1] for p in pts]
for i, n in ((2, 'CMBT'), (3, 'DHT'), (4, 'SBLK')):
    print(f'{n}: correlation of log price with reopening odds, weekly since March: {corr(o, [math.log(p[i]) for p in pts]):+.2f}')
# weekly changes: regression of log return on change in odds
for i, n in ((2, 'CMBT'), (3, 'DHT'), (4, 'SBLK')):
    dx = [pts[j][1] - pts[j - 1][1] for j in range(1, len(pts))]; dy = [math.log(pts[j][i] / pts[j - 1][i]) for j in range(1, len(pts))]
    mx, my = sum(dx) / len(dx), sum(dy) / len(dy)
    b = sum((x - mx) * (y - my) for x, y in zip(dx, dy)) / sum((x - mx) ** 2 for x in dx)
    print(f'{n}: a 10-point fall in reopening odds came with a {-b*0.10:+.1%} weekly move on average ({len(dx)} weeks)')
first, last = pts[0], pts[-1]
print(f'odds {first[1]:.0%} on {first[0]} -> {last[1]:.0%} on {last[0]}; CMBT ${first[2]:.2f} -> ${last[2]:.2f}')
print('CMB.TECH price/NAV on the broker basis: 0.40 at end-2025 (before the war), 0.55 at 30 Jun (odds about 71%), 0.62 at 30 Sep (odds about 16%), 0.57 on 24 Nov (odds 2%, September NAV)')
