"""Build independent Python reference values for the browser implementation."""
import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'simulation'))
from models import solve

config = json.loads((ROOT.parent / 'simulation' / 'config.json').read_text())
fixtures = []
for model, spec in config.items():
    for values in itertools.product(*spec['sweep'].values()):
        p = spec['parameters'] | dict(zip(spec['sweep'], values))
        fixtures.append(dict(model=model, parameters=p, expected=solve(model, p)))
for model, p in [('2', {'w': .375}), ('3', {'t': 100}), ('4', {'m': 0, 't': 2}),
                 ('7', {'F': 0, 'R': 0}), ('7', {'H': 2}),
                 ('5', {'omega': .6}), ('5', {'omega': 1}), ('5', {'ell': 2}),
                 ('8', {'theta': 0}), ('8', {'w': 1, 'p': 0}), ('8', {'lam': 0, 'w': .1}),
                 ('9', {'h': 20}), ('9', {'R': 10, 't': 0}), ('9', {'kappa': 15}), ('9', {'f': 12, 't': 8})]:
    fixtures.append(dict(model=model, parameters=p, expected=solve(model, p)))
(ROOT / 'fixtures.json').write_text(json.dumps(fixtures, indent=2, allow_nan=False)+'\n')
print(f'Generated {len(fixtures)} Python reference scenarios')
