# Curie-temperature target auditing

Data and reproducible analysis code for **Target auditing exposes chemistry-regime dependence in Curie-temperature models for magnetocaloric high-entropy alloys**.

This source repository contains data, source manifests, code, environment requirements and documentation. Model outputs, saved predictions, fitted models and rendered figures are not tracked. Generate them in a separate output directory; reference numerical outputs remain available in the journal Supplementary Data archive and in the earlier Zenodo release where applicable.

## Primary conservative analysis

The primary cohort contains **72 records from 25 publications**. It excludes seven peak-defined source-[15] Perrin et al. records from the broader 79-record cohort. The source authors also discuss those values as Curie temperatures; their exclusion is an operational admissibility choice, not an allegation of measurement error. Source identifiers in CSV files are not manuscript reference numbers.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python conservative_reanalysis/run_primary.py check
python conservative_reanalysis/run_primary.py all --output-dir ../curie_outputs --n-jobs 8
python conservative_reanalysis/verify_outputs.py --output-dir ../curie_outputs
```

On Windows use `.venv\Scripts\activate`. Use Python 3.12; exact scientific-library versions are pinned. `check` validates source data and dependencies without fitting models. A complete nested refit can take substantial CPU time. The `all` command fits all seven regressors before repeated-partition diagnostics, then direct classifiers and three paired process/phase models. Separate actions are `models`, `robustness`, `classification` and `process`; `robustness` requires `models` outputs. Existing output files are not automatically deleted.

The regression and process comparisons use 60 candidates; repeated partitions and classification use 30. Preprocessing and tuning remain inside grouped training loops. Changing software versions is a new reproduction and must not be silently substituted for the original environment. The family baseline uses outer-training targets only. Mean fold R² and pooled R² have different meanings; repeated-partition standard deviations are not confidence intervals. Model-family selection on the same dataset remains a stated limitation.

## Historical 141-record analysis

`historical_141/` retains the original unharmonized development inputs and executable regression, window-rule and stress-test methods. These analyses do not use the 72-record cohort. They retain their historical dependency ranges separately.

```bash
python historical_141/run_historical.py all --output-dir ../curie_historical_outputs --n-jobs 8
```

Actions: `grouped`, `windows`, `rules`, `challenges`, `canonical-counts`. The grouped action evaluates the original three descriptor families; rules reruns repeated nested interval selection; challenges reads the newly generated rule. Canonical configuration counts merge equivalent descriptor orders without altering predictions. No saved model result is needed to start the workflow. The record-random comparison and broader 79-record historical outputs are preserved in the earlier archive, rather than represented as new 72-record fits.

## File map

- `conservative_reanalysis/data/`: primary 72-record input, full 141-row adjudication ledger, broader 79-record sensitivity input and record-level process annotations.
- `conservative_reanalysis/scripts/`: nested regression, family diagnostics, direct classification and paired process/phase code.
- `historical_141/`: original development/challenge data and executable historical analyses.
- `references/`: DOI-bearing literature manifests and the manuscript bibliography.
- `LICENSE.md`: split code/data licensing and third-party-material exception.

The 79-record file is a frozen input for sensitivity/provenance, not a second independent external dataset. Original literature target values and audit decisions are preserved. The primary data retain 25/25/22 records in 3d-transition-metal, rare-earth-rich and transition-metal–metalloid families. No copyrighted source-article PDFs are redistributed.

## Archive status

Release v1.3.0 is identified by https://doi.org/10.5281/zenodo.23604881. The source ZIP contains data and reproducible code; Supplementary_Data.zip separately preserves the conservative numerical reference outputs, exact inputs and plotting sources. The previous v1.2.0 archive at https://doi.org/10.5281/zenodo.23102726 contains the broader-cohort analysis and does not contain the conservative refits. Git history and the earlier DOI preserve previous tracked results; the current branch contains source material only.

## Funding

Supported by the Scientific and Technological Research Council of Türkiye (TÜBİTAK), Career Development Program (3501), project 125F375.
