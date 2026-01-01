import pandas as pd
import numpy as np
import logging
from pathlib import Path
from src.grn.infer_grn import GRNExtractor
import networkx as nx

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def evaluate_cohort(cohort_dir: Path):
    res = {
        "cohort_id": cohort_dir.name,
        "type": "Real",
        "precision": np.nan,
        "recall": np.nan,
        "f1": np.nan,
        "edges_inferred": 0
    }
    
    inferred_path = cohort_dir / "inferred_grn.txt"
    if not inferred_path.exists():
        return None
        
    inferred_adj = np.loadtxt(inferred_path)
    res["edges_inferred"] = np.sum(inferred_adj != 0)
    
    # Check for Ground Truth
    gt_path = cohort_dir / "ground_truth_adj.txt"
    if gt_path.exists():
        res["type"] = "Synthetic"
        # We need a graph object to use the helper from Task 6?
        # Actually infer_grn.py has compare_with_ground_truth.
        # But that takes a Graph object and a PATH to truth.
        
        # Reconstruct graph from adj to reuse existing code or just calc here.
        # Let's calc here, simpler.
        
        gt_adj = np.loadtxt(gt_path)
        
        # Ensure shapes match (sometimes synthetic generator saves full matrix, inference might be same size)
        if inferred_adj.shape != gt_adj.shape:
            logger.warning(f"Shape mismatch for {cohort_dir.name}")
            return res
            
        flat_pred = (inferred_adj != 0).flatten()
        flat_true = (gt_adj != 0).flatten()
        
        tp = np.sum(flat_true & flat_pred)
        fp = np.sum((~flat_true) & flat_pred)
        fn = np.sum(flat_true & (~flat_pred))
        
        res["precision"] = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        res["recall"] = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        res["f1"] = 2 * res["precision"] * res["recall"] / (res["precision"] + res["recall"]) if (res["precision"] + res["recall"]) > 0 else 0.0
        
    return res

def main():
    processed_dir = Path("data/processed")
    results = []
    
    # Synthetic
    synth_dir = processed_dir / "synthetic"
    if synth_dir.exists():
        for p in synth_dir.iterdir():
            if p.is_dir():
                r = evaluate_cohort(p)
                if r: results.append(r)
                
    # Real (no GT usually)
    for p in processed_dir.iterdir():
        if p.name == "synthetic": continue
        if p.is_dir():
            r = evaluate_cohort(p)
            if r: results.append(r)
            
    if not results:
        logger.warning("No results found.")
        return
        
    df = pd.DataFrame(results)
    out_dir = Path("results/tables")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "training_summary.csv"
    
    df.to_csv(out_path, index=False)
    logger.info(f"Saved summary to {out_path}")
    print(df)

if __name__ == "__main__":
    main()
