# what burning ammonia costs a Newcastlemax per day against VLSFO, at today's fuel prices.
# physics: VLSFO about 41 MJ/kg and ammonia about 18.6 MJ/kg (lower heating values), so ammonia takes about 2.2x the
# mass for the same energy. engine load and specific consumption are my assumptions: 165 g/kWh, 60% and 85% of the
# continuous service rating. dual-fuel ammonia engines still burn some pilot fuel; I use 8% of energy from VLSFO.
from common import rows
p = {r['item']: float(r['value']) for r in rows('fuel_prices_2026-11.csv')}
LHV_VLSFO, LHV_NH3, SFOC, PILOT = 41.0, 18.6, 165.0, 0.08
for load in (0.60, 0.85):
    t_vlsfo = p['newcastlemax_csr_kw'] * load * 24 * SFOC / 1e6           # tonnes a day on VLSFO
    cost_v = t_vlsfo * p['vlsfo_singapore_usd_t']
    t_nh3 = t_vlsfo * (1 - PILOT) * LHV_VLSFO / LHV_NH3
    for lab, px in (('grey, NW Europe Sep 2026', p['ammonia_nw_europe_cfr_usd_t']),
                    ('green, delivered, late 2025 low', p['green_ammonia_delivered_usd_t_low']),
                    ('green, high', p['green_ammonia_delivered_usd_t_high'])):
        cost_a = t_nh3 * px + t_vlsfo * PILOT * p['vlsfo_singapore_usd_t']
        print(f'load {load:.0%}: VLSFO {t_vlsfo:.0f} t/day = ${cost_v:,.0f}/day; ammonia ({lab} ${px:.0f}/t) {t_nh3:.0f} t/day + pilot = ${cost_a:,.0f}/day, '
              f'${cost_a-cost_v:+,.0f}/day more')
print('a dual-fuel ship can burn VLSFO instead, so the extra cost applies to the days it burns ammonia. at a 2027 forward Newcastlemax rate of')
print('$40,608 a day (structure_and_green.py), a day on grey ammonia costs roughly half to three-quarters of that day\'s hire in extra fuel at sea.')
