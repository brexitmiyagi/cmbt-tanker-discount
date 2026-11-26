# builds results/CMBT_model.xlsx: the same model as model.py, hormuz_paths.py and the target, as live Excel formulas.
# blue cells are inputs you can change. everything else is a formula.
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as L
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'results', 'CMBT_model.xlsx')
wb = Workbook()
BLUE = Font(color='0000FF'); BOLD = Font(bold=True); HEAD = PatternFill('solid', fgColor='DDE6EC')
Q = ['Q4 26', 'Q1 27', 'Q2 27', 'Q3 27', 'Q4 27', 'Q1 28', 'Q2 28', 'Q3 28', 'Q4 28']
C0 = 3  # first quarter column (C)
cols = [L(C0 + i) for i in range(9)]

# ---------------- Inputs ----------------
I = wb.active; I.title = 'Inputs'
I['A1'] = 'CMB.TECH (CMBT) model inputs. Blue = input. $m unless stated. Sources in column K.'; I['A1'].font = BOLD
gen = [
    ('shares', 'Shares outside treasury (m)', 290.169769, 'Q3 2026 release'),
    ('price', 'Share price ($), 24 Nov 2026', 17.54, 'Nasdaq'),
    ('payout', 'Payout ratio (of profit incl. gains)', 0.5, 'Q3 2026 call'),
    ('tax', 'Tax rate', (375.141 - 373.898) / 375.141, 'Q3 2026 release (tonnage tax)'),
    ('rate', 'Cost of debt (annual)', 4 * 74.039 / 4938.5, 'Q3 net finance cost x4 / gross debt'),
    ('sofr', 'Extra rate shock (e.g. 0.01 = +1pt)', 0.0, 'scenario input; 20-F: +1pt = $44.6m in 2025'),
    ('nd0', 'Net debt 30 Sep 2026', 4870.3, 'Q3 2026 release'),
    ('eq0', 'Book equity 30 Sep 2026', 3495.006, 'Q3 2026 release'),
    ('vess0', 'Vessels + under construction + held for sale, book', 6780.215 + 572.189 + 160.48, 'Q3 2026 release'),
    ('cash0', 'Cash (held flat)', 68.211, 'Q3 2026 release'),
    ('dist0', 'Q3 2026 distribution due ($/share)', 0.65, 'Q3 2026 release'),
    ('dep', 'Depreciation per quarter', 113.133, 'Q3 2026 release'),
    ('q3ex', 'Q3 2026 profit ex sale gains', 373.898 - 100.277, 'Q3 2026 release'),
    ('uplift', 'Ship value over book (broker fleet value $12,186m less vessels at book)', 12186 - 6780.215, 'Q3 2026 presentation slide 4 and release'),
    ('mult', 'Price/NAV applied to forward NAV (broker basis)', 0.62, 'best CMBT level on this basis, nav_reconcile.py'),
    ('drybulk', 'Dry bulk broker value 30 Sep 2026', 7017, 'Q3 2026 presentation slide 4'),
    ('tankfmv', 'Tanker broker value 30 Sep 2026', 3128, 'Q3 2026 presentation slide 4'),
    ('drycut', 'Dry bulk value change by end-2027 (halfway back to end-2025 value per ship)', 0.5 * ((6329 / 103) / (7017 / 108) - 1), 'hormuz_paths.py'),
]
N = {}
r = 3
for key, label, val, src in gen:
    I.cell(r, 1, label); c = I.cell(r, 2, val); c.font = BLUE; I.cell(r, 11, src); N[key] = f'Inputs!$B${r}'; r += 1
