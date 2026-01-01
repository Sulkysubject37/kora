import logging
import pickle
import numpy as np
from pathlib import Path
from multiprocessing import Pool, cpu_count
import argparse
import sys

# Ensure src is in path
sys.path.append(".")

from src.snn.simulation import Trainer
from src.grn.infer_grn import GRNExtractor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def train_cohort(cohort_path: Path):
    """
    Worker function to train one cohort.
    """
    try:
        spikes_path = cohort_path / "spikes.pkl"
        if not spikes_path.exists():
            return None
            
        logger.info(f"Training on {cohort_path.name}...")
        
        with open(spikes_path, "rb") as f:
            spikes = pickle.load(f) # List[np.ndarray]
            
        n_genes = len(spikes)
        
        # Initialize Trainer
        trainer = Trainer(n_genes=n_genes)
        
        # Calc duration
        # We need the max spike time to know duration roughly, or pass it?
        # The encoder saved spikes.
        # Let's infer duration from max spike + epsilon
        max_time = 0
        for s in spikes:
            if len(s) > 0:
                max_time = max(max_time, s.max())
                
        duration = max_time + 100.0
        
        # Train
        # Trainer.train_cohort expects list of spikes
        weights = trainer.train_cohort(spikes, duration_ms=duration, dt=1.0)
        
        # Save weights
        np.save(cohort_path / "trained_weights.npy", weights)
        
        # Extract GRN
        extractor = GRNExtractor(weight_threshold=0.1)
        grn = extractor.extract(weights)
        
        # Save GRN adj
        import networkx as nx
        # nx.write_adjacency_matrix is deprecated/removed in 3.0?
        # Use to_numpy_array
        adj = nx.to_numpy_array(grn)
        np.savetxt(cohort_path / "inferred_grn.txt", adj)
        
        logger.info(f"Completed {cohort_path.name}")
        return cohort_path.name
        
    except Exception as e:
        logger.error(f"Failed {cohort_path.name}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=max(1, cpu_count() - 1))
    args = parser.parse_args()
    
    processed_dir = Path("data/processed")
    cohorts = []
    
    # Collect cohorts
    # Real
    for p in processed_dir.iterdir():
        if p.name == "synthetic": continue
        if p.is_dir() and (p / "spikes.pkl").exists():
            cohorts.append(p)
            
    # Synthetic
    synth_dir = processed_dir / "synthetic"
    if synth_dir.exists():
        for p in synth_dir.iterdir():
            if p.is_dir() and (p / "spikes.pkl").exists():
                cohorts.append(p)
                
    if not cohorts:
        logger.warning("No encoded cohorts found.")
        return

    logger.info(f"Starting training for {len(cohorts)} cohorts with {args.workers} workers...")
    
    with Pool(args.workers) as pool:
        results = pool.map(train_cohort, cohorts)
        
    logger.info("Training batch complete.")

if __name__ == "__main__":
    main()
