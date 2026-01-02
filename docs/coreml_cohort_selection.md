# Cohort Selection for CoreML Inference

The following 10 datasets have been selected as representative cohorts for the Swift/CoreML inference phase. Selection criteria included:
*   Bulk transcriptomics only.
*   Sample size > 15 (except where limited options existed, e.g., HD).
*   Disease diversity (2 cohorts per major neurodegenerative indication).
*   Successful processing status (Harmonized + Normalized + Spikes encoded).

| Accession | Disease | N Samples | Matrix Type | Justification |
| :--- | :--- | :--- | :--- | :--- |
| **GSE269316** | Parkinsons Disease | 48 | Raw Counts | Robust sample size; modern RNA-seq. |
| **GSE290333** | Parkinsons Disease | 38 | Normalized | Good size; processed array data. |
| **GSE307054** | Amyotrophic Lateral Sclerosis | 22 | Raw Counts | Recent dataset; reasonable size for ALS. |
| **GSE284339** | Amyotrophic Lateral Sclerosis | 26 | Counts | Consistent size; feature counts available. |
| **GSE79557** | Frontotemporal Dementia | 30 | Normalized | Established dataset; good baseline. |
| **GSE215241** | Frontotemporal Dementia | 35 | Counts | Uniquely mapped counts; high quality. |
| **GSE312139** | Alzheimers Disease | 48 | Raw Counts | Large recent cohort; ideal for AD representation. |
| **GSE309664** | Alzheimers Disease | 39 | Counts | Good size; standard count data. |
| **GSE217469** | Huntingtons Disease | 26 | Raw Counts | Best available size for HD in this collection. |
| **GSE273501** | Huntingtons Disease | 19 | Counts | Acceptable size; complements GSE217469. |

**Exclusions:**
*   **GSE301585:** Single-cell (too large/complex for this bulk pipeline).
*   **GSE232647:** N=6 (Too small).
*   **GSE252892:** N=7 (Too small).
