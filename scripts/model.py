# my earnings model, Q4 2026 to Q4 2028, quarterly. it is a driver model, not the company's.
# how it works:
#  - tankers and dry bulk: days x (rate - the company's own P&L breakeven per day). the breakevens on slides 13 and 24
#    include opex, insurance, management fees, depreciation, interest and pool fees, so this lands at net profit.
#  - spot days for 2027 come from slide 8 (FCF step per $1,000/day). time charter days at the Q3 2026 charter averages.
#  - everything else (chemicals, containers, offshore, CTVs, G&A not in the breakevens, JV income) is one line,
#    calibrated so the model reproduces Q3 2026 profit ex gains ($273.6m), then held flat.
#  - Q4 2026 fleet: 4 VLCCs on the water, 1 on the one-year charter, so 3 spot; 6 Suezmaxes spot; sold ships left out.
#  - rates: Q4 2026 = booked share at the quarter-to-date rate, rest at Q3. 2027 = the company deck (the market's
#    forward price). 2028 = halfway from the deck to the 2015-2025 through-cycle average, for every segment.
#  - cash: profit ex gains + depreciation - capex (slide 9) + sale proceeds - distributions (50% of profit incl gains,
#    paid the next quarter). all spare cash goes to debt, which is what the CFO said they prefer.
from common import rows, kv
import os
HERE = os.path.dirname(os.path.abspath(__file__))
fx = {r['segment']: r for r in rows('fixtures.csv')}
d = {r['item']: float(r['value']) for r in rows('debt_and_pl_q3_2026.csv')}
bs = kv('balance_sheet_2026-09-30.csv')
sh = bs['shares_ex_treasury'] / 1e6
BE = {k: float(fx[k + ' spot']['pnl_breakeven']) for k in ['VLCC', 'Suezmax', 'Newcastlemax', 'Capesize', 'Kamsarmax/Panamax']}
Q3 = {k: float(fx[k + ' spot']['q3_2026']) for k in BE}
Q4 = {k: float(fx[k + ' spot']['fixed_pct']) * float(fx[k + ' spot']['q4_2026_to_date']) + (1 - float(fx[k + ' spot']['fixed_pct'])) * Q3[k] for k in BE}
PRE = {k: float(fx[k + ' spot']['q3_2025']) for k in BE}
_t = rows('cmbt_tanker_tce_2025.csv')
PRE['VLCC'] = sum(float(r['vlcc_spot']) for r in _t) / len(_t); PRE['Suezmax'] = sum(float(r['suezmax_spot']) for r in _t) / len(_t)
DECK = {'VLCC': 122500, 'Suezmax': 77500, 'Newcastlemax': 40608, 'Capesize': 31975, 'Kamsarmax/Panamax': 17050}
SPOT27 = {'VLCC': 1633, 'Suezmax': 2839, 'Newcastlemax': 15510, 'Capesize': 11260, 'Kamsarmax/Panamax': 10560}  # tc_drag.py / fcf_stress.py
TC = {'VLCC': 85623, 'Suezmax': 32986, 'Newcastlemax': 35942, 'Capesize': 28879, 'Kamsarmax/Panamax': 17557}  # Q3 2026 charter averages
# dry bulk house view: CAPE27 / CAPE28 set the Capesize rate; Newcastlemax and Kamsarmax move in proportion to the
# company's 2027 deck. defaults = the company deck for 2027 and $30,000 for 2028. dry_bulk_cases.py runs the others.
# one rule for every segment: 2027 at the market's forward price (the company deck, FFAs for dry bulk); 2028 halfway
# from there to the through-cycle average (through_cycle.py: Euronav/CMB.TECH realised spot 2015-2025 for tankers,
# the Clarksons-implied 10-year Capesize average for dry bulk); from 2029 the through-cycle year itself.
import json as _json
_tc = _json.load(open(os.path.join(HERE, '..', 'results', 'through_cycle.json')))['through_cycle']
Y25_CAPE = 21297
CAPE27 = float(os.environ.get('CAPE27', DECK['Capesize']))
CAPE28 = float(os.environ.get('CAPE28', (DECK['Capesize'] + _tc['Capesize']) / 2))
D27 = {**DECK, **{k: DECK[k] * CAPE27 / DECK['Capesize'] for k in ('Newcastlemax', 'Capesize', 'Kamsarmax/Panamax')}}
TCQ = {'VLCC': 92, 'Suezmax': 717, 'Newcastlemax': 24, 'Capesize': 435, 'Kamsarmax/Panamax': 286}  # Q3 2026 charter days

def seg(days_spot, days_tc, rate):
    return sum(days_spot[k] * (rate[k] - BE[k]) + days_tc[k] * (TC[k] - BE[k]) for k in BE) / 1e6

