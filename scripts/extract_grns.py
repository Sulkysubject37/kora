import pandas as pd
import numpy as np
import logging
from pathlib import Path
import json
import os
import gc

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_grn(accession):
    res_dir = Path(f"results/{accession}")
    weights_path = res_dir / "weights" / "trained_weights.npy"
    genes_path = res_dir / "weights" / "gene_names.json"
    grn_dir = res_dir / "grn"
    
    if not weights_path.exists():
        return None

    logger.info(f"Extracting GRN for {accession}...")
    
    try:
        # 1. Load weights and gene names
        W = np.load(weights_path)
        with open(genes_path, "r") as f:
            gene_names = json.load(f)
            
        # 2. Thresholding
        # Standardize weights or use simple threshold
        # Causal STDP weights: rows = pre (source), cols = post (target)
        # W[i, j] is strength of i -> j
        
        abs_W = np.abs(W)
        mean_w = np.mean(abs_W)
        std_w = np.std(abs_W)
        threshold = mean_w + 2 * std_w # Conservative
        
        # 3. Create Adjacency
        adj_mask = abs_W > threshold
        # Preserve sign and magnitude for the adjacency matrix
        adj_matrix = np.where(adj_mask, W, 0)
        
        # 4. Save Adjacency CSV
        adj_df = pd.DataFrame(adj_matrix, index=gene_names, columns=gene_names)
        grn_dir.mkdir(parents=True, exist_ok=True)
        adj_df.to_csv(grn_dir / "adjacency.csv")
        
        # 5. Save Edge List TSV
        sources, targets = np.where(adj_mask)
        edges = []
        for s, t in zip(sources, targets):
            edges.append({
                "source": gene_names[s],
                "target": gene_names[t],
                "weight": float(W[s, t]),
                "type": "activation" if W[s, t] > 0 else "repression"
            })
            
        edges_df = pd.DataFrame(edges)
        edges_df.to_csv(grn_dir / "edges.tsv", sep="\t", index=False)
        
        logger.info(f"Saved GRN for {accession}: {len(edges)} edges")
        return len(edges)
        
    except Exception as e:
        logger.error(f"Failed to extract GRN for {accession}: {e}")
        return None
    finally:
        gc.collect()

def main():
    registry_path = "data/cohort_index.csv"
    if not os.path.exists(registry_path):
        return
        
    df = pd.read_csv(registry_path)
    summary = []
    
    for acc in df["accession"]:
        n_edges = extract_grn(acc)
        if n_edges is not None:
            summary.append({"accession": acc, "n_edges": n_edges})
            
    summary_df = pd.DataFrame(summary)
    print("\n=== GRN Extraction Summary ===\n")
    if not summary_df.empty:
        print(summary_df.to_string())
    else:
        print("No GRNs extracted.")

if __name__ == "__main__":
    main()
