# is the war really in the price? the old test correlated the level of CMB.TECH's price with the level of Kalshi's
# reopening odds. both trended for eight months, and two trending series correlate whatever drives them. so test
# changes instead: regress each stock's return on the change in the odds, daily and weekly, and look at the days the
# odds moved most. then turn the slope into cents a share for a full reopening.
# odds: Kalshi KXHORMUZNORM-26MAR17, contracts B270101 (normal before 1 Jan 2027) and B270701 (before 1 Jul 2027),
# daily mid of bid and ask from Kalshi's public API. prices: Nasdaq daily closes.
import math, os, json
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
px = {r['date']: r for r in rows('daily_closes_nasdaq.csv')}
K = {}
for r in rows('kalshi_hormuz_daily.csv'):
    if r['mid_close']:
        K.setdefault(r['contract'], {})[r['date']] = float(r['mid_close'])
names = ('CMBT', 'DHT', 'FRO', 'SBLK')

def ols(x, y):
    n = len(x); mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x); sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    b = sxy / sxx; a = my - b * mx
    res = [yy - a - b * xx for xx, yy in zip(x, y)]
    se = math.sqrt(sum(e * e for e in res) / (n - 2) / sxx)
    r = sxy / math.sqrt(sxx * sum((v - my) ** 2 for v in y))
    return b, se, r, n

def odds_on(c, d):
    ks = [k for k in K[c] if k <= d]
    return K[c][max(ks)] if ks else None

days = sorted(d for d in px if d >= '2026-03-18')
out = {}
for c in ('B270101', 'B270701'):
    first = min(K[c])
    ds = [d for d in days if d >= first]
    print(f'contract {c} ({first} to {ds[-1]}):')
    for freq, step in (('daily', 1), ('weekly', 5)):
        sel = ds[::step]
        dx = [odds_on(c, sel[i]) - odds_on(c, sel[i - 1]) for i in range(1, len(sel))]
        for nme in names:
            dy = [math.log(float(px[sel[i]][nme]) / float(px[sel[i - 1]][nme])) for i in range(1, len(sel))]
            b, se, r, n = ols(dx, dy)
            out[(c, freq, nme)] = (b, se, r, n)
            print(f'  {freq:6s} {nme:4s}: a 10-point rise in reopening odds -> {b*0.10:+.2%} (t {b/se:+.1f}), correlation of changes {r:+.2f}, {n} obs')
    # levels, for comparison with the old test
    lv = [(odds_on(c, d), float(px[d]['CMBT'])) for d in ds]
    _, _, rl, _ = ols([a for a, _ in lv], [math.log(b) for _, b in lv])
    print(f'  levels (the old test), CMBT daily: correlation {rl:+.2f}')

# the ten biggest one-day moves in the odds (B270101 while it was still live, B270701 after), and what the stocks did
print('\nthe ten biggest one-day moves in the odds, and same-day returns:')
ev = []
for c in ('B270101', 'B270701'):
    ds = [d for d in days if d >= min(K[c])]
    for i in range(1, len(ds)):
        ev.append((odds_on(c, ds[i]) - odds_on(c, ds[i - 1]), ds[i], c, ds[i - 1]))
ev = sorted(ev, key=lambda e: -abs(e[0]))
seen, top = set(), []
for e in ev:
    if e[1] in seen: continue
    seen.add(e[1]); top.append(e)
    if len(top) == 10: break
agree = 0
for dxo, d, c, d0 in sorted(top, key=lambda e: e[1]):
    rr = {n: float(px[d][n]) / float(px[d0][n]) - 1 for n in names}
    agree += (rr['CMBT'] < 0) == (dxo > 0)
    print(f'  {d} {c} odds {dxo*100:+.0f} pts: ' + ', '.join(f'{n} {rr[n]:+.1%}' for n in names))
print(f'  CMBT moved the way a war-priced stock should (down when reopening odds rose) on {agree} of 10 days')

# cents a share for a full reopening: odds from today's level to 100%, at the daily slope on the live contract
c = 'B270701'
now = odds_on(c, days[-1]); p0 = float(px[days[-1]]['CMBT'])
b, se, _, _ = out[(c, 'daily', 'CMBT')]
move = math.exp(b * (1 - now)) - 1
lo, hi = math.exp((b - 2 * se) * (1 - now)) - 1, math.exp((b + 2 * se) * (1 - now)) - 1
print(f'\nfull reopening priced off the daily slope ({c} at {now:.0%} -> 100%): CMBT {move:+.1%} (${p0*move:+.2f} a share), two-standard-error band {lo:+.1%} to {hi:+.1%}')
bd, sed, _, _ = out[(c, 'daily', 'DHT')]
print(f'same for DHT: {math.exp(bd*(1-now))-1:+.1%}')
json.dump({'cmbt_full_reopen_pct': move, 'band_lo': lo, 'band_hi': hi, 'odds_now_B270701': now,
           'slope_daily_B270701_cmbt': b, 'se': se, 'agree_of_10': agree},
          open(os.path.join(HERE, '..', 'results', 'hormuz_sensitivity.json'), 'w'), indent=1)

# the old levels test, weekly, for all four, on the same footing as the change tests above (contract B270101)
wk = [r for r in rows('weekly_closes_nasdaq.csv') if r['week_ending'] >= '2026-03-20']
for nme in names:
    pts = [(odds_on('B270101', r['week_ending']), math.log(float(r[nme]))) for r in wk if odds_on('B270101', r['week_ending']) is not None]
    _, _, rl, n = ols([a for a, _ in pts], [b for _, b in pts])
    print(f'levels, weekly, {nme}: correlation {rl:+.2f} ({n} weeks)')
