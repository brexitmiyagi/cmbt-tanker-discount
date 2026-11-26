# the crude tanker fleet ship by ship, from the 20-F list (1 April 2026) and the 2026 releases.
from common import rows
f = rows('fleet_crude_tankers.csv')
sz = [r for r in f if r['type'] == 'Suezmax' and r['status_25_nov_2026'] == 'on the water']
tc = [r['vessel'] for r in sz if r['employment_1_apr_2026'] == 'Time Charter']
sp = [r['vessel'] for r in sz if r['employment_1_apr_2026'] == 'Spot']
val = [r['vessel'] for r in sz if 'Valero' in r['charterer_if_known']]
sold = [r['vessel'] for r in f if r['status_25_nov_2026'].startswith('sold')]
sold_tc = [r['vessel'] for r in f if r['status_25_nov_2026'].startswith('sold') and r['employment_1_apr_2026'] == 'Time Charter']
print(f'Suezmaxes on the water: {len(sz)}; on time charter in April: {len(tc)}; spot in April: {len(sp)} ({", ".join(sp)})')
print(f'built for or chartered to Valero: {len(val)} ({", ".join(val)})')
print(f'Q3 2026 charter days 717 = {717/92:.1f} ships, so up to {len(tc) - 717/92:.1f} ships came off charter or were off hire in Q3')
print(f'tankers sold since the April list: {len(sold)}, of which on time charter: {len(sold_tc)} ({", ".join(sold_tc)})')
