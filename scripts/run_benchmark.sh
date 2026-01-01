#!/bin/bash
# Runs the inference benchmark using the KORA environment

# Ensure script fails on error
set -e

# Path to python environment
PYTHON_EXEC="kora_env/bin/python"

if [ ! -f "$PYTHON_EXEC" ]; then
    echo "Error: Virtual environment not found at kora_env/"
    exit 1
fi

echo "Running KORA Inference Benchmark..."
export PYTHONPATH=.
$PYTHON_EXEC scripts/run_inference_benchmark.py
echo "Benchmark Complete."
