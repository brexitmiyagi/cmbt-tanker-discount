# the earnings test with no hindsight: at each date, only what the period market said then. a five-year-old Capesize
# valued on year 1 at the one-year time charter, then the three-year time charter rate for the rest of a 20-year
# life (the longest rate the market quotes), less $7,113 a day of opex (CMB.TECH's today; lower in the 2010s, which
# makes old valuations look a bit worse than they were), scrap at 24,000 ldt x $460, at 8%. price over that value is
# the signal. the outcome is the yearly change in the five-year-old price to the first observation 2 to 3.5 years
# later. 29 Intermodal weekly reports, 2015 to 2026 (data/broker_weekly_intermodal.csv). Capesize only: the tanker
# value tables didn't come through in the text of most of the older PDFs.
import math, os, json
from datetime import date
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
D = [r for r in rows('broker_weekly_intermodal.csv') if r['cape_5yr_value']]
d = lambda s: date.fromisoformat(s)
def value(y1, y3, r=0.08, years=20, opex=7113, scrap=24000 * 460 / 1e6):
    rates = [y1] + [y3] * (years - 1)
    return sum((x - opex) * 355 / 1e6 / (1 + r) ** (i + 0.5) for i, x in enumerate(rates)) + scrap / (1 + r) ** years
pts = []
for i, r in enumerate(D):
    px = float(r['cape_5yr_value']); v = value(float(r['cape_1y_tc']), float(r['cape_3y_tc']))
    fwd = None
    for s in D[i + 1:]:
        yrs = (d(s['report_date']) - d(r['report_date'])).days / 365.25
        if 2 <= yrs <= 3.5:
            fwd = (float(s['cape_5yr_value']) / px) ** (1 / yrs) - 1; break
    pts.append({'date': r['report_date'], 'price': px, 'value': v, 'ratio': px / max(v, 1), 'nb_ratio': px / float(r['cape_nb']), 'fwd': fwd})
for p in pts:
    f = f'{p["fwd"]:+.1%}/yr' if p['fwd'] is not None else 'n/a'
    print(f'{p["date"]} price ${p["price"]:5.1f}m  value on period rates ${p["value"]:6.1f}m  price/value {p["ratio"]:5.2f}  price/newbuild {p["nb_ratio"]:.2f}  next 2-3.5 yrs {f}')
T = [p for p in pts if p['fwd'] is not None and p['value'] > 0]
def corr(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    c = sum((x - ma) * (y - mb) for x, y in zip(a, b)); return c / math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))
lr = [math.log(p['ratio']) for p in T]; fw = [p['fwd'] for p in T]
print(f'\n{len(T)} dates with an outcome. correlation of log(price/value) with the next yearly price change: {corr(lr, fw):+.2f}')
print(f'correlation of price/newbuild with the next yearly price change: {corr([p["nb_ratio"] for p in T], fw):+.2f}')
s = sorted(T, key=lambda p: p['ratio']); h = len(s) // 2
lo, hi = s[:h], s[h:]
print(f'cheapest half (price/value {lo[0]["ratio"]:.2f}-{lo[-1]["ratio"]:.2f}): next price change {sum(p["fwd"] for p in lo)/len(lo):+.1%}/yr; dearest half ({hi[0]["ratio"]:.2f}-{hi[-1]["ratio"]:.2f}): {sum(p["fwd"] for p in hi)/len(hi):+.1%}/yr')
now = pts[-1]
rank = sum(1 for p in pts[:-2] if p['ratio'] < now['ratio']) / len(pts[:-2])
print(f'today ({now["date"]}): price/value {now["ratio"]:.2f}, dearer than {rank:.0%} of the earlier dates; price/newbuild {now["nb_ratio"]:.2f}')
json.dump(pts, open(os.path.join(HERE, '..', 'results', 'backtest_capesize.json'), 'w'), indent=1)

# the same test without the dates where period rates were below opex (value near zero makes the ratio meaningless)
T2 = [p for p in T if p['value'] > 5]
print(f'without the {len(T)-len(T2)} dates where period rates barely covered opex: correlation {corr([math.log(p["ratio"]) for p in T2], [p["fwd"] for p in T2]):+.2f} ({len(T2)} dates)')
# a straight line through price/newbuild and the next yearly change, and what it says at today's ratio
x = [p['nb_ratio'] for p in T]; mx, my = sum(x) / len(x), sum(fw) / len(fw)
b = sum((a - mx) * (c - my) for a, c in zip(x, fw)) / sum((a - mx) ** 2 for a in x); a0 = my - b * mx
print(f'fit: next yearly change = {a0:+.1%} {b:+.2f} x (price/newbuild); range of price/newbuild in the sample {min(x):.2f}-{max(x):.2f}')
print(f'at today\'s {now["nb_ratio"]:.2f} the line gives {a0 + b*now["nb_ratio"]:+.1%} a year, outside the range it was fitted on')
tk = [r for r in rows('broker_weekly_intermodal.csv') if r['vlcc_5yr_value']]
for r in tk:
    print(f'  {r["report_date"]} VLCC price/newbuild {float(r["vlcc_5yr_value"])/float(r["vlcc_nb"]):.2f}, Suezmax {float(r["suez_5yr_value"])/float(r["suez_nb"]):.2f}')
