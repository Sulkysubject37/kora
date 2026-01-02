# KORA (Kinetic Ordered Regulatory Analysis)

## Overview

KORA is a novel computational biology pipeline designed for inferring Gene Regulatory Networks (GRNs) from transcriptomic data, with a specific focus on neurodegenerative disorders. Leveraging principles from neuroscience and machine learning, KORA redefines GRN inference as a temporal causal learning problem. It utilizes Spiking Neural Networks (SNNs) trained with generalized Spike-Timing Dependent Plasticity (STDP) to capture dynamic, causal relationships between genes.

The pipeline spans data acquisition and preprocessing, spike encoding, SNN training, GRN extraction, and high-performance inference via CoreML on Apple's Neural Processing Unit (NPU). Comprehensive documentation, automated testing, and dynamic visualizations ensure reproducibility and interpretability.

## Core Features

*   **Causal GRN Inference**: Employs generalized STDP in SNNs to infer directed gene regulatory links based on temporal correlations.
*   **Disease-Specific Cohorts**: Processes diverse transcriptomic datasets from public repositories (e.g., GEO) across various neurodegenerative diseases.
*   **Modular Pipeline**: Structured Python scripts for data handling, SNN training, and GRN extraction.
*   **High-Performance Inference**: Exported GRN operators as inference-only CoreML models for accelerated execution on Apple Silicon (NPU/CPU).
*   **Swift Integration**: Native Swift application for loading CoreML models, performing batch inference, and benchmarking performance.
*   **Comprehensive Documentation**: Detailed `README.md` files within each directory explain structure, manifest, and usage.
*   **Dynamic Visualizations**: Tools for generating interactive GRN graphs, weight distribution plots, and performance benchmarks.

## Pipeline Overview

1.  **Data Processing**: Clean and normalize raw transcriptomic data.
2.  **Spike Encoding**: Convert gene expression into spike trains.
3.  **SNN Training**: Train cohort-specific SNNs using generalized STDP.
4.  **GRN Extraction**: Extract directed GRNs from learned synaptic weights.
5.  **CoreML Export**: Distill GRN operators into inference-only CoreML models.
6.  **Swift Inference**: Perform high-performance inference on Apple devices (CPU/NPU).
7.  **Analysis & Visualization**: Generate insights and dynamic plots.

## Project Status

**Version:** `v1.0.1` (Frozen for initial paper draft / release candidate)

All core pipeline components are implemented, tested, and documented. The system is capable of processing neurodegenerative cohorts, inferring GRNs, and performing high-speed inference.

## Getting Started

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/Sulkysubject37/kora.git
    cd kora
    ```
2.  **Setup Environment**:
    ```bash
    python3 -m venv kora_env
    source kora_env/bin/activate
    pip install -r requirements.txt
    ```
3.  **Run Pipeline**: Follow the instructions in the `scripts/README.md` to execute the data processing, encoding, training, and GRN extraction steps.
4.  **CoreML Export & Swift Inference**: Refer to `models/README.md` and `swift/README.md` for details on exporting CoreML models and running the Swift inference engine.

## Documentation

Each major directory (`configs/`, `data/`, `docs/`, `models/`, `results/`, `scripts/`, `src/`, `swift/`, `tests/`) contains a `README.md` file detailing its purpose, contents, and usage.

## License

This project is licensed under the MIT License.

## Citation

If you use this project in your research, please cite:
MD.Arshad
