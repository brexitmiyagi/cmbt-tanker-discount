# Q4 2026, built from what is already booked. tankers and dry bulk: the share of Q4 spot days fixed at the
# quarter-to-date rate (Q3 2026 release), the rest at the Q3 rate, less the company's own P&L breakeven per day;
# charter days at Q3 charter rates. the other businesses bottom-up from the Q3 presentation (slides 30-34): ships x
# days x (rate - breakeven), Q4 at the quarter-to-date rate where one is given. gains from the three sales the
# release names. then the same with the unbooked days at the quarter-to-date rate instead of Q3.
import os, json
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
fx = {r['segment'].replace(' spot', ''): r for r in rows('fixtures.csv')}
oth = {r['segment']: r for r in rows('other_segments_q3_2026.csv')}
TC = {'VLCC': 85623, 'Suezmax': 32986, 'Newcastlemax': 35942, 'Capesize': 28879, 'Kamsarmax/Panamax': 17557}
off = 100 / 108                                   # drydock and off-hire allowance, as in model.py
spot_days = {'VLCC': 3 * 92, 'Suezmax': 6 * 92, 'Newcastlemax': 41 * 92 * off, 'Capesize': 37 * 92 * off, 'Kamsarmax/Panamax': 30 * 92 * off}
tc_days = {'VLCC': 92, 'Suezmax': 717, 'Newcastlemax': 24, 'Capesize': 435, 'Kamsarmax/Panamax': 286}
sh = 290.169769
def segs(unbooked_at_qtd=False):
    out = {}
    for k, r in fx.items():
        be, q3, qtd, f = float(r['pnl_breakeven']), float(r['q3_2026']), float(r['q4_2026_to_date']), float(r['fixed_pct'])
        rate = f * qtd + (1 - f) * (qtd if unbooked_at_qtd else q3)
        out[k] = (spot_days[k] * (rate - be) + tc_days[k] * (TC[k] - be)) / 1e6
    return out
def other(q):
    g = lambda s, c: float(oth[s][c]) if oth[s][c] else None
    o = {}
    o['Container'] = 4 * 92 * (g('Container', 'q3_2026_tce') - g('Container', 'pnl_breakeven')) / 1e6
    o['Chemicals'] = (2 * 92 * ((g('Chemical pool', 'q4_2026_tce_to_date') if q == 4 else g('Chemical pool', 'q3_2026_tce')) - g('Chemical pool', 'pnl_breakeven'))
                      + 6 * 92 * (g('Chemical TC', 'q3_2026_tce') - g('Chemical TC', 'pnl_breakeven'))) / 1e6
    o['CSOV'] = 4 * 92 * ((g('CSOV', 'q4_2026_tce_to_date') if q == 4 else g('CSOV', 'q3_2026_tce')) - g('CSOV', 'pnl_breakeven')) / 1e6
    o['CTV'] = 60 * 92 * ((g('CTV', 'q4_2026_tce_to_date') if q == 4 else g('CTV', 'q3_2026_tce')) - g('CTV', 'pnl_breakeven')) / 1e6
    return o
o3, o4 = other(3), other(4)
group_costs = 12.7 - sum(o3.values())             # model.py's calibrated Q3 residual less the businesses above
gains = 74.3 + 56.9 + 59.6
res = {}
for lab, flag in (('base', False), ('unbooked at QTD', True)):
    s = segs(flag)
    ex = sum(s.values()) + sum(o4.values()) + group_costs
    res[lab] = {'segments': s, 'other': o4, 'group_costs': group_costs, 'profit_ex_gains': ex, 'profit': ex + gains, 'eps': (ex + gains) / sh, 'eps_ex': ex / sh}
b = res['base']
print('Q4 2026 profit by segment ($m): ' + ', '.join(f'{k} {v:.1f}' for k, v in b['segments'].items()))
print('  other businesses Q4 ($m): ' + ', '.join(f'{k} {v:+.1f}' for k, v in o4.items()) + f'; same at Q3 rates: ' + ', '.join(f'{k} {v:+.1f}' for k, v in o3.items()))
print(f'  group costs not in the breakevens, backed out of Q3: {group_costs:+.1f} a quarter')
print(f'  profit ex gains ${b["profit_ex_gains"]:.0f}m (${b["eps_ex"]:.2f}); gains ${gains:.1f}m; profit ${b["profit"]:.0f}m, EPS ${b["eps"]:.2f}; '
      f'half of EPS, as in Q2 ($0.64 of $1.26) and Q3 ($0.65 of $1.29): about ${b["eps"]/2:.2f}')
u = res['unbooked at QTD']
print(f'  if the unbooked days earn the quarter-to-date rate: profit ${u["profit"]:.0f}m, EPS ${u["eps"]:.2f}')
tank = b['segments']['VLCC'] + b['segments']['Suezmax']; dry = sum(b['segments'][k] for k in ('Newcastlemax', 'Capesize', 'Kamsarmax/Panamax'))
print(f'  tankers ${tank:.0f}m, dry bulk ${dry:.0f}m of the ${b["profit_ex_gains"]:.0f}m before gains')
json.dump(res, open(os.path.join(HERE, '..', 'results', 'q4_preview.json'), 'w'), indent=1)

# the other businesses for a year, at Q3 rates, against what they'd need to earn their broker value
fmv_other, total_fmv, nd = 408 + 844 + 789, 12186, 4870.3
yr = sum(o3.values()) * 365 / 92
eq = fmv_other * (1 - nd / total_fmv)
print(f'other businesses at Q3 rates: ${yr:.0f}m a year (${yr/sh:.2f} a share), {yr/eq:.1%} on their ${eq:,.0f}m share of equity at broker value; '
      f'capitalised at 8.2%: ${yr/0.0816:,.0f}m (${yr/0.0816/sh:.2f} a share) against ${eq/sh:.2f} at broker value; gap ${(eq - yr/0.0816)/sh:.2f} a share, '
      f'{(eq - yr/0.0816)/sh*1.0816/17.72*100:+.1f} points of expected return')
print('  company FY2027 FCF chart: chemicals, containers and CSOVs 6.1% of $722m, about $' + f'{0.061*722:.0f}m (CTVs excluded)')
