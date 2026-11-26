# what a short has to check before putting the trade on. short interest from FINRA (via equibles), free float from
# structure_and_green.py's share register (CMB NV and treasury out). borrow cost: no free source I could find.
from common import rows
si = rows('short_interest_2026-11.csv')
free_float = 3.207486 / 0.029   # structure_and_green.py: 3.207m short = 2.9% of free float -> about 110.6m shares
for r in si:
    s = float(r['shares_short']) / 1e6
    print(f'{r["settlement_date"]}: {s:.2f}m shares short, about {s/free_float:.1%} of free float, {r["days_to_cover"]} days to cover')
print('borrow cost: not published for free; get a quote from the prime broker before sizing')