r += 1
I.cell(r, 1, 'Segment inputs').font = BOLD; r += 1
segs = ['VLCC', 'Suezmax', 'Newcastlemax', 'Capesize', 'Kamsarmax']
be = {'VLCC': 34769, 'Suezmax': 25512, 'Newcastlemax': 29823, 'Capesize': 21096, 'Kamsarmax': 14659}
tcr = {'VLCC': 85623, 'Suezmax': 32986, 'Newcastlemax': 35942, 'Capesize': 28879, 'Kamsarmax': 17557}
q3r = {'VLCC': 149945, 'Suezmax': 148540, 'Newcastlemax': 43001, 'Capesize': 35525, 'Kamsarmax': 20183}
q4qtd = {'VLCC': (635199, .59), 'Suezmax': (377164, .68), 'Newcastlemax': (48835, .81), 'Capesize': (41634, .78), 'Kamsarmax': (20657, .87)}
deck = {'VLCC': 122500, 'Suezmax': 77500, 'Newcastlemax': 40608, 'Capesize': 31975, 'Kamsarmax': 17050}
pre = {'VLCC': 46352.5, 'Suezmax': 48576.0}   # CMB.TECH's 2025 spot averages (cmbt_tanker_tce_2025.csv)
# one rule (model.py): 2027 at the forward price (company deck), 2028 halfway to the 2015-2025 through-cycle average
import json as _jj
_tc = _jj.load(open(os.path.join(HERE, '..', 'results', 'through_cycle.json')))['through_cycle']
CAPE27, CAPE28 = 31975, (31975 + _tc['Capesize']) / 2
R28 = {'VLCC': (122500 + _tc['VLCC']) / 2, 'Suezmax': (77500 + _tc['Suezmax']) / 2}
DRYSEG = ('Newcastlemax', 'Capesize', 'Kamsarmax')
spot27 = {'VLCC': 1633, 'Suezmax': 2839, 'Newcastlemax': 15510, 'Capesize': 11260, 'Kamsarmax': 10560}
q3days = {'VLCC': (5 * 92 - 184, 184), 'Suezmax': (17 * 92 - 717, 717), 'Newcastlemax': (41 * 92 - 24, 24), 'Capesize': (37 * 92 - 435, 435), 'Kamsarmax': (30 * 92 - 286, 286)}
q4spot = {'VLCC': 3 * 92, 'Suezmax': 6 * 92, 'Newcastlemax': 41 * 92 * 100 / 108, 'Capesize': 37 * 92 * 100 / 108, 'Kamsarmax': 30 * 92 * 100 / 108}
for i, q in enumerate(Q):
    I.cell(r, C0 + i, q).font = BOLD
hdr = r; r += 1
S = {}
for s in segs:
    I.cell(r, 1, s).font = BOLD; r += 1
    S[s] = {}
    for key, label in (('be', 'P&L breakeven $/day (slides 13, 24)'), ('tc', 'Time charter rate $/day (Q3 2026 average)'), ('q3rate', 'Q3 2026 spot $/day'), ('q3spot', 'Q3 2026 spot days'), ('q3tc', 'Q3 2026 charter days')):
        v = {'be': be[s], 'tc': tcr[s], 'q3rate': q3r[s], 'q3spot': q3days[s][0], 'q3tc': q3days[s][1]}[key]
        I.cell(r, 1, '  ' + label); c = I.cell(r, 2, v); c.font = BLUE; S[s][key] = f'Inputs!$B${r}'; r += 1
    for key, label in (('rate', '  Spot rate $/day'), ('spot', '  Spot days'), ('tcd', '  Charter days')):
        I.cell(r, 1, label)
        S[s][key] = r
        for i in range(9):
            if key == 'rate':
                if i == 0:
                    a, f = q4qtd[s]; v = f * a + (1 - f) * q3r[s]
                elif i <= 4: v = deck[s] * CAPE27 / 31975 if s in DRYSEG else deck[s]
                else: v = R28.get(s, deck[s] * CAPE28 / 31975)
            elif key == 'spot':
                v = q4spot[s] if i == 0 else spot27[s] / 4
            else:
                if s == 'VLCC': v = 92 if i == 0 else (96 if i <= 2 else 0)
                elif s == 'Suezmax': v = 717 if i == 0 else (14 * 365 - 2839) / 4
                else: v = q3days[s][1]
            c = I.cell(r, C0 + i, v); c.font = BLUE
        r += 1
r += 1
I.cell(r, 1, 'Per quarter').font = BOLD; r += 1
rowsq = {}
for key, label, vals in (('capex', 'Capex (slide 9; 2028 = rest of $843m)', [167, 223, 88, 57, 30, 69.5, 69.5, 69.5, 69.5]),
                         ('gains', 'Sale gains booked', [190.8] + [0] * 8),
                         ('proc', 'Sale proceeds (Donoussa, Bristol: book + gain)', [160.48 + 74.3 + 56.9] + [0] * 8),
                         ('hfs', 'Book value of ships delivered to buyers', [160.48] + [0] * 8),
                         ('nwc', 'Working capital release (+) / build (-)', [0] * 9)):
    I.cell(r, 1, label); rowsq[key] = r
    for i, v in enumerate(vals):
        c = I.cell(r, C0 + i, v); c.font = BLUE
    r += 1
