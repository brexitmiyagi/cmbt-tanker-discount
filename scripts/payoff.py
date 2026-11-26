# the upside case only: route 2 (broker basis) held at its best price/NAV, 0.62x. the published target and the
# real bear case, with the multiple allowed to reset and both NAV routes, are in payoff_both_routes.py.
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
ms = json.load(open(os.path.join(HERE, '..', 'results', 'model_summary.json')))
hp = json.load(open(os.path.join(HERE, '..', 'results', 'hormuz_paths.json')))
px = 17.54
w = hp['w_mine (Sameer)']
target = int(w['value'] * 2) / 2   # rounded down to the nearest $0.50
dist = ms['dist12']
print(f'probability-weighted value (A/B/C/D at 20/25/25/30): ${w["value"]:.2f} -> at the best multiple ${target:.2f} ({target/px-1:+.1%})')
print(f'12-month distributions about ${dist:.2f} = {dist/px:.1%}; total {(target+dist)/px-1:+.1%}')
print(f'dry bulk -20% with the multiple still at 0.62x (dry bulk values -20% in every path): ${w["bear"]:.2f} ({w["bear"]/px-1:+.1%}), {(w["bear"]+dist)/px-1:+.1%} with distributions')
print(f'multiple sensitivity: 0.55x ${w["s55"]:.2f}, 0.62x ${w["value"]:.2f}, 0.70x ${w["s70"]:.2f}')
print(f'Q3 charter gap $82.9m = $0.29 a share; spot is {148540/32986:.1f}x the charter average')