# calibrate the residual on Q3 2026. Q3 fleet: 5 VLCCs (incl. Donoussa), ~17 Suezmaxes (incl. Bristol, Stella and
# Brest/Brugge for about half the quarter), 41/37/30 bulkers.
q3_spot = {'VLCC': 5 * 92 - 184, 'Suezmax': 17 * 92 - 717, 'Newcastlemax': 41 * 92 - 24, 'Capesize': 37 * 92 - 435, 'Kamsarmax/Panamax': 30 * 92 - 286}
q3_tc = {'VLCC': 184, 'Suezmax': 717, 'Newcastlemax': 24, 'Capesize': 435, 'Kamsarmax/Panamax': 286}
q3_profit_ex = (373.898 - 100.277)
resid = q3_profit_ex - seg(q3_spot, q3_tc, Q3)
print(f'calibration: Q3 2026 tankers + dry bulk modelled ${q3_profit_ex-resid:,.1f}m; everything else ${resid:,.1f}m a quarter')

quarters = ['Q4 26', 'Q1 27', 'Q2 27', 'Q3 27', 'Q4 27', 'Q1 28', 'Q2 28', 'Q3 28', 'Q4 28']
capex = [167, 223, 88, 57, 30, 69.5, 69.5, 69.5, 69.5]  # slide 9; 2028 = remaining $278m of the $843m, spread evenly
gains = [190.8] + [0] * 8
proceeds = [160.48 + 74.3 + 56.9] + [0] * 8  # Donoussa + Bristol: held-for-sale book + gain; Stella left out
dep = d['depreciation_q3_2026_usd_m']
nd = bs['bank_loans_and_borrowings'] / 1000 + 5.5 - bs['cash'] / 1000 if 'bank_loans_and_borrowings' in bs else 4870.3
eq = bs['total_equity'] / 1000 if 'total_equity' in bs else 3495.006
dist_due = 0.65 * sh
RATE = 4 * d['net_finance_expenses_q3_2026_usd_m'] / d['gross_debt_incl_leases_q3_2026_usd_m']   # ~6.0%
TAX = (375.141 - 373.898) / 375.141   # Q3 2026 tax over profit before tax (tonnage tax regime), ~0.3%
out = []
for i, q in enumerate(quarters):
    if i == 0:
        sp = {'VLCC': 3 * 92, 'Suezmax': 6 * 92, 'Newcastlemax': 41 * 92 * 100 / 108, 'Capesize': 37 * 92 * 100 / 108, 'Kamsarmax/Panamax': 30 * 92 * 100 / 108}
        tc = {'VLCC': 92, 'Suezmax': 717, 'Newcastlemax': 24, 'Capesize': 435, 'Kamsarmax/Panamax': 286}
        rate = Q4
    else:
        yr = 2027 if i <= 4 else 2028
        sp = {k: SPOT27[k] / 4 for k in BE}
        tc = {'VLCC': 96 if i <= 2 else 0, 'Suezmax': (14 * 365 - 2839) / 4, 'Newcastlemax': 24, 'Capesize': 435, 'Kamsarmax/Panamax': 286}
        if yr == 2028:
            sp['VLCC'] += 0
        # 2028: tankers back to pre-war; dry bulk at CAPE28, Newcastlemax and Kamsarmax in proportion to the 2027 deck
        D28 = {k: DECK[k] * CAPE28 / DECK['Capesize'] for k in ('Newcastlemax', 'Capesize', 'Kamsarmax/Panamax')}
        _mode = os.environ.get('TANK28', 'phased')
        T28 = DECK if _mode == 'deck' else PRE if _mode == '2025' else {'VLCC': _tc['VLCC'], 'Suezmax': _tc['Suezmax']} if _mode == 'cycle' else {'VLCC': (DECK['VLCC'] + _tc['VLCC']) / 2, 'Suezmax': (DECK['Suezmax'] + _tc['Suezmax']) / 2}
        rate = D27 if yr == 2027 else {**D28, 'VLCC': T28['VLCC'], 'Suezmax': T28['Suezmax']}
    # the breakevens carry 2026-budget interest; paying debt down saves interest at the Q3 run-rate cost of debt
    saving = (4870.3 - nd) * RATE / 4
    # the 1,400 TEU ammonia containership delivers in December 2026 on a 15-year charter; I give it the existing
    # container fleet's Q3 margin over breakeven ($29,681 - $21,353). chemical newbuilds (2028) earn ~$453/day over
    # breakeven on the Q3 numbers, so they're left out as immaterial.
    box = 0 if i == 0 else 91 * (29681 - 21353) / 1e6
    # Q4_OTHER=1 (v26 on): Q4 2026 chemical/container/offshore at their Q4 to-date rates plus group costs, from
    # q4_preview.py, instead of the flat Q3 residual. off by default so earlier versions still reproduce.
    r_i = resid
    if i == 0 and os.environ.get('Q4_OTHER') == '1':
        _j = __import__('json').load(open(os.path.join(HERE, '..', 'results', 'q4_preview.json')))['base']
        r_i = sum(_j['other'].values()) + _j['group_costs']
    ni_ex = (seg(sp, tc, rate) + r_i + box + saving) * (1 - TAX)
    ni = ni_ex + gains[i]
    # depreciation grows as newbuilds deliver: capex to date over a 25-year life (the breakevens carry it in profit)
    dep_i = dep + sum(capex[:i]) / 100
    fcf = ni_ex + dep_i - capex[i] + proceeds[i]
    paid = dist_due
    nd = nd - (fcf - paid)
    eq = eq + ni - paid
    dist_due = 0.5 * ni
    out.append((q, ni_ex, ni, ni / sh, fcf, paid, nd, eq))
