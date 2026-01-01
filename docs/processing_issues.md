# Data Processing Methodology & Issues

## Overview
This document tracks the status of dataset ingestion, specifically addressing the differences between Microarray (SOFT-native) and RNA-Seq (Supplementary-native) pipelines.

## Processing Pipelines

### 1. Microarray (Legacy)
- **Source:** GEO SOFT Files (`_family.soft.gz`).
- **Method:** `GEOparse` extracts the `VALUE` column from the sample table.
- **Status:** Functional.
- **Successes:** GSE75249, GSE40378, GSE290333, etc.

### 2. RNA-Seq (HTS)
- **Source:** Supplementary Files (`_counts.txt.gz`, `_tpm.txt`, `_matrix.txt`).
- **Issue:** SOFT files for HTS (e.g., Illumina) often contain only metadata, not the expression matrix. Attempting to parse `ID_REF` fails.
- **Methodology (New):**
    1. Identify datasets that fail SOFT parsing.
    2. Query GEO for "Supplementary Files".
    3. Prioritize files matching `*count*`, `*tpm*`, `*fpkm*`, `*matrix*`.
    4. Download and parse these custom tables.
    5. Standardize to Gene x Sample format.

## Failed Datasets & Analysis

| Accession | Error | Cause | Action |
| :--- | :--- | :--- | :--- |
| GSE268609 | KeyError: 'ID_REF' | HTS Data (Metadata only in SOFT) | Fetch Supp Files |
| GSE232649 | KeyError: 'ID_REF' | HTS Data | Fetch Supp Files |
| GSE315111 | KeyError: 'ID_REF' | HTS Data | Fetch Supp Files |
| GSE230519 | KeyError: 'ID_REF' | HTS Data | Fetch Supp Files |
| GSE53740 | File Size Limit | >2GB SOFT file (uncompressed >10GB) | Use streaming / Supp Files |

## Next Steps
1.  **Refactor `download_cohorts.py`**: Add logic to fetch supplementary files for datasets identified as "Expression profiling by high throughput sequencing".
2.  **Refactor `process_expression.py`**: Add a handler for `_counts.txt` / `_matrix.txt` parsing.
