# the 2026 tanker sales, split by whether they were agreed before or after the strait shut at the end of February.
# gains are the company's own figures (6-K releases and the Q3 2026 release). sale prices are not disclosed.
from common import rows
s = rows('tanker_sales_2026.csv')
tot = sum(float(r['gain_usd_m']) for r in s)
pre = sum(float(r['gain_usd_m']) for r in s if r['before_war'] == 'yes')
vl = sum(float(r['gain_usd_m']) for r in s if r['type'].startswith('VLCC'))
sz = sum(float(r['gain_usd_m']) for r in s if r['type'].startswith('Suezmax'))
for r in s:
    print(f'{r["announced"]}  {r["type"]:11s} {r["vessels"]:46s} built {r["built"]:9s} gain ${float(r["gain_usd_m"]):6.1f}m  {r["delivery"]}')
print(f'total 2026 tanker gains ${tot:.1f}m: VLCCs ${vl:.1f}m, Suezmaxes ${sz:.1f}m')
print(f'agreed before the war ${pre:.1f}m ({pre/tot:.0%}), after ${tot-pre:.1f}m')
print(f'gains per share ${tot/290.169769:.2f}')
