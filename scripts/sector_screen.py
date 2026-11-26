# the same question across the listed owners: how much of what they earned came from selling ships, and what
# happened to that line when ship prices fell. sale gains and impairments from SEC XBRL (roe_history.csv for Euronav,
# Golden Ocean and Star Bulk; peer_gains_xbrl.csv for International Seaways and Frontline). Frontline's and DHT's sale
# gains aren't tagged consistently in XBRL, so they're left out of the gains columns rather than shown as zero.
from common import rows
R = rows('roe_history.csv') + rows('peer_gains_xbrl.csv')
f = lambda x: float(x) if x not in ('', None) else None
data = {}
for r in R:
    data.setdefault(r['company'], {})[int(r['year'])] = {k: f(r[k]) for k in ('net_income_usd_m', 'equity_end_usd_m', 'impairment_usd_m', 'disposal_gain_usd_m')}
def window(co, y0, y1):
    d = data[co]; g = ni = imp = eqs = 0; n = 0; gaps = False
    for y in range(y0, y1 + 1):
        x = d.get(y); p = d.get(y - 1)
        if not x or not p or x['equity_end_usd_m'] is None or p['equity_end_usd_m'] is None: gaps = True; continue
        avg = (x['equity_end_usd_m'] + p['equity_end_usd_m']) / 2
        if x['disposal_gain_usd_m'] is None: gaps = True
        g += x['disposal_gain_usd_m'] or 0; ni += x['net_income_usd_m'] or 0; imp += x['impairment_usd_m'] or 0
        eqs += avg; n += 1
    return {'gain': g, 'ni': ni, 'imp': imp, 'gain_roe': g / eqs, 'net_roe': (g - imp) / eqs, 'n': n, 'gaps': gaps}
print('rising prices, 2021 to latest: sale gains as a share of profit, and as yearly return on equity')
for co, y1 in (('Euronav', 2024), ('INSW', 2025), ('Golden Ocean', 2024), ('Star Bulk', 2025)):
    w = window(co, 2021, y1)
    print(f'  {co:12s} 2021-{y1}: gains ${w["gain"]:,.0f}m = {w["gain"]/w["ni"]:.0%} of profit ${w["ni"]:,.0f}m; {w["gain_roe"]:+.1%} of equity a year')
import json, os
flg = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results', 'vessel_sales.json')))['frontline_gain']
w = window('Euronav', 2021, 2024)
print(f'  Euronav without the ${flg:,.0f}m of gains on the Frontline fleet sale: {(w["gain"]-flg)/w["ni"]:.0%} of profit')
print('falling prices: sale gains less impairments, as yearly return on equity')
for co, y0, y1 in (('Star Bulk', 2010, 2016), ('Golden Ocean', 2013, 2016), ('INSW', 2016, 2018), ('Frontline', 2016, 2017), ('Euronav', 2016, 2018)):
    w = window(co, y0, y1)
    gl = 'gains not tagged, ' if w['gaps'] and co == 'Frontline' else ''
    print(f'  {co:12s} {y0}-{y1}: gains ${w["gain"]:,.0f}m, impairments ${w["imp"]:,.0f}m -> {w["net_roe"]:+.1%} of equity a year ({gl}{w["n"]} years)')
# what the forward_gains.py slope (0.31 points of ROE per point of drift) would have said for a 7.6%-a-year fall,
# the pace VLCC newbuild prices fell from 2008 to January 2015 (orderbook.py)
print(f'the symmetric slope predicts {0.31*-7.6:+.1f} points a year for a 7.6%-a-year fall')

# forward exposure: how much NAV moves for a 10% move in ship values (fleet value / NAV), published fleet values only
nav = {r['ticker']: (float(r['fleet_value_usd_m']), float(r['net_debt_usd_m']), float(r['close_2026_11_24']) * float(r['shares_m'])) for r in rows('peers_nav.csv')}
nav['CMBT'] = (10145.0, None, 17.54 * 290.169769)
print('NAV sensitivity to a 10% fall in ship values, and price/NAV, 24 Nov 2026:')
for t, (fv, nd, mc) in nav.items():
    n = fv - nd if nd is not None else 30.67 * 290.169769   # CMB.TECH: route-2 NAV (nav_bridge.py); route 1 is $25.02
    print(f'  {t:5s} fleet ${fv:,.0f}m, NAV ${n:,.0f}m: NAV {-0.1*fv/n:+.0%}; price/NAV {mc/n:.2f}')
