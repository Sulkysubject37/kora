# Models Directory

This directory stores various model artifacts generated during the KORA pipeline, including trained Python models and exported CoreML models for inference.

## Directory Structure

| Directory | Description |
| :--- | :--- |
| `coreml/` | Contains the exported CoreML models for selected cohorts. Each cohort has its own subdirectory (e.g., `coreml/GSE12345/`) containing the `.mlmodel` file, metadata, and Python validation logs. |
| `snn/` | Placeholder for Python-based SNN model definitions and potentially trained Python models. |
| `stdp/` | Placeholder for Python-based STDP rule implementations. |
| `distilled/` | Placeholder for any distilled or simplified model representations. |

## Manifest

*   **`coreml/{accession}/grn_operator.mlmodel`**: The CoreML model representing the distilled, rate-based GRN operator for a specific cohort.
*   **`coreml/{accession}/metadata.json`**: Metadata about the CoreML model, including number of genes and validation results.
*   **`coreml/{accession}/python_validation.txt`**: Logs from the Python validation step, comparing Python and CoreML inference outputs.

## Usage

CoreML models in this directory are loaded by the Swift inference engine (`swift/Sources/KORAInference/`) for high-performance CPU and NPU inference.

## Notes

*   **Git Ignore:** `.mlmodel` files are binary and can be large. They are intentionally ignored by git to avoid repository bloat.
