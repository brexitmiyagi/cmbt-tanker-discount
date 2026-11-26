# checks the Excel model (results/CMBT_model.xlsx, values as last calculated) against the Python model.
# needs openpyxl. if you change inputs in Excel, recalculate and save before running this.
import json, os
from openpyxl import load_workbook
HERE = os.path.dirname(os.path.abspath(__file__))
wb = load_workbook(os.path.join(HERE, '..', 'results', 'CMBT_model.xlsx'), data_only=True)
Y = wb['Summary']
ms = json.load(open(os.path.join(HERE, '..', 'results', 'model_summary.json')))
pairs = [('FY2027 EPS', Y['C4'].value, ms['fy27_eps']), ('FY2028 EPS', Y['D4'].value, ms['fy28_eps']), ('12-month distributions', Y['B10'].value, ms['dist12'])]
for n, a, b in pairs:
    print(f'{n}: Excel {a:.4f}, Python {b:.4f}, {"match" if abs(a - b) < 1e-6 else "MISMATCH"}')
print(f"Excel probability-weighted value at 0.62x ${Y['G22'].value:.2f}, rounded ${Y['G23'].value:.2f}")
hp = json.load(open(os.path.join(HERE, '..', 'results', 'hormuz_paths.json')))
print(f'weighted value: Excel {Y["G22"].value:.4f}, Python {hp["w_mine (Sameer)"]["value"]:.4f}, {"match" if abs(Y["G22"].value - hp["w_mine (Sameer)"]["value"]) < 1e-3 else "MISMATCH"}')
