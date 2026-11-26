# forward_bias.py again, with two fixes.
# 1. dry bulk on real earnings, not later quotes: Baltic Capesize average earnings by year as reported in Golden Ocean's
#    filings (2015-17, 2021-24) and Kpler/Breakwave (2025), with Golden Ocean's own Capesize TCE for 2019-20 where I
#    couldn't find the Baltic average (data/capesize_realised_annual.csv). no 2018 figure, so windows that include 2018
#    are dropped. Baltic averages and the Intermodal three-year rate are both gross time-charter-equivalent for a
#    180,000 dwt ship, so the basis matches.
# 2. tankers: Euronav's realised spot TCE is net of commission and counted voyage by voyage, the three-year quote is a
#    gross time charter. two checks on that gap: a flat 5% commission, and the realised spot rate against the average
#    one-year time charter quote in the same calendar year across the whole sample.
import os, json, datetime as dt
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
R = rows('broker_weekly_intermodal.csv')
d = lambda s: dt.date.fromisoformat(s)
cape = {int(r['year']): float(r['usd_day']) for r in rows('capesize_realised_annual.csv') if r['usd_day']}
real = {int(r['year']): r for r in rows('euronav_realised_rates.csv')}
def window_avg(series, t0):
    t1 = dt.date(t0.year + 3, t0.month, min(t0.day, 28)); tot = w = 0.0
    for y in range(t0.year, t1.year + 1):
        a, b = max(t0, dt.date(y, 1, 1)), min(t1, dt.date(y, 12, 31))
        if b <= a: continue
        if y not in series: return None
        ww = (b - a).days; tot += ww * series[y]; w += ww
    return tot / w
def test(col3, series):
    pts = []
    for r in R:
        t0 = d(r['report_date'])
        if t0 > dt.date(2022, 12, 31) or not r[col3]: continue
        x = window_avg(series, t0)
        if x: pts.append((r['report_date'], float(r[col3]), x))
    ratio = [x / q for _, q, x in pts]; srt = sorted(pts, key=lambda p: p[1]); n = max(1, len(srt) // 3)
    return {'n': len(pts), 'mean': sum(ratio) / len(ratio), 'top': sum(x / q for _, q, x in srt[-n:]) / n, 'bottom': sum(x / q for _, q, x in srt[:n]) / n,
            'top_dates': [p[0] for p in srt[-n:]], 'over': sum(1 for v in ratio if v < 1)}
out = {}
c = test('cape_3y_tc', cape); out['capesize'] = c
print(f'Capesize on realised earnings ({c["n"]} reports, 2019-2022; windows through 2018 dropped): later earnings / 3-yr rate {c["mean"]:.2f} on average, '
      f'top third {c["top"]:.2f} ({", ".join(c["top_dates"])}), bottom third {c["bottom"]:.2f}; the 3-yr rate overshot in {c["over"]} of {c["n"]}')
# tankers with the basis checks
for seg, col3, col1 in (('vlcc', 'vlcc_3y_tc', 'vlcc_1y_tc'), ('suezmax', 'suez_3y_tc', 'suez_1y_tc')):
    s = {y: float(r[f'{seg}_spot']) for y, r in real.items()}
    t = test(col3, s)
    # same-year basis: realised spot over the average one-year quote dated that year
    yrs = {}
    for r in R:
        yrs.setdefault(d(r['report_date']).year, []).append(float(r[col1]))
    basis = [s[y] / (sum(q) / len(q)) for y, q in yrs.items() if y in s]
    b = sum(basis) / len(basis)
    out[seg] = {**t, 'basis_same_year': b, 'top_commission_adj': t['top'] / 0.95, 'top_basis_adj': t['top'] / b}
    print(f'{seg}: top third {t["top"]:.2f} raw; {t["top"]/0.95:.2f} after a 5% commission; realised spot averaged {b:.2f}x the same-year one-year quote '
          f'({len(basis)} years), so {t["top"]/b:.2f} on that basis; bottom third {t["bottom"]:.2f} raw')
json.dump(out, open(os.path.join(HERE, '..', 'results', 'forward_bias_v2.json'), 'w'), indent=1)
