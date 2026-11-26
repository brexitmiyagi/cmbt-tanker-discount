# what moves secondhand prices, on the evidence of backtest_capesize.py, is where they sit against newbuild prices.
# today a five-year-old trades above a newbuild in every segment CMB.TECH owns, because a ship on the water now earns
# war rates and a newbuild ordered today delivers around 2029-30 (yards are sold 3.7 years ahead). that premium is
# the price of prompt delivery, and it shrinks as the 2027-29 deliveries arrive. newbuild prices themselves have
# little reason to fall while yards are full. this script prints the newbuild paths and the drift if the premium
# goes back to its recent levels over three years with newbuild prices flat.
from common import rows
B = rows('broker_weekly_intermodal.csv')
o = {r['item']: float(r['value']) for r in rows('orderbook_2026.csv')}
print('newbuild prices, Intermodal ($m): ' + '; '.join(f'{r["report_date"][:7]} VLCC {r["vlcc_nb"]} Capesize {r["cape_nb"]}' for r in B[::4] + [B[-1]]))
print(f'VLCC 2008 peak ${o["vlcc_newbuild_2008_peak_usd_m"]}m (Poten) to ${o["vlcc_newbuild_jan_2015_usd_m"]}m Jan 2015 (Drewry); yard cover {o["yard_cover_years_nov_2026"]} years now vs 1.4 in 2020')
now = B[-1]
cases = {'VLCC': (float(now['vlcc_5yr_value']), float(now['vlcc_nb']), max(float(r['vlcc_5yr_value']) / float(r['vlcc_nb']) for r in B[:-2] if r['vlcc_5yr_value'])),
         'Suezmax': (float(now['suez_5yr_value']), float(now['suez_nb']), max(float(r['suez_5yr_value']) / float(r['suez_nb']) for r in B[:-2] if r['suez_5yr_value'])),
         'Capesize': (float(now['cape_5yr_value']), float(now['cape_nb']), max(float(r['cape_5yr_value']) / float(r['cape_nb']) for r in B[:-2]))}
dr = {}
for seg, (px, nb, hi) in cases.items():
    tgt = hi * nb; d = (tgt / px) ** (1 / 3) - 1; dr[seg] = d
    print(f'{seg:8s} five-year-old ${px}m against newbuild ${nb}m = {px/nb:.2f}; highest earlier ratio {hi:.2f} -> ${tgt:.0f}m, {tgt/px-1:+.0%}, {d:+.1%} a year over three years')
fleet = ((dr['VLCC'] + dr['Suezmax']) / 2 * 3128 + dr['Capesize'] * 7017) / 10145
print(f'CMB.TECH fleet mix: {fleet:+.1%} a year with newbuild prices flat')
