import logging
from pathlib import Path
import numpy as np
import pandas as pd
from src.data.generator import SyntheticGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Define synthetic cohorts to generate
    cohorts = [
        {"id": "SYNTH_AD_001", "n_genes": 100, "n_cohorts": 50, "n_timepoints": 50},
        {"id": "SYNTH_PD_001", "n_genes": 100, "n_cohorts": 50, "n_timepoints": 50},
        {"id": "SYNTH_ALS_001", "n_genes": 100, "n_cohorts": 50, "n_timepoints": 50},
    ]
    
    processed_dir = Path("data/processed/synthetic")
    
    for c in cohorts:
        cid = c["id"]
        logger.info(f"Generating synthetic cohort {cid}...")
        
        out_dir = processed_dir / cid
        out_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize generator
        gen = SyntheticGenerator(
            n_genes=c["n_genes"], 
            n_timepoints=c["n_timepoints"], 
            n_cohorts=c["n_cohorts"],
            seed=sum(ord(char) for char in cid) # Deterministic seed based on ID
        )
        
        gen.generate_ground_truth_grn()
        data = gen.simulate_dynamics()
        
        # Save standard expression.csv format (Samples x Genes)
        # The generator produces (n_cohorts, n_timepoints, n_genes)
        # We need to flatten or decide how to represent "Samples".
        # For KORA SNN, we usually train on time-series.
        # "expression.csv" usually implies a static matrix for standard analysis, 
        # BUT KORA is Kinetic.
        # The processing script produced (Samples x Genes).
        # If the input is static (real post-mortem data), we treat samples as pseudo-time or distinct snapshots?
        # KORA's SNN expects TIME SERIES.
        # Real data (GEO) is usually static snapshots of many patients.
        # We need to pseudotime order them or treat them as independent samples fed sequentially?
        
        # Strategy for Real Data (implied):
        # If data is cross-sectional (ADNI), we order by disease stage -> Pseudo-time.
        # If we just have a bag of samples, we might train on them as a sequence (batch).
        
        # For synthetic, we HAVE time.
        # Let's save the first cohort's time series as the "expression.csv" for simple testing,
        # OR save all cohorts concatenated.
        # Let's save a 2D matrix: (n_cohorts * n_timepoints) x n_genes? 
        # Or better: just save the 3D numpy array which KORA prefers, but the task says "expression.csv".
        
        # To align with Task 4 (which outputs CSV), I will output a CSV.
        # Let's flatten: Index = Cohort_Timepoint
        
        reshaped = data.reshape(-1, c["n_genes"])
        index = [f"C{i}_T{t}" for i in range(c["n_cohorts"]) for t in range(c["n_timepoints"])]
        df = pd.DataFrame(reshaped, index=index, columns=[f"Gene_{g}" for g in range(c["n_genes"])])
        
        df.to_csv(out_dir / "expression.csv")
        
        # Also save ground truth for validation
        gen.save_data(out_dir, data) # This saves .npy and adj matrix
        
        logger.info(f"Generated {cid}")

if __name__ == "__main__":
    main()
