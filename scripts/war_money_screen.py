# who kept the war money, Q3 2026. for each listed tanker owner: what its time charters earned against its own spot
# ships in the same quarter, times the charter days. positive = earnings that went to the charterer instead.
# 'stated' rows use the company's own day counts; 'derived' rows back the days out of blended rates or vessel counts
# (method in the data file). own spot is the benchmark because it's the same company and quarter; it isn't always the
# same ships, so read each line as an order of magnitude.
import os, csv
HERE = os.path.dirname(os.path.abspath(__file__))
def rows(f): return list(csv.DictReader(open(os.path.join(HERE, '..', 'data', f))))
P = {r['ticker']: r for r in rows('war_money_profit_q3_2026.csv')}
tot, tot_s = {}, 0.0
print(f'{"owner":22s} {"class":11s} {"charter $/d":>11s} {"spot $/d":>9s} {"gap":>9s} {"days":>6s} {"$m":>7s}  days')
for r in rows('war_money_q3_2026.csv'):
    gap = float(r['spot_tce']) - float(r['tc_tce']); m = gap * float(r['tc_days']) / 1e6
    t = tot.setdefault(r['ticker'], {'name': r['company'], 'm': 0.0, 'derived': False}); t['m'] += m
    if r['days_method'] != 'stated': t['derived'] = True
    print(f'{r["company"]:22s} {r["class"]:11s} {float(r["tc_tce"]):11,.0f} {float(r["spot_tce"]):9,.0f} {gap:9,.0f} {float(r["tc_days"]):6,.0f} {m:7.1f}  {"stated" if r["days_method"]=="stated" else "derived"}')
print()
grand = 0.0
for k, t in sorted(tot.items(), key=lambda x: -x[1]['m']):
    grand += t['m']; extra = ''
    if k in P:
        p = float(P[k]['q3_2026_profit_usd_m']); extra = f', {t["m"]/p:+.0%} of its Q3 profit'
        if P[k]['shares_m']: extra += f', ${t["m"]/float(P[k]["shares_m"]):.2f} a share'
    print(f'{t["name"]:22s} ${t["m"]:7.1f}m{" (days partly derived)" if t["derived"] else ""}{extra}')
print(f'total across the {len(tot)} owners: ${grand:,.0f}m handed to charterers in one quarter')
vlo = float(P['VLO']['q3_2026_profit_usd_m'])
print(f'for scale: Valero, which charters six of CMB.TECH\'s Suezmaxes, made ${vlo:,.0f}m in Q3; everything CMB.TECH handed to all its charterers is {tot["CMBT"]["m"]/vlo:.1%} of that')
print('INSW is the exception: its VLCC charters carry profit sharing, which INSW says lifted Q3 by about $75m; the charter TCE ($315,258) ran above its own spot ($154,597)')
