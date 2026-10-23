#!/usr/bin/env python3
"""Reproduce historical 141-record analyses without storing results in git."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / 'scripts'

def execute(module, *arguments):
    subprocess.run([sys.executable, str(SCRIPTS / (module + '.py')), *map(str, arguments)], check=True)

def canonical_counts(output):
    data = pd.read_csv(output / 'rule_reassessment/outer_fold_rule_selections.csv')
    print('Available selection columns:', ', '.join(data.columns))
    feature_column = 'features'
    if feature_column not in data:
        raise ValueError('Expected original nested-selection features column.')
    data['canonical_features'] = data[feature_column].map(lambda x: ';'.join(sorted(str(x).split(';'))))
    keys = [x for x in ['rule', 'objective', 'canonical_features', 'percentile_band', 'band'] if x in data]
    if not any(x in keys for x in ['percentile_band', 'band']):
        # The original code stores percentile endpoints in separate columns.
        keys += [x for x in ['q_low', 'q_high', 'lower_pct', 'upper_pct', 'p_low', 'p_high', 'lo', 'hi'] if x in data]
    if len(keys) < 3:
        raise ValueError('Expected rule objective and percentile-band fields; inspect the newly generated table.')
    counts = data.groupby(keys, dropna=False).size().reset_index(name='count').sort_values('count', ascending=False)
    counts.to_csv(output / 'canonical_rule_selection_counts.csv', index=False)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['all', 'grouped', 'windows', 'rules', 'challenges', 'canonical-counts'])
    p.add_argument('--output-dir', type=Path, default=ROOT.parents[1] / 'curie_historical_outputs')
    p.add_argument('--n-jobs', type=int, default=8)
    args = p.parse_args()
    output = args.output_dir.resolve(); output.mkdir(parents=True, exist_ok=True)
    actions = ['grouped', 'windows', 'rules', 'challenges', 'canonical-counts'] if args.action == 'all' else [args.action]
    for action in actions:
        if action == 'grouped':
            execute('publication_grouped_analysis', '--data', ROOT / 'data/processed/development_unique_141.csv',
                    '--full-data', ROOT / 'data/processed/development_full_199.csv',
                    '--output-dir', output / 'grouped_cv', '--candidate-budget', '60', '--n-jobs', args.n_jobs)
        elif action == 'windows':
            execute('development_window_rules', '--data', ROOT / 'data/processed/development_unique_141.csv',
                    '--output-dir', output / 'development_windows')
            execute('historical_audit_metrics', '--data', ROOT / 'data/processed/historical_audit_32.csv',
                    '--output-dir', output / 'historical_audit')
        elif action == 'rules':
            execute('nested_rule_selection', '--data', ROOT / 'data/processed/development_unique_141.csv',
                    '--output-dir', output / 'rule_reassessment', '--n-jobs', args.n_jobs)
        elif action == 'challenges':
            rule = output / 'rule_reassessment/final_v2_rule.json'
            if not rule.exists():raise SystemExit('Run rules first in the same --output-dir.')
            execute('evaluate_frozen_rules', '--rule-file', rule,
                    '--historical', ROOT / 'data/processed/historical_audit_32.csv',
                    '--challenge', ROOT / 'data/processed/targeted_challenge_26.csv',
                    '--output-dir', output / 'external_rules')
        else:
            canonical_counts(output)

if __name__ == '__main__':
    main()
