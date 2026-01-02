# Source Code Directory (`src/`)

This directory contains the core Python source code that implements the KORA (Kinetic Ordered Regulatory Analysis) pipeline's functionalities. It is structured into modules corresponding to different logical components of the system.

## Module Structure

| Module | Description |
| :--- | :--- |
| `data/` | Utilities for data handling, generation, and basic transformations. |
| `encoding/` | Implementation of spike encoding strategies to convert gene expression into spike trains. |
| `evaluation/` | Tools for evaluating model performance, GRN quality, and biological relevance. |
| `grn/` | Core logic for extracting Gene Regulatory Networks from trained SNNs. |
| `snn/` | Implementation of the Spiking Neural Network (SNN) architecture and simulation mechanisms. |
| `stdp/` | Contains various Spike-Timing Dependent Plasticity (STDP) learning rules. |
| `utils/` | General utility functions, including gene mapping, I/O operations, logging, and parallel processing. |

## Key Files & Concepts

*   **`src/encoding/spike_encoding.py`**: Defines the `SpikeEncoder` class responsible for converting continuous gene expression data into discrete spike events.
*   **`src/snn/network.py`**: Implements the `Network` class, which defines the SNN's structure (neurons, synapses) and forward dynamics.
*   **`src/snn/simulation.py`**: The `Trainer` class orchestrates the SNN simulation and applies STDP learning rules.
*   **`src/stdp/generalized_stdp.py`**: Contains the `CausalSTDP` implementation, the primary learning rule for adjusting synaptic weights.
*   **`src/utils/gene_mapping.py`**: Critical for harmonizing gene identifiers across diverse datasets.
*   **`src/grn/infer_grn.py`**: Logic for thresholding and interpreting trained SNN weights as regulatory links in a GRN.

## Usage

Modules within `src/` are imported and utilized by the scripts located in the top-level `scripts/` directory.

## Notes

*   **Modularity**: The codebase emphasizes modularity to allow for easy interchangeability of components (e.g., different STDP rules, encoding strategies).
*   **Performance**: Core computations are designed for efficiency, leveraging NumPy for numerical operations.
