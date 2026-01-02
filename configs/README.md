# Configuration Files

This directory contains YAML configuration files that control the behavior of the KORA pipeline, including data loading, SNN training parameters, and STDP rules.

## Manifest

| File | Description |
| :--- | :--- |
| `kora_config.yaml` | **Primary Configuration.** Defines the default parameters for the neurodegenerative pipeline, including STDP learning rates, time constants, and simulation time steps. |
| `default.yaml` | Base template for pipeline defaults. |
| `covid.yaml` | Legacy configuration for the COVID-19 transcriptomics experiment (Phase 1). |
| `neurodegeneration.yaml` | Disease-specific overrides and cohort definitions for the neurodegeneration study. |

## Usage

Load configurations in Python scripts using `yaml`:

```python
import yaml
from pathlib import Path

def load_config(path="configs/kora_config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)
```

## Key Parameters (kora_config.yaml)

*   **`training`**:
    *   `dt`: Simulation time step (ms).
    *   `duration`: Default simulation duration (ms).
    *   **`stdp`**:
        *   `learning_rate`: Maximum weight change per update.
        *   `tau_plus` / `tau_minus`: Time constants for causal/acausal windows.
        *   `w_max`: Maximum synaptic weight.
