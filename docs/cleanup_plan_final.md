# Final Cleanup Plan

The following scripts are identified as one-off utilities or deprecated tools and will be removed to prepare the repository for release.

## Scripts to Remove

1.  `scripts/inspect_gpl.py`
    *   **Reason:** Diagnostic tool for platform debugging. Not part of the core pipeline.

2.  `scripts/organize_processed.py`
    *   **Reason:** Migration script for directory restructuring. State is now consistent.

3.  `scripts/download_synapse_datasets.py`
    *   **Reason:** Redundant if not used (we focus on GEO).

4.  `scripts/debug_training.py`
    *   **Reason:** Temporary debugging script.

## Justification

Removing these reduces clutter and clarify the entry points for the KORA pipeline (Process -> Encode -> Train -> Export -> Inference).