I.column_dimensions['A'].width = 52

# ---------------- Model ----------------
M = wb.create_sheet('Model')
M['A1'] = 'Quarterly P&L, cash flow and balance sheet ($m)'; M['A1'].font = BOLD
for i, q in enumerate(Q):
    M.cell(2, C0 + i, q).font = BOLD
r = 3
M.cell(r, 1, 'Calibration: Q3 2026 modelled segments');
calib = '+'.join(f"{S[s]['q3spot']}*({S[s]['q3rate']}-{S[s]['be']})+{S[s]['q3tc']}*({S[s]['tc']}-{S[s]['be']})" for s in segs)
M.cell(r, 2, f'=({calib})/1000000'); rc = r; r += 1
M.cell(r, 1, 'Everything else per quarter (calibrated)'); M.cell(r, 2, f"={N['q3ex']}-B{rc}"); rres = r; r += 2
R = {}
def row(label, fn, bold=False):
    global r
    M.cell(r, 1, label)
    if bold: M.cell(r, 1).font = BOLD
    for i, col in enumerate(cols):
        M.cell(r, C0 + i, fn(i, col))
    R[label] = r; r += 1
    return r - 1
for s in segs:
    row(f'{s} profit contribution', lambda i, c, s=s: f"=(Inputs!{c}{S[s]['spot']}*(Inputs!{c}{S[s]['rate']}-{S[s]['be']})+Inputs!{c}{S[s]['tcd']}*({S[s]['tc']}-{S[s]['be']}))/1000000")
row('Containership newbuild (Q3 container margin)', lambda i, c: ('=0' if i == 0 else '=91*(29681-21353)/1000000'))
row('Everything else', lambda i, c: f'=$B${rres}')
row('Interest saving vs 2026 budget', lambda i, c: f"=({N['nd0']}-{c}{{ndo}})*{N['rate']}/4-{N['sofr']}*{c}{{ndo}}/4")
row('Profit before tax, ex gains', lambda i, c: f"=SUM({c}{R['VLCC profit contribution']}:{c}{R['Interest saving vs 2026 budget']})", True)
row('Tax', lambda i, c: f"=-{c}{R['Profit before tax, ex gains']}*{N['tax']}")
row('Profit ex gains', lambda i, c: f"={c}{R['Profit before tax, ex gains']}+{c}{R['Tax']}", True)
row('Sale gains', lambda i, c: f"=Inputs!{c}{rowsq['gains']}")
row('Net profit', lambda i, c: f"={c}{R['Profit ex gains']}+{c}{R['Sale gains']}", True)
row('EPS ($)', lambda i, c: f"={c}{R['Net profit']}/{N['shares']}")
r += 1
M.cell(r, 1, 'Cash flow').font = BOLD; r += 1
row('Profit ex gains (cash)', lambda i, c: f"={c}{R['Profit ex gains']}")
row('Depreciation', lambda i, c: (f"={N['dep']}" if i == 0 else f"={N['dep']}+SUM(Inputs!$C${rowsq['capex']}:{cols[i-1]}${rowsq['capex']})/100"))
row('Working capital', lambda i, c: f"=Inputs!{c}{rowsq['nwc']}")
row('Capex', lambda i, c: f"=-Inputs!{c}{rowsq['capex']}")
row('Sale proceeds', lambda i, c: f"=Inputs!{c}{rowsq['proc']}")
row('Free cash flow', lambda i, c: f"=SUM({c}{R['Profit ex gains (cash)']}:{c}{R['Sale proceeds']})", True)
row('Distributions paid', lambda i, c: (f"=-{N['dist0']}*{N['shares']}" if i == 0 else f"=-{cols[i-1]}{{distdecl}}"))
row('Distributions declared', lambda i, c: f"={c}{R['Net profit']}*{N['payout']}")
row('Cash left for debt', lambda i, c: f"={c}{R['Free cash flow']}+{c}{R['Distributions paid']}")
r += 1
M.cell(r, 1, 'Balance sheet (condensed)').font = BOLD; r += 1
row('Net debt, opening', lambda i, c: (f"={N['nd0']}" if i == 0 else f"={cols[i-1]}{{ndc}}"))
row('Net debt, closing', lambda i, c: f"={c}{R['Net debt, opening']}-{c}{R['Cash left for debt']}", True)
row('Cash (held flat)', lambda i, c: f"={N['cash0']}")
row('Gross debt', lambda i, c: f"={c}{R['Net debt, closing']}+{c}{R['Cash (held flat)']}")
row('Vessels and newbuilds, book', lambda i, c: (f"={N['vess0']}" if i == 0 else f"={cols[i-1]}{{vb}}") + f"-Inputs!{c}{rowsq['capex']}*-1-{N['dep']}-Inputs!{c}{rowsq['hfs']}")
row('Book equity', lambda i, c: (f"={N['eq0']}" if i == 0 else f"={cols[i-1]}{{eqr}}") + f"+{c}{R['Net profit']}+{c}{R['Distributions paid']}", True)
row('Other net assets (balancing, see note)', lambda i, c: f"={c}{R['Book equity']}+{c}{R['Net debt, closing']}-{c}{R['Vessels and newbuilds, book']}")
row('Book equity a share ($)', lambda i, c: f"={c}{R['Book equity']}/{N['shares']}")
# resolve placeholders
ph = {'{ndo}': str(R['Net debt, opening']), '{distdecl}': str(R['Distributions declared']), '{ndc}': str(R['Net debt, closing']), '{vb}': str(R['Vessels and newbuilds, book']), '{eqr}': str(R['Book equity'])}
for rr in M.iter_rows():
    for cell in rr:
        if isinstance(cell.value, str):
            v = cell.value
            for k, x in ph.items(): v = v.replace(k.replace('{', '{').strip(), x) if False else v.replace('{' + k.strip('{}') + '}', x)
            cell.value = v
