# what the rating rests on, and everything that moves it. the published case (valuation_derived.py) runs my model:
# 2027 at the company's rate deck, 2028 halfway from there to the 2015-2025 through-cycle average. that is a house
# view, and this script prices it against the market's own forward prices: the Capesize forward curve for dry bulk
# (data/capesize_ffa_2026-10-26.csv) and the three-year time charter for tankers (Intermodal, 20 Nov 2026).
# then: where 2028 EPS differs from consensus, the cost of equity from outside inputs, price-to-book on a
# like-for-like basis, four more tanker sales in 2027, and the 2027 tanker rate if Hormuz reopens or rates hold.
import os, json, subprocess, sys, tempfile
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda f: json.load(open(os.path.join(HERE, '..', 'results', f)))
rw, ct = J('roe_windows.json'), J('charter_test_curves.json')
sh, px, k = 290.169769, {r['ticker']: float(r['close_2026_11_25']) for r in rows('prices_2026-11-25.csv')}['CMBT'], (4.91 + 0.65 * 5) / 100
pred = lambda e, g: (e * 3128 + g * 7017) / 10145
rc = rw['routine_common']
kk = (pred(rc['Euronav'], rc['Golden Ocean']) - pred(0.067, 0.068)) / ((98 / 76.2) ** (1 / 7) - 1)
r_of = lambda d: pred(0.067, 0.068) + kk * d
T_ON = 3.7 - (2 + 1 / 12)
drift = ct['fleet']['drift_compass']

def run_model(**env):
    f = os.path.join(tempfile.mkdtemp(), 'ms.json')
    subprocess.run([sys.executable, os.path.join(HERE, 'model.py')], env={**os.environ, **{k_: str(v) for k_, v in env.items()}, 'MODEL_OUT': f}, capture_output=True, check=True)
    return json.load(open(f))
def value(ms, kq=k, d=drift, extra=0.0):
    q4, f27, f28, book = ms['fcf_q4_26'] / sh, ms['fcf27'] / sh, ms['fcf28'] / sh, ms['eq28'] / sh
    cash = q4 / (1 + kq) ** 0.125 + f27 / (1 + kq) ** 0.625 + f28 / (1 + kq) ** 1.625 + extra
    rd, r0, s, t = r_of(d), r_of(0.0), 0.0, 0.0
    while t < T_ON - 1e-9:
        dt = min(1.0, T_ON - t); s += (rd - kq) * dt * book / (1 + kq) ** (t + dt); t += dt
    s += (r0 - kq) / kq * book / (1 + kq) ** T_ON
    v = cash + (book + s) / (1 + kq) ** 1.625
    return v, v * (1 + kq) / px - 1            # distributions cancel: (p12 + dist) / px - 1

ffa = {r['period']: float(r['usd_day']) for r in rows('capesize_ffa_2026-10-26.csv') if r['period'].startswith('Cal')}
seg = {r['segment']: r for r in rows('segments_2026-11-20.csv')}
base = run_model()
fwd_dry = run_model(CAPE27=ffa['Cal 2027'], CAPE28=ffa['Cal 2028'])
deck_t = run_model(CAPE27=ffa['Cal 2027'], CAPE28=ffa['Cal 2028'], TANK28='deck')
# the model has no switch for tankers at the three-year rate, so scale the deck case: 2028 VLCC and Suezmax spot days
# (1,633 and 2,839) x the gap between each rate and my 2028 rate
tc = J('through_cycle.json')['through_cycle']
DECK = {'VLCC': 122500, 'Suezmax': 77500}
mine28 = {s: (DECK[s] + tc[s]) / 2 for s in DECK}
days = {'VLCC': 1633, 'Suezmax': 2839}
gap_deck = sum(days[s] * (DECK[s] - mine28[s]) for s in DECK)
gap_3y = sum(days[s] * (float(seg[s]['tc_3y']) - mine28[s]) for s in DECK)
w = gap_3y / gap_deck
fwd_all = {x: fwd_dry[x] + w * (deck_t[x] - fwd_dry[x]) for x in fwd_dry}
cases = {'my 2028 (published)': base, 'dry bulk on the forward curve': fwd_dry, 'dry bulk forward curve + tankers at the 3-year charter': fwd_all}
out = {'cases': {}}
for lab, ms in cases.items():
    v, e = value(ms); out['cases'][lab] = {'eps27': ms['fy27_eps'], 'eps28': ms['fy28_eps'], 'value': v, 'er': e, 'p12': v * (1 + k) - ms['dist12']}
    print(f'{lab:55s} EPS 2027 ${ms["fy27_eps"]:.2f}, 2028 ${ms["fy28_eps"]:.2f}; expected 12-month total return {e:+.1%} (SELL line {k-0.05:.1%})')
