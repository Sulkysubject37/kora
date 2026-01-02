# Data Processing Methodology & Issues

## Overview
This document previously tracked issues during dataset ingestion and processing. **All issues described herein have been addressed and resolved.**

## Historical Issues & Resolutions

### 1. Microarray (Legacy)
- **Source:** GEO SOFT Files (`_family.soft.gz`).
- **Method:** `GEOparse` extracts the `VALUE` column from the sample table.
- **Resolution:** This pipeline proved robust and functional.

### 2. RNA-Seq (HTS)
- **Source:** Supplementary Files (`_counts.txt.gz`, `_tpm.txt`, `_matrix.txt`).
- **Original Issue:** SOFT files for HTS (e.g., Illumina) often contained only metadata, not the expression matrix, leading to `KeyError: 'ID_REF'` during parsing.
- **Resolution:** The `scripts/download_cohorts.py` and `scripts/harmonize_genes.py` scripts were enhanced to:
    1.  Automatically identify datasets that fail SOFT parsing for expression data.
    2.  Prioritize and correctly parse expression matrices from supplementary files (e.g., `*count*`, `*tpm*`, `*matrix*` files).
    3.  Standardize data orientation (Samples x Genes).

## Previously Failed Datasets (Now Resolved)

The datasets previously listed as failing due to `KeyError: 'ID_REF'` or file size limits have now been successfully processed by the updated pipeline scripts.

## Current Status

The data processing pipeline is robust, handling both Microarray (SOFT) and RNA-Seq (supplementary files) data types, including large datasets and various gene identifier formats. All known issues have been mitigated.