print(f'{"qtr":6s} {"profit ex gains":>15s} {"profit":>8s} {"EPS":>6s} {"FCF":>7s} {"dist paid":>9s} {"net debt":>9s} {"book equity":>11s}')
for q, a, b, c, f, p, n, e in out:
    print(f'{q:6s} {a:15.1f} {b:8.1f} {c:6.2f} {f:7.1f} {p:9.1f} {n:9.1f} {e:11.1f}')
fy26 = d['profit_9m_2026_usd_m'] + out[0][2]
fy26_ex = fy26 - d['gains_9m_2026_usd_m'] - gains[0]
fy27 = sum(o[2] for o in out[1:5]); fy28 = sum(o[2] for o in out[5:9])
print(f'FY2026 EPS ${fy26/sh:.2f} reported (incl. ${(d["gains_9m_2026_usd_m"]+190.8)/sh:.2f} of sale gains), ${fy26_ex/sh:.2f} ex gains; consensus ${d["consensus_eps_2026"]:.2f}')
print(f'FY2027 EPS ${fy27/sh:.2f}; consensus ${d["consensus_eps_2027"]:.2f} ({fy27/sh/d["consensus_eps_2027"]-1:+.0%})')
print(f'FY2028 EPS ${fy28/sh:.2f}; consensus ${d["consensus_eps_2028"]:.2f} ({fy28/sh/d["consensus_eps_2028"]-1:+.0%})')
print(f'net debt end-2026 ${out[0][6]:,.0f}m (CFO guide: gross debt ~$4.4bn), end-2027 ${out[4][6]:,.0f}m, end-2028 ${out[8][6]:,.0f}m')
print(f'distributions paid in the next 12 months (Dec 2026 to Sep 2027): ${sum(o[5] for o in out[0:4]):,.1f}m = ${sum(o[5] for o in out[0:4])/sh:.2f} a share; Q4 2026 distribution about ${0.5*out[0][2]/sh:.2f}')
print(f'book equity a share end-2027 ${out[4][7]/sh:.2f}, end-2028 ${out[8][7]/sh:.2f}')
print(f'interest: Q3 2026 net finance cost ${d["net_finance_expenses_q3_2026_usd_m"]:.1f}m = {4*d["net_finance_expenses_q3_2026_usd_m"]/d["gross_debt_incl_leases_q3_2026_usd_m"]:.1%} of gross debt annualised; +1% SOFR = ${d["sofr_plus_1pct_interest_2025_usd_m"]:.1f}m a year = ${d["sofr_plus_1pct_interest_2025_usd_m"]/sh:.2f} a share before tax')
lt1 = d['bank_loans_flows_lt1y'] + d['other_borrowings_flows_lt1y']; m = d['bank_loans_flows_1to5y'] + d['other_borrowings_flows_1to5y']; gt = d['bank_loans_flows_gt5y'] + d['other_borrowings_flows_gt5y']
print(f'debt service at end-2025 (principal + interest): <1y ${lt1:,.0f}m, 1-5y ${m:,.0f}m, >5y ${gt:,.0f}m')
import json
json.dump({'dist12': sum(o[5] for o in out[0:4]) / sh, 'q4_profit': out[0][2], 'fy27_eps': fy27 / sh, 'fy28_eps': fy28 / sh, 'eq27': out[4][7], 'nd27': out[4][6], 'fcf27': sum(o[4] for o in out[1:5]), 'fcf28': sum(o[4] for o in out[5:9]), 'fcf_q4_26': out[0][4], 'eq28': out[8][7]}, open(os.environ.get('MODEL_OUT', os.path.join(HERE, '..', 'results', 'model_summary.json')), 'w'))