print(f'  my 2028 rates: VLCC ${mine28["VLCC"]:,.0f}, Suezmax ${mine28["Suezmax"]:,.0f}, Capesize ${(31975 + tc["Capesize"]) / 2:,.0f}; '
      f'market: 3-yr TC VLCC ${float(seg["VLCC"]["tc_3y"]):,.0f}, Suezmax ${float(seg["Suezmax"]["tc_3y"]):,.0f}, Capesize Cal28 FFA ${ffa["Cal 2028"]:,.0f}')

# 2028 EPS against consensus, step by step
cons = {r['item']: float(r['value']) for r in rows('consensus_2026-11.csv') if r['item'].startswith('consensus_eps')}
b28, d28, a28 = base['fy28_eps'], fwd_dry['fy28_eps'], fwd_all['fy28_eps']
out['eps28_bridge'] = {'mine': b28, 'dry_bulk_to_forward': d28 - b28, 'tankers_to_3yr': a28 - d28, 'market_prices': a28, 'consensus': cons['consensus_eps_2028']}
print(f'2028 EPS: mine ${b28:.2f}; dry bulk at the forward curve {d28-b28:+.2f}; tankers at the 3-year charter {a28-d28:+.2f}; = ${a28:.2f} on market prices; consensus ${cons["consensus_eps_2028"]:.2f}')

# cost of equity from outside inputs
ce = {r['item']: float(r['value']) for r in rows('cost_of_equity_2026-11.csv')}
rf, erp = ce['riskfree_10y'] / 100, ce['implied_erp_sp500'] / 100
grid = {b: rf + b * erp for b in (ce['cmbt_beta_low'], 0.65, ce['industry_beta_shipbuilding_marine'], ce['cmbt_beta_high'])}
out['coe'] = grid
print('cost of equity, 4.94% risk-free + beta x 4.41% implied ERP (Damodaran, 1 Nov 2026): ' + ', '.join(f'beta {b:.2f} {v:.2%}' for b, v in grid.items()))
print(f'  Damodaran industry table (Jan 2026 inputs) shows Shipbuilding & Marine at {ce["industry_coe_shipbuilding_marine"]:.2f}%; with a 5% premium instead, beta 0.75 gives {rf + 0.75 * 0.05:.2%}')
for kq in (ce['cmbt_beta_low'] * erp + rf, rf + 0.75 * erp, rf + ce['cmbt_beta_high'] * erp):
    print(f'  published case at {kq:.2%}: expected {value(base, kq)[1]:+.1%} vs line {kq-0.05:.1%}')

# price-to-book, like for like: return on equity with and without sale gains and impairments, 2016-2025
bk = {r['ticker']: r for r in rows('peer_book_2026-09-30.csv')}
hist, adj = {}, {}
for r in rows('peer_roe_xbrl.csv'): hist.setdefault(r['ticker'], {})[int(r['year'])] = (float(r['net_income_usd_m']), float(r['equity_end_usd_m']))
for r in rows('peer_gains_impairments_xbrl.csv'):
    adj.setdefault(r['ticker'], {})[int(r['year'])] = float(r['sale_gain_usd_m'] or 0) - float(r['impairment_usd_m'] or 0)
