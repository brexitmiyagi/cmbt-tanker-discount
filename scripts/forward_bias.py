# are period rates biased forecasts of what ships later earn? for every Intermodal report with three full years of
# outcome behind it (report dates to end-2022), compare the three-year time charter rate quoted that day with what
# was actually earned over the next three years. tankers: Euronav / CMB.TECH realised spot TCE by calendar year
# (data/euronav_realised_rates.csv), each year weighted by its overlap with the window. Capesize: no realised series
# here, so the average of the one-year time charter quotes in later Intermodal reports inside the window stands in.
# that is a weaker test (a quote, not earnings). the published research (Kavussanos and Nomikos 1999; Kavussanos,
# Visvikis and Menachof 2005) finds freight forward prices unbiased one or two months out and biased at three months
# in some routes; nothing I found tests three-year period rates, which is what my 2028 call is about.
import os, json, datetime as dt
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
R = rows('broker_weekly_intermodal.csv')
real = {int(r['year']): r for r in rows('euronav_realised_rates.csv')}
d = lambda s: dt.date.fromisoformat(s)
def realised(seg, t0):
    t1 = dt.date(t0.year + 3, t0.month, min(t0.day, 28)); tot = w = 0.0
    for y in range(t0.year, t1.year + 1):
        a, b = max(t0, dt.date(y, 1, 1)), min(t1, dt.date(y, 12, 31))
        if b <= a: continue
        if y not in real: return None
        ww = (b - a).days; tot += ww * float(real[y][f'{seg}_spot']); w += ww
    return tot / w
def later_quotes(col, t0):
    t1 = dt.date(t0.year + 3, t0.month, min(t0.day, 28))
    q = [float(r[col]) for r in R if t0 < d(r['report_date']) <= t1 and r[col]]
    return sum(q) / len(q) if len(q) >= 3 else None
out = {}
for seg, col3, kind in (('vlcc', 'vlcc_3y_tc', 'realised'), ('suezmax', 'suez_3y_tc', 'realised'), ('capesize', 'cape_3y_tc', 'later 1-yr quotes')):
    pts = []
    for r in R:
        t0 = d(r['report_date'])
        if t0 > dt.date(2022, 12, 31): continue
        x = realised(seg, t0) if kind == 'realised' else later_quotes('cape_1y_tc', t0)
        if x: pts.append((r['report_date'], float(r[col3]), x))
    ratio = [x / q for _, q, x in pts]
    srt = sorted(pts, key=lambda p: p[1]); n = len(srt) // 3
    hi = [x / q for _, q, x in srt[-n:]]; lo = [x / q for _, q, x in srt[:n]]
    over = sum(1 for v in ratio if v < 1)
    out[seg] = {'n': len(pts), 'mean_ratio': sum(ratio) / len(ratio), 'high_third': sum(hi) / len(hi), 'low_third': sum(lo) / len(lo), 'overshoots': over,
                'points': pts}
    print(f'{seg:9s} ({kind}, {len(pts)} reports 2015-2022): later earnings / 3-yr rate quoted = {out[seg]["mean_ratio"]:.2f} on average; '
          f'when the 3-yr rate was in its top third {out[seg]["high_third"]:.2f}, bottom third {out[seg]["low_third"]:.2f}; '
          f'the 3-yr rate overshot what was earned in {over} of {len(pts)}')
json.dump(out, open(os.path.join(HERE, '..', 'results', 'forward_bias.json'), 'w'), indent=1)
