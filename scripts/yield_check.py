# the cash and earnings check on the asset-based target: what you earn on today's price, against the cost of equity
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
ms = json.load(open(os.path.join(HERE, '..', 'results', 'model_summary.json')))
sh, px = 290.169769, 17.54
coe = 4.91 + 0.65 * 5.0
f27, f28 = ms['fcf27'] / sh, ms['fcf28'] / sh
e27, e28 = ms['fy27_eps'], ms['fy28_eps']
print(f'free cash flow a share: 2027 ${f27:.2f} ({f27/px:.1%}), 2028 ${f28:.2f} ({f28/px:.1%}), average {(f27+f28)/2/px:.1%}')
print(f'EPS: 2027 ${e27:.2f} (P/E {px/e27:.1f}x, earnings yield {e27/px:.1%}), 2028 ${e28:.2f} (P/E {px/e28:.0f}x); average earnings yield {(e27+e28)/2/px:.1%}')
print(f'cost of equity {coe:.1f}% (10-year Treasury 4.91% + beta 0.65 x 5% equity risk premium, the premium is my assumption)')
# settle the cash check: discount the model's own cash flows. Q4 2026, 2027 and 2028 free cash flow, then a normal
# year for ever from 2029 with capex = depreciation, so cash = earnings. the normal year is a return on the book equity
# in place when it starts (end-2028 on my model), taken from what shipowners actually earned (roe_windows.py).
import json as _j
rw = _j.load(open(os.path.join(HERE, '..', 'results', 'roe_windows.json')))
book = ms['eq28']
print(f'book equity at the start of the normal year (end-2028, model): ${book:,.0f}m')
for kk in (0.07, coe / 100, 0.10):
    q4 = ms['fcf_q4_26'] / sh
    pv3 = q4 / (1 + kk) ** 0.125 + f27 / (1 + kk) ** 0.625 + f28 / (1 + kk) ** 1.625
    need = ((px - pv3) * (1 + kk) ** 1.625) * kk
    r_need = need * sh / book
    share = sum(1 for x in rw['adjusted'] if x >= r_need) / len(rw['adjusted'])
    vals = {lab: pv3 + (r * book / sh / kk) / (1 + kk) ** 1.625 for lab, r in (('median window 5.0%', sorted(rw['adjusted'])[len(rw['adjusted'])//2]), ('2015-2024 adjusted range low 6.7%', 0.067), ('high 9.7%', 0.097))}
    print(f'cost of equity {kk:.1%}: price needs normal EPS ${need:.2f} = {r_need:.1%} on end-2028 book; {share:.0%} of the 17 adjusted 8-year windows beat that; SELL line {kk-0.05:.1%}; value at ' + ', '.join(f'{k} ${v:.2f}' for k, v in vals.items()))
# central case: the three companies on the common 2015-2024 window, adjusted, averaged
import statistics
c = [0.067, 0.097, 0.068]   # roe_windows.py, common window 2015-2024, adjusted
kk = coe / 100
q4 = ms['fcf_q4_26'] / sh
pv3 = q4 / (1 + kk) ** 0.125 + f27 / (1 + kk) ** 0.625 + f28 / (1 + kk) ** 1.625
r = statistics.mean(c)
dcf = pv3 + (r * book / sh / kk) / (1 + kk) ** 1.625
print(f'central DCF: common-window adjusted average {r:.1%} on end-2028 book -> ${dcf:.2f} a share')
hp = _j.load(open(os.path.join(HERE, '..', 'results', 'payoff_both_routes.json')))
asset = hp['base']
print(f'asset view ${asset:.2f} (12-month value), central DCF ${dcf:.2f} (value today, implied 12-month return {dcf*(1+kk)/px-1:+.1%})')
# the businesses CMB.TECH actually owns: its tankers are the old Euronav, most of its dry bulk the old Golden Ocean.
# weight their common-window adjusted returns by today's fleet value (tankers $3,128m, dry bulk $7,017m).
rp = (0.067 * 3128 + 0.068 * 7017) / (3128 + 7017)
dcf_p = pv3 + (rp * book / sh / kk) / (1 + kk) ** 1.625
er_dcf = dcf_p * (1 + kk) / px - 1
er_asset = hp['ev']
er = (er_dcf + er_asset) / 2
print(f'predecessors (Euronav tankers, Golden Ocean dry bulk), fleet-weighted: {rp:.2f}% -> DCF ${dcf_p:.2f}; implied 12-month return {er_dcf:+.1%}'.replace(f'{rp:.2f}%', f'{rp:.1%}'))
print(f'asset view expected return (25/50/25) {er_asset:+.1%}; 50/50 expected return {er:+.1%} against a SELL line of {kk-0.05:.1%} and a BUY line of {kk+0.05:.1%}')
print(f'target: 50/50 of asset ${asset:.2f} and predecessor DCF ${dcf_p:.2f} = ${(asset+dcf_p)/2:.2f}')
p3 = pv3 + (0.097 * book / sh / kk) / (1 + kk) ** 1.625
print(f'on Star Bulk\'s 9.7% instead: DCF ${p3:.2f}, implied return {p3*(1+kk)/px-1:+.1%}')
for kq in (0.07, coe / 100, 0.10):
    q4_ = ms['fcf_q4_26'] / sh
    pv_ = q4_ / (1 + kq) ** 0.125 + f27 / (1 + kq) ** 0.625 + f28 / (1 + kq) ** 1.625
    vp = pv_ + (rp * book / sh / kq) / (1 + kq) ** 1.625
    print(f'cost of equity {kq:.1%}: DCF at the predecessors\' {rp:.1%} = ${vp:.2f}, implied 12-month return {vp*(1+kq)/px-1:+.1%}')
# the normal-year return at which the 50/50 method reaches the BUY line
target_er = 2 * (kk + 0.05) - er_asset
v_need = (1 + target_er) * px / (1 + kk)
r_buy = (v_need - pv3) * (1 + kk) ** 1.625 * kk / (book / sh)
print(f'BUY line reached when the normal-year return is about {r_buy:.1%} on end-2028 book')
