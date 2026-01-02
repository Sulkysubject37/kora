import pandas as pd
import matplotlib.pyplot as pd_plt
import argparse
from pathlib import Path
import os

def analyze(csv_path):
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    print("Benchmark Results:")
    print(df)
    
    # Calculate Speedup
    cpu_row = df[df['device'] == 'cpu']
    npu_row = df[df['device'] == 'npu']
    
    if not cpu_row.empty and not npu_row.empty:
        cpu_t = cpu_row.iloc[0]['throughput']
        npu_t = npu_row.iloc[0]['throughput']
        speedup = npu_t / cpu_t
        print(f"\nNPU Speedup: {speedup:.2f}x")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", help="Path to benchmark CSV")
    args = parser.parse_args()
    analyze(args.csv_path)

