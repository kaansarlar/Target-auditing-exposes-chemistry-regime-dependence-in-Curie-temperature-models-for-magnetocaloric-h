#!/usr/bin/env python3
"""Run conservative Curie-temperature analyses with untracked output locations."""
from pathlib import Path
import argparse
import importlib
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'scripts'))

def check_inputs():
    data = pd.read_csv(ROOT / 'data/strict_experimental_tc_72.csv')
    broader = pd.read_csv(ROOT / 'data/strict_experimental_tc_79_broader.csv')
    ledger = pd.read_csv(ROOT / 'data/record_audit_141_conservative.csv')
    annotation = pd.read_csv(ROOT / 'data/processing_phase_annotation_seed.csv')
    assert len(data) == 72 and data.reference_id.nunique() == 25
    assert len(broader) == 79 and len(ledger) == 141
    assert not data.reference_id.eq('[15]').any()
    assert set(broader.loc[~broader.reference_id.eq('[15]'), 'source_row']) == set(data.source_row)
    assert not data.source_row.duplicated().any()
    assert sorted(data.chemistry_family.value_counts().tolist()) == [22, 25, 25]
    assert {'source_row', 'model_eligibility', 'process_route', 'thermal_state', 'phase_class', 'product_form'}.issubset(annotation.columns)
    for name in ['numpy', 'pandas', 'scipy', 'sklearn', 'lightgbm', 'xgboost']:
        importlib.import_module(name)
    print('PASS: 72 primary records / 25 publications; broader selection, ledger and metadata verified.')

def run(action, jobs, output, models=None):
    module = {
        'models': 'run_strict_tc_analysis',
        'robustness': 'run_strict_tc_robustness',
        'classification': 'run_strict_tc_classification',
        'process': 'run_process_phase_extension',
    }[action]
    m = importlib.import_module(module)
    m.DATA = ROOT / 'data/strict_experimental_tc_72.csv'
    targets = {'models':'strict_tc_grouped_cv', 'robustness':'strict_tc_robustness',
               'classification':'strict_tc_classification', 'process':'strict_tc_process_phase'}
    m.OUT = output / targets[action]
    m.DEFAULT_OUT = m.OUT
    m.CV = output / 'strict_tc_grouped_cv'
    m.ANNOTATION = ROOT / 'data/processing_phase_annotation_seed.csv'
    if action == 'robustness' and not (m.CV / 'strict_model_summary.csv').exists():
        raise SystemExit('Run models first in the same --output-dir.')
    budget = 60 if action in ['models', 'process'] else 30
    sys.argv = [module, '--candidate-budget', str(budget), '--n-jobs', str(jobs)]
    if action in ['models', 'process']:
        sys.argv += ['--output-dir', str(m.OUT)]
    if action == 'models' and models:
        sys.argv += ['--models', models]
    m.main()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['check', 'all', 'models', 'robustness', 'classification', 'process'])
    p.add_argument('--n-jobs', type=int, default=8)
    p.add_argument('--output-dir', type=Path, default=ROOT.parents[1] / 'curie_outputs')
    p.add_argument('--models', help='Optional comma-separated subset for the models action; all seven are the publication protocol.')
    args = p.parse_args()
    check_inputs()
    if args.action == 'check':
        return
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    for action in (['models', 'robustness', 'classification', 'process'] if args.action == 'all' else [args.action]):
        run(action, args.n_jobs, output, args.models)

if __name__ == '__main__':
    main()
