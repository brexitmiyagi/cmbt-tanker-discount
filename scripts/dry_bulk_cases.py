# what 2028 looks like is the assumption the call turns on. 2027 is at the market's forward price in every case.
import json, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sh = 290.169769
tc = json.load(open(os.path.join(HERE, '..', 'results', 'through_cycle.json')))['through_cycle']
cases = {'base: 2028 halfway from the forward price to the 2015-2025 average': {},
         '2028 at the 2015-2025 average (no phasing)': {'CAPE28': str(tc['Capesize']), 'TANK28': 'cycle'},
         '2028 at 2025 rates': {'CAPE28': '21297', 'TANK28': '2025'},
         '2028 stays at the 2027 forward price': {'CAPE28': '31975', 'TANK28': 'deck'}}
res = {}
for name, ev in cases.items():
    f = os.path.join(tempfile.gettempdir(), 'cmbt_case.json')
    subprocess.run([sys.executable, os.path.join(HERE, 'model.py')], env={**os.environ, **ev, 'MODEL_OUT': f}, capture_output=True, check=True)
    r = json.load(open(f)); res[name] = r
    print(f'{name}: EPS 2027 ${r["fy27_eps"]:.2f}, 2028 ${r["fy28_eps"]:.2f} (consensus $1.91, {r["fy28_eps"]/1.91-1:+.0%}); 2028 FCF ${r["fcf28"]/sh:.2f}')
json.dump(res, open(os.path.join(HERE, '..', 'results', 'dry_bulk_cases.json'), 'w'), indent=1)
