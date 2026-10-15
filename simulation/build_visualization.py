"""Embed saved simulation results into the in-conversation explorer fragment."""
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    args = parser.parse_args()
    manifest = json.loads((args.run / 'manifest.json').read_text())
    data = {}
    def convert(value):
        if value in ('True', 'False'):
            return value == 'True'
        try:
            return float(value)
        except ValueError:
            return value
    for model, config in manifest['models'].items():
        with (args.run / f'model_{model}.csv').open() as file:
            rows = [{k: convert(v) for k, v in row.items()} for row in csv.DictReader(file)]
        if len(rows) != config['rows']:
            raise ValueError(f'Model {model}: row count mismatch')
        data[model] = {'sweep': config['sweep'], 'rows': rows}
    if set(data) != set('123456789'):
        raise ValueError('Explorer requires a run containing all nine models')
    fragment = (ROOT / 'visualization-template.html').read_text().replace(
        '__SIMULATION_DATA__', json.dumps(data, separators=(',', ':'), allow_nan=False).replace('<', '\\u003c'))
    destination = args.run / 'procurement-simulations.html'
    destination.write_text(fragment)
    print(destination.resolve())


if __name__ == '__main__':
    main()
