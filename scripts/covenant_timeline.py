# why did the share of fleet value over book that the covenant measure leaves out fall from 55% at the end of 2025
# to 32% by June? the only facility agreement on file is the March 2025 bridge, whose "Vessels" are only ships
# "fully owned by a member of the Group" (so leaseback ships are out). the debt tables show when it went away.
import json, os
from common import rows
HERE = os.path.dirname(os.path.abspath(__file__))
c = {r['item']: r['text'] for r in rows('covenant_definitions.csv')}
print(f'bridge drawn: 31 Dec 2025 ${float(c["bridge_drawn_2025-12-31_usd_k"])/1000:.1f}m, 30 Jun 2026 ${float(c["bridge_drawn_2026-06-30_usd_k"])/1000:.1f}m')
print(f'$2bn facility margin: 31 Dec 2025 {c["facility_2b_margin_2025-12-31"]}, 30 Jun 2026 {c["facility_2b_margin_2026-06-30"]} (repriced in the half)')
print(f'exhibits filed with the 2025 20-F: {c["only_facility_agreement_filed"]}')
nc = open(os.path.join(HERE, '..', 'results', 'nav_covenant.txt')).read()
print('share of fleet value over book left out of the covenant measure, from nav_covenant.py:')
print('  ' + '\n  '.join(l for l in nc.splitlines() if 'left out' in l or 'outside' in l or '%' in l)[:1200])
print('so the gap was widest while the bridge, with the narrow definition, was still drawn, and shrank in the half the')
print('bridge was repaid and the $2bn facility was repriced. that fits a change in which definition governs the reported')
print('ratio. it does not prove it: the newer facility agreements are not on file.')
