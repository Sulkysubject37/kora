import subprocess
import json
import os
from pathlib import Path

COHORTS = [
    "GSE269316", "GSE290333", 
    "GSE307054", "GSE284339",
    "GSE79557",  "GSE215241",
    "GSE312139", "GSE309664",
    "GSE217469", "GSE273501"
]

SWIFT_EXEC = "swift/.build/release/KORAInference"

def run_benchmark():
    for acc in COHORTS:
        print(f"Benchmarking {acc}...")
        
        # 1. Get N Genes
        meta_path = Path(f"models/coreml/{acc}/metadata.json")
        if not meta_path.exists():
            print(f"Skipping {acc}: No metadata.")
            continue
            
        with open(meta_path, "r") as f:
            meta = json.load(f)
            n_genes = meta["n_genes"]
            
        model_path = f"models/coreml/{acc}/grn_operator.mlmodel"
        
        # 2. Run Swift
        cmd = [SWIFT_EXEC, model_path, str(n_genes), "1000"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            output = result.stdout
            
            # Save Log
            with open(f"results/benchmarks/benchmark_{acc}.log", "w") as f:
                f.write(output)
                
            # Extract CSV
            if "CSV_RESULT:" in output:
                csv_content = output.split("CSV_RESULT:\n")[1].strip()
                with open(f"results/benchmarks/benchmark_{acc}.csv", "w") as f:
                    f.write(csv_content)
                print(f"Saved results for {acc}")
            else:
                print(f"No CSV output for {acc}")
                
        except subprocess.CalledProcessError as e:
            print(f"Error running {acc}: {e}")
            print(e.stderr)

if __name__ == "__main__":
    run_benchmark()
