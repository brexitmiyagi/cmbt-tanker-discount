# the bear case puts CMB.TECH back on its pre-war multiple when the strait reopens. is that what happened after the last
# tanker spikes? two in a row: Oct 2019 (COSCO sanctions) and Mar-Apr 2020 (floating storage, VLCCs above $200,000 a
# day). free NAV history isn't available, so this uses price to book, which is the same idea with book in place of
# broker values. INSW files quarterly, so it gives the full path; Euronav and DHT file annually.
from common import rows
P = rows('spike_history_pb.csv')
by = {}
for r in P:
    pb = float(r['price_usd']) / (float(r['book_equity_usd_m']) / float(r['shares_m']))
    by.setdefault(r['company'], []).append((r['date'], pb))
for co, s in by.items():
    print(f'{co}: ' + ', '.join(f'{d} {pb:.2f}' for d, pb in s))
    hi = max(x for _, x in s); lo = min(x for _, x in s)
    print(f'  peak to trough after the spikes: {lo/hi-1:+.0%}')
print('CMB.TECH now, route 2 price/NAV: 0.62 at 30 Sep 2026 against 0.40 at end-2025 (nav_reconcile.py), a fall of '
      f'{0.40/0.62-1:+.0%} if it goes back. after 2019-20 the three fell by 38% to 56%, so the size of the bear move is in the range')
print('of the last episode. the 2020 spike lasted about two months, this one nine, so it is an imperfect comparison.')
