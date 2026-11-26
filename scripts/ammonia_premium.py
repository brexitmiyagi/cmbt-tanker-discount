# what the ammonia Newcastlemaxes need. breakevens from structure_and_green.py: $30,095/day to earn 8% on a
# conventional-cost ship, $34,706/day with a 20% ammonia premium on cost. against what a Newcastlemax earns at the
# 2027 forward price, at 2025 rates and at the through-cycle Capesize level (Newcastlemax deck scaled by the Capesize
# ratio, as in model.py).
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
tc = json.load(open(os.path.join(HERE, '..', 'results', 'through_cycle.json')))['through_cycle']
ncm27, cape27 = 40608, 31975
for lab, cape in (('2027 forward', cape27), ('2025 rates', 21297), ('through-cycle', tc['Capesize'])):
    n = ncm27 * cape / cape27
    print(f'{lab}: Newcastlemax ${n:,.0f}/day; vs ${34706:,} needed with the ammonia premium: {n-34706:+,.0f} ({34706/n-1:+.0%} premium needed)')