M.column_dimensions['A'].width = 42
M.cell(r + 1, 1, 'Note: other net assets (receivables, payables, goodwill, JVs) move only with sale gains booked against held-for-sale ships; working capital is an input on the Inputs sheet.')

# ---------------- Summary ----------------
Y = wb.create_sheet('Summary')
Y['A1'] = 'Annual summary, valuation and Hormuz paths'; Y['A1'].font = BOLD
Y['B2'], Y['C2'], Y['D2'] = 'FY2026', 'FY2027', 'FY2028'
for c in ('B2', 'C2', 'D2'): Y[c].font = BOLD
Y['A3'] = 'Net profit ($m)'; Y['B3'] = f"=1107.1+Model!C{R['Net profit']}"; Y['C3'] = f"=SUM(Model!D{R['Net profit']}:G{R['Net profit']})"; Y['D3'] = f"=SUM(Model!H{R['Net profit']}:K{R['Net profit']})"
Y['A4'] = 'EPS ($)'; Y['B4'] = f"=B3/{N['shares']}"; Y['C4'] = f"=C3/{N['shares']}"; Y['D4'] = f"=D3/{N['shares']}"
Y['A5'] = 'EPS ex sale gains ($)'; Y['B5'] = f"=(B3-495.146-Model!C{R['Sale gains']})/{N['shares']}"; Y['C5'] = '=C4'; Y['D5'] = '=D4'
Y['A6'] = 'Consensus EPS (Seeking Alpha, 25 Nov 2026)'; Y['B6'], Y['C6'], Y['D6'] = 4.38, 2.16, 1.91
for c in ('B6', 'C6', 'D6'): Y[c].font = BLUE
Y['A7'] = 'Mine vs consensus'; Y['B7'] = '=B5/B6-1'; Y['C7'] = '=C4/C6-1'; Y['D7'] = '=D4/D6-1'
Y['A8'] = 'Free cash flow ($m)'; Y['C8'] = f"=SUM(Model!D{R['Free cash flow']}:G{R['Free cash flow']})"; Y['D8'] = f"=SUM(Model!H{R['Free cash flow']}:K{R['Free cash flow']})"
Y['A9'] = 'Net debt, year end ($m)'; Y['B9'] = f"=Model!C{R['Net debt, closing']}"; Y['C9'] = f"=Model!G{R['Net debt, closing']}"; Y['D9'] = f"=Model!K{R['Net debt, closing']}"
Y['A10'] = 'Distributions paid, next 12 months ($/share)'; Y['B10'] = f"=-SUM(Model!C{R['Distributions paid']}:F{R['Distributions paid']})/{N['shares']}"
Y['A12'] = 'Forward NAV end-2027 before charter marks ($m, broker basis)'; Y['B12'] = f"=Model!G{R['Book equity']}+{N['uplift']}"
Y['A13'] = 'Forward NAV a share ($)'; Y['B13'] = f"=B12/{N['shares']}"
Y['A14'] = 'Value at the chosen price/NAV ($), no charter marks, tanker values flat'; Y['B14'] = f"=B13*{N['mult']}"
Y['A16'] = 'Hormuz paths'; Y['A16'].font = BOLD
for j, h in enumerate(['Probability', 'Share of 2027 at pre-war rates', 'Share of 2027 at 1-yr charter rates', 'Tanker value change', 'Charter marks $m (hormuz_paths.py)', 'Value a share ($)', 'Dry bulk -20% in total ($)', 'At 0.55x', 'At 0.70x']):
    Y.cell(16, 2 + j, h).font = BOLD
