# Data Directory

This directory hosts all data artifacts for the KORA project, organized by processing stage.

## Directory Structure

| Directory | Description |
| :--- | :--- |
| **`raw/`** | Raw downloads from GEO/Synapse. Organized by `Disease/Accession`. Files are typically `.txt.gz` or `.csv.gz`. |
| **`processed/`** | Cleaned and normalized data. Organized by `Disease/Accession`. <br> Contains: <br> - `expression.csv`: Raw expression matrix. <br> - `expression_genes.csv`: Harmonized gene symbols. <br> - `expression_log_normalized.csv`: Log2(CPM+1) normalized data. |
| **`spikes/`** | Rate-encoded spike trains for SNN training. Organized by `Accession`. <br> Contains: `spikes.pkl` (Pickled numpy arrays of spike times). |
| `external/` | External reference data (e.g., Gene Ontology, PPI networks). |
| `interim/` | Temporary processing artifacts. |

## Key Files

*   **`cohort_index.csv`**: The master registry of all datasets, their disease labels, sample counts, and processing status. Used by all pipeline scripts to discover data.

## Notes

*   **Data Integrity:** Do not manually edit files in `processed/` or `spikes/`. Use the pipeline scripts (`scripts/harmonize_genes.py`, `scripts/encode_cohorts.py`) to regenerate them.
*   **Git Ignore:** Large data files are ignored by git. Only metadata and small configuration files are tracked.
