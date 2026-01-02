# Scripts Directory

This directory contains Python scripts that implement the various stages of the KORA computational biology pipeline, from data acquisition and preprocessing to model training, GRN extraction, and analysis.

## Pipeline Stages & Core Scripts

| Category | Script Name | Description |
| :--- | :--- | :--- |
| **Data Acquisition** | `download_cohorts.py` | Fetches raw transcriptomic data from GEO for inventoried cohorts. |
| | `discover_datasets.py` | Discovers new GEO datasets for neurodegenerative disorders. |
| | `inventory_datasets.py` | Catalogs downloaded datasets and updates `cohort_index.csv`. |
| | `register_cohorts.py` | Registers newly discovered datasets into the `cohort_index.csv`. |
| **Data Processing** | `harmonize_genes.py` | Harmonizes gene identifiers (e.g., probes, Ensembl, Entrez) to HGNC symbols. |
| | `normalize_cohorts.py` | Applies log-normalization (Log2(CPM+1) or Log2(Intensity+1)) to expression data. |
| **Spike Encoding** | `encode_cohorts.py` | Converts normalized gene expression matrices into spike trains for SNNs. |
| **SNN Training** | `train_cohort_snn.py` | Trains cohort-specific Spiking Neural Networks using generalized STDP. |
| **GRN Extraction** | `extract_grns.py` | Extracts Gene Regulatory Networks (adjacency matrices and edge lists) from trained SNN weights. |
| **Analysis & Viz** | `analyze_benchmarks.py` | Python script to load and analyze Swift benchmark results. |
| | `run_full_benchmark.py` | Automates execution of Swift benchmarks for all selected CoreML models. |
| | `visualize_results.py` | Generates static plots (e.g., benchmark performance, weight distributions). |
| | `visualize_dynamic.py` | Generates dynamic and interactive visualizations (e.g., interactive GRNs, animation). |

## Auxiliary Scripts

| Script Name | Description |
| :--- | :--- |
| `discover_synapse.py` | Utility to discover datasets from Synapse (currently not integrated into main pipeline). |
| `extract_archives.py` | Extracts compressed data archives (`.tar.gz`, `.zip`). |
| `generate_synthetic.py` | Generates synthetic datasets for testing and development. |
| `validate_datasets.py` | Validates the integrity and format of processed datasets. |
| `aggregate_results.py` | Placeholder for aggregating results across multiple cohorts (not yet fully implemented). |
| `run_benchmark.sh` | Shell script example for running Python benchmarks. |
| `run_covid_experiment.sh` | Shell script for an older COVID-19 experiment. |
| `run_neurodegeneration_experiment.sh` | Shell script for older neurodegeneration experiments. |
| `run_inference_benchmark.py` | Older script for Python-only inference benchmarking. |
| `visualize_grn.py` | (Deprecated/Replaced by `visualize_results.py` or `visualize_dynamic.py`). |

## Usage

Scripts are typically executed from the project root using `python3 scripts/script_name.py`. Ensure the `kora_env` virtual environment is activated.
