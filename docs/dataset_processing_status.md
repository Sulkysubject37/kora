# Dataset Processing Status

## Inventory Summary

This table lists datasets that have been successfully inventoried and are ready for standardized processing.

| Disease | Accession | Source | Samples | Matrix Type | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Parkinson's** | GSE269316 | Supp: count_matrix_galaxy.txt.gz | 48 | Raw Counts | Ready |
| **Parkinson's** | GSE294029 | Supp: Raw_counts.tsv.gz | 27 | Raw Counts | Ready |
| **Parkinson's** | GSE287574 | Supp: raw_counts.csv.gz | 24 | Raw Counts | Ready |
| **Parkinson's** | GSE75249 | SOFT | 33 | Intensity/Raw | Ready |
| **Parkinson's** | GSE290333 | SOFT | 38 | Normalized/Log | Ready |
| **Parkinson's** | GSE295831 | Supp: IPSCdopamin_Syn_raw.txt.gz | 7 | Raw Counts | Ready |
| **Parkinson's** | GSE282494 | Supp: feature_counts.txt.gz | 8 | Raw Counts | Ready |
| **Parkinson's** | GSE295832 | Supp: IPSC_dopamin_Syn_raw.txt.gz | 26 | Counts | Ready |
| **Parkinson's** | GSE268939 | Supp: all.genes.expression.annot.txt.gz | 21 | Intensity/Raw | Ready |
| **ALS** | GSE304550 | Supp: MN-samples-counts-processed.txt.gz | 18 | Counts | Ready |
| **ALS** | GSE309506 | Supp: Riluzole_treatment_raw_counts.txt.gz | 20 | Raw Counts | Ready |
| **ALS** | GSE301585 | Supp: MAID_samples_EP_cells_normalized_matrix.csv.gz | 2543 | Normalized/Log | Ready |
| **ALS** | GSE277085 | Supp: miRNA_counts.csv.gz | 15 | Raw Counts | Ready |
| **ALS** | GSE284339 | Supp: featureCounts.txt.gz | 26 | Counts | Ready |
| **ALS** | GSE304548 | Supp: iPSC-read-counts-processed.txt.gz | 8 | Counts | Ready |
| **ALS** | GSE252892 | Supp: D7-scr-vs-kd-gene-normalized-counts.csv.gz | 7 | Counts | Ready |
| **ALS** | GSE307054 | Supp: counts.csv.gz | 22 | Raw Counts | Ready |
| **FTD** | GSE79557 | SOFT | 30 | Normalized/Log | Ready |
| **FTD** | GSE230520 | SOFT | 18 | Normalized/Log | Ready |
| **FTD** | GSE158947 | Supp: SEMatrix_15477onWT.txt.gz | 24 | Intensity/Raw | Ready |
| **FTD** | GSE230447 | SOFT | 18 | Normalized/Log | Ready |
| **FTD** | GSE299341 | Supp: feature_counts.csv.gz | 52 | Counts | Ready |
| **FTD** | GSE230450 | Supp: bulk_counts_fin.csv.gz | 22 | Raw Counts | Ready |
| **FTD** | GSE215241 | Supp: uniquely_mapping-raw_counts.tsv.gz | 35 | Counts | Ready |
| **FTD** | GSE62935 | SOFT | 28 | Normalized/Log | Ready |
| **Alzheimer's** | GSE312139 | Supp: feature_counts_GEO.csv.gz | 48 | Raw Counts | Ready |
| **Alzheimer's** | GSE294848 | Supp: raw_count_all.csv.gz | 26 | Raw Counts | Ready |
| **Alzheimer's** | GSE311382 | Supp: RawCounts_iMG_IFNTreated_AllGroups.tsv.gz | 16 | Counts | Ready |
| **Alzheimer's** | GSE309664 | Supp: counts.txt.gz | 39 | Counts | Ready |
| **Alzheimer's** | GSE311578 | Supp: normalized_beta_values.csv.gz | 63 | Normalized/Log | Ready |
| **Alzheimer's** | GSE309036 | Supp: counts_all_mature.tsv.gz | 19 | Raw Counts | Ready |
| **Alzheimer's** | GSE313307 | Supp: normalised_all_samples.csv.gz | 202 | Normalized/Log | Ready |
| **Alzheimer's** | GSE310554 | Supp: raw_counts_matrix.tsv.gz | 396k? | Raw Counts | Large |
| **Alzheimer's** | GSE305625 | Supp: normalized_data.txt.gz | 326 | Intensity/Raw | Ready |
| **Huntington's** | GSE232647 | Supp: counts_cerulenin.csv.gz | 6 | Raw Counts | Ready |
| **Huntington's** | GSE232648 | Supp: raw_counts_sc.csv.gz | 43k | Raw Counts | Large (SC) |
| **Huntington's** | GSE273501 | Supp: RawCounts_Subfractions.txt.gz | 19 | Counts | Ready |
| **Huntington's** | GSE217469 | Supp: gene_counts_matrix.tsv.gz | 26 | Raw Counts | Ready |
| **Huntington's** | GSE284798 | Supp: CHDI_Cortical_Counts_Merged.csv.gz | 16 | Raw Counts | Ready |
| **Huntington's** | GSE283225 | Supp: filtered.norm.meth.csv.gz | 40 | Intensity/Raw | Ready |

## Next Actions
1.  **Normalization:** Apply `Log2(TPM + 1)` or `Log2(CPM + 1)` to datasets marked as "Raw Counts" or "Counts".
2.  **Filtering:** Exclude single-cell datasets (e.g., GSE310554, GSE232648 seems suspiciously large) if the pipeline is for bulk.
3.  **Spike Encoding:** Proceed to spike encoding for all "Ready" datasets.
