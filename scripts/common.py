# small helpers shared by the scripts. everything loads from ../data relative to this file
import os, csv
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')

def rows(name):
    with open(os.path.join(DATA, name), newline='') as f:
        return list(csv.DictReader(f))

def kv(name, key='line', val='usd_thousands'):
    return {r[key]: float(r[val]) for r in rows(name)}
