# Tests Directory

This directory contains unit tests for various components of the KORA pipeline. These tests ensure the correctness and reliability of critical functionalities, from spike encoding to GRN extraction.

## Manifest

| File | Description |
| :--- | :--- |
| `test_encoding.py` | Unit tests for the `SpikeEncoder` module, verifying correct conversion of expression data to spike trains. |
| `test_grn.py` | Unit tests for the GRN extraction logic, including thresholding and matrix operations. |
| `test_stdp.py` | Unit tests for the Spike-Timing Dependent Plasticity (STDP) rules, ensuring accurate weight updates based on spike timings. |

## Usage

Tests are implemented using the `pytest` framework. To run all tests, navigate to the project root and execute:

```bash
pytest tests/
```

To run a specific test file:

```bash
pytest tests/test_encoding.py
```

## Importance

Comprehensive testing is crucial for a computational biology pipeline to ensure reproducibility, data integrity, and the scientific validity of the results. These tests act as a regression suite, preventing unintended side effects from new code changes.
