# Cleanup Plan

The following scripts and files are identified as redundant or obsolete and will be removed to maintain codebase hygiene and reproducibility.

## Scripts to Remove

1.  `scripts/process_expression.py`
    *   **Reason:** Superseded by `scripts/harmonize_genes.py` and `scripts/normalize_cohorts.py`. The new pipeline explicitly separates harmonization and normalization steps.

2.  `scripts/encode_spikes.py`
    *   **Reason:** Redundant with `scripts/encode_cohorts.py`. `encode_cohorts.py` contains more robust logic for normalization and batch processing.

3.  `scripts/train_kora_snn.py`
    *   **Reason:** Superseded by `scripts/train_cohort_snn.py`, which implements the correct cohort-specific isolation logic and Generalized STDP.

## Justification

Removing these files eliminates ambiguity about which scripts to run for the core pipeline steps (Processing, Encoding, Training).