cutf = '=(2383/22)/(3128/20)-1'
import json
_hp = json.load(open(os.path.join(HERE, '..', 'results', 'hormuz_paths.json')))
paths = [('A. Reopens Q1 2027', .20, .75, 0, cutf, _hp['A']['marks']), ('B. Reopens H2 2027', .25, .5, 0, cutf, _hp['B']['marks']), ('C. Opens, mines keep risk high', .25, 0, 0, '=((2383/22)/(3128/20)-1)/2', _hp['C']['marks']), ('D. Stays shut through 2027', .30, 0, 1, 0, _hp['D']['marks'])]
for k, (nm, p, fp, ft, cut, mk) in enumerate(paths):
    rr = 17 + k
    Y.cell(rr, 1, nm)
    for j, v in enumerate((p, fp, ft, cut, mk)):
        c = Y.cell(rr, 2 + j, v); c.font = BLUE
    dprof = f"(1633*(C{rr}*(46352.5-122500)+D{rr}*(234000-122500))+2839*(C{rr}*(48576-77500)+D{rr}*(136250-77500)))/1000000"
    nav = f"($B$12+E{rr}*{N['tankfmv']}+{N['payout']}*{dprof}-F{rr}+{N['drycut']}*{N['drybulk']})"
    Y.cell(rr, 7, f"={N['mult']}*{nav}/{N['shares']}")
    Y.cell(rr, 8, f"={N['mult']}*({nav}-(0.2+{N['drycut']})*{N['drybulk']})/{N['shares']}")
    Y.cell(rr, 9, f"=0.55*{nav}/{N['shares']}")
    Y.cell(rr, 10, f"=0.70*{nav}/{N['shares']}")
Y['A22'] = 'Probability-weighted'; Y['B22'] = '=SUM(B17:B20)'
for col in 'GHIJ':
    Y[f'{col}22'] = f'=SUMPRODUCT($B$17:$B$20,{col}17:{col}20)'
Y['A23'] = 'Upside case: value at the best multiple (0.62x), rounded down. The published $16.00 target is in payoff_both_routes.py'; Y['G23'] = '=FLOOR(G22,0.5)'
Y['A24'] = 'Upside to target'; Y['G24'] = f"=G23/{N['price']}-1"
Y['A25'] = 'Total return with 12-month distributions'; Y['G25'] = f"=(G23+B10)/{N['price']}-1"
Y['A26'] = 'Bear case (dry bulk -20%), total return with distributions'; Y['G26'] = f"=(H22+B10)/{N['price']}-1"
Y['A28'] = 'Market cross-checks (weights A/B/C/D)'; Y['A28'].font = BOLD
for k, (nm, w) in enumerate([('Polymarket ladder, 25 Nov 2026', (0.125, 0.23, 0, 0.645)), ('Kalshi KXHORMUZNORM, 25 Nov 2026', (0.12, 0.21, 0, 0.67))]):
    rr = 29 + k
    Y.cell(rr, 1, nm)
    for j, v in enumerate(w):
        c = Y.cell(rr, 2 + j, v); c.font = BLUE
    Y.cell(rr, 7, f'=SUMPRODUCT(B{rr}:E{rr},TRANSPOSE(G17:G20))')
Y['A32'] = 'Path C uses half the pre-war cut; the pre-war cut is the company\'s tanker value per ship at end-2025 vs 30 Sep 2026. Charter marks are the present value of what the chartered ships give up against each path\'s market rates (hormuz_paths.py, 3 years assumed left on the 8 charters without disclosed end dates).'
Y.column_dimensions['A'].width = 48
for ws in (I, M, Y):
    ws.freeze_panes = 'B3'
wb.save(OUT)
print('wrote', OUT)