pb = {}
for t, b in bk.items():
    p_b = px if t == 'CMBT' else {r['ticker']: float(r['close_2026_11_25']) for r in rows('prices_2026-11-25.csv')}[t]
    p_b = p_b * float(b['shares_m']) / float(b['equity_usd_m'])
    if t == 'CMBT':
        rep, ex = pred(rc['Euronav'], rc['Golden Ocean']), pred(0.067, 0.068)   # routine gains kept / gains and impairments out, 2015-2024
    else:
        h = hist[t]; ys = [y for y in range(2016, 2026) if y in h and y - 1 in h]
        eq = sum((h[y][1] + h[y - 1][1]) / 2 for y in ys)
        rep = sum(h[y][0] for y in ys) / eq; ex = sum(h[y][0] - adj[t].get(y, 0.0) for y in ys) / eq
    pb[t] = {'pb': p_b, 'roe_reported': rep, 'roe_ex': ex}
    print(f'{t:5s} price/book {p_b:.2f}; ten-year ROE {rep:+.1%} reported, {ex:+.1%} without sale gains and impairments; justified (no growth, at {k:.1%}) {max(rep,0)/k:.2f} / {max(ex,0)/k:.2f}')
out['pb'] = pb

# four more tanker sales early in 2027 at today's prices: two VLCCs and two Suezmaxes at the average of this quarter's
# deals (gains $74.3m, $56.9m, $59.6m; book $160.48m for Donoussa and Bristol together). the company gets the price now,
# gives up the ships' 2027-28 earnings (deck, then my 2028) and their end-2028 book at what my normal year pays for it.
gain, book_s = (74.3 + 56.9 + 59.6) / 3, 160.48 / 2
BE = {r['segment'].split()[0]: float(r['pnl_breakeven']) for r in rows('fixtures.csv')}
dep = book_s / 13
lost = sum(2 * ((DECK[s] - BE[s]) * 355 / 1e6 + dep) / (1 + k) ** 0.6 + 2 * ((mine28[s] - BE[s]) * 355 / 1e6 + dep) / (1 + k) ** 1.6 for s in DECK)
cash_pv = base['fcf_q4_26'] / sh / (1 + k) ** 0.125 + base['fcf27'] / sh / (1 + k) ** 0.625 + base['fcf28'] / sh / (1 + k) ** 1.625
ratio = (value(base)[0] - cash_pv) / (base['eq28'] / sh)   # what a dollar of end-2028 book is worth today on my normal year
keep_book = 4 * (book_s - 2 * dep) * ratio
dv = (4 * (book_s + gain) / (1 + k) ** 0.1 - lost - keep_book) / sh
out['tanker_sales'] = {'dv': dv, 'er': value(base, extra=dv)[1]}
print(f'four more tanker sales in early 2027: proceeds ${4*(book_s+gain):,.0f}m, value {dv:+.2f} a share, expected {out["tanker_sales"]["er"]:+.1%}')

# 2027 tanker rates: Hormuz reopens and the deck halves, or rates hold at today's one-year charters
for lab, r27 in (('reopening, tanker deck halves', {s: DECK[s] / 2 for s in DECK}), ('rates hold at the one-year charter', {s: float(seg[s]['tc_1y']) for s in DECK})):
    dni = sum(days[s] * (r27[s] - DECK[s]) for s in DECK) / 1e6
    dv = dni / (1 + k) ** 0.625 / sh
    out[lab] = {'eps27': base['fy27_eps'] + dni / sh, 'er': value(base, extra=dv)[1]}
    print(f'2027 {lab}: EPS 2027 ${base["fy27_eps"] + dni/sh:.2f} (from ${base["fy27_eps"]:.2f}), expected {out[lab]["er"]:+.1%}')
print('Kalshi 26 Nov 2026: normal Hormuz traffic before 1 Jan 2028 32.5% (kalshi_2026-11-26.csv); Polymarket 34.5% by 31 Dec 2027')
json.dump(out, open(os.path.join(HERE, '..', 'results', 'house_view_checks.json'), 'w'), indent=1)

# the cost of equity at which the published case sits exactly on its SELL line
lo, hi = 0.06, 0.10
for _ in range(60):
    m = (lo + hi) / 2; lo, hi = (lo, m) if value(base, m)[1] < m - 0.05 else (m, hi)
out['coe_flip'] = m
print(f'the published case is on its SELL line at a cost of equity of {m:.2%}; below that it is not a SELL')
json.dump(out, open(os.path.join(HERE, '..', 'results', 'house_view_checks.json'), 'w'), indent=1)
