# Swift Inference Layer

This directory contains the Swift project for loading and running CoreML-exported GRN operators. It provides a high-performance inference pipeline for benchmarking and integration into potential downstream applications.

## Directory Structure

| Directory | Description |
| :--- | :--- |
| `.build/` | Swift build artifacts (ignored by Git). |
| `.swiftpm/` | Swift Package Manager metadata (ignored by Git). |
| `Sources/KORAInference/` | Contains the Swift source files for the KORA inference application. |
| `Package.swift` | The Swift Package Manager manifest file, defining the project's dependencies and targets. |

## Source Files (`Sources/KORAInference/`)

| File | Description |
| :--- | :--- |
| `main.swift` | The entry point for the executable. Handles command-line arguments and orchestrates the inference and benchmarking process. |
| `ModelLoader.swift` | Utility class for loading compiled CoreML models (`.mlmodel`) into `MLModel` instances. |
| `InferenceRunner.swift` | Encapsulates the logic for performing a single inference pass using an `MLModel`, handling input/output conversions. |
| `BatchExecutor.swift` | Manages the execution of multiple inference passes (batches) and measures performance metrics for benchmarking. |
| `ResultWriter.swift` | Placeholder for writing inference results and benchmark summaries to file (currently outputs to `stdout` for capture). |

## Usage

1.  **Build**: Navigate to the `swift/` directory and build the project:
    ```bash
    swift build -c release
    ```
    This will create an executable at `.build/release/KORAInference`.

2.  **Run Benchmark**: Execute the compiled tool, providing the path to a CoreML model, the number of genes (`n_genes`), and an optional batch size.
    ```bash
    ./.build/release/KORAInference <path_to_mlmodel> <n_genes> [batch_size] > output.log
    ```
    Example:
    ```bash
    ./.build/release/KORAInference ../models/coreml/GSE269316/grn_operator.mlmodel 5000 1000
    ```
    The `scripts/run_full_benchmark.py` automates this process for all selected cohorts.

## Key Features

*   **CoreML Integration**: Leverages Apple's CoreML framework for optimized inference on Apple Silicon (NPU) and CPU.
*   **Performance Benchmarking**: Measures latency and throughput for different compute units.
*   **Modular Design**: Clear separation of concerns for model loading, inference execution, and batch processing.
