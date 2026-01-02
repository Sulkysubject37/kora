import pandas as pd
import numpy as np
import logging
from pathlib import Path
import pickle
import sys
import os
import gc
import json
import yaml

# Ensure src is importable
sys.path.append(os.path.abspath("."))

from src.snn.simulation import Trainer
from src.stdp.generalized_stdp import CausalSTDP

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MAX_NEURONS = 5000 

def load_config():
    config_path = Path("configs/kora_config.yaml")
    if config_path.exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}

def train_cohort(accession, disease, config):
    if accession == "GSE301585" or accession == "GSE311578":
        logger.info(f"Skipping {accession}: Blacklisted (Too large/missing spikes).")
        return

    # Path finding
    processed_root = Path("data/processed")
    disease_safe = disease.replace(" ", "_")
    processed_dir = processed_root / disease_safe / accession
    
    if not processed_dir.exists():
        processed_dir = processed_root / accession
        if not processed_dir.exists():
            logger.warning(f"Skipping {accession}: Data directory not found.")
            return

    input_csv = processed_dir / "expression_log_normalized.csv"
    if not input_csv.exists():
        input_csv = processed_dir / "expression.csv" # Fallback
        
    spike_path = Path(f"data/spikes/{accession}/spikes.pkl")
    
    if not spike_path.exists():
        logger.warning(f"Skipping {accession}: No spikes found.")
        return

    res_dir = Path(f"results/{accession}")
    
    weights_dir = res_dir / "weights"
    logs_dir = res_dir / "logs"
    
    for d in [weights_dir, logs_dir]:
        d.mkdir(parents=True, exist_ok=True)
        
    if (weights_dir / "trained_weights.npy").exists() and (weights_dir / "gene_names.json").exists():
        logger.info(f"Skipping {accession}: Already trained and has gene metadata.")
        return

    logger.info(f"Training SNN for cohort {accession}...")
    
    try:
        # Load expression to find HVGs if needed
        df = pd.read_csv(input_csv, index_col=0)
        n_orig_genes = df.shape[1]
        
        # Load spikes
        with open(spike_path, "rb") as f:
            all_spikes = pickle.load(f)
            
        selected_indices = list(range(n_orig_genes))
        
        if n_orig_genes > MAX_NEURONS:
            logger.info(f"Selecting top {MAX_NEURONS} HVGs for {accession}...")
            # HVG selection
            variances = df.var(axis=0)
            selected_indices = np.argsort(variances)[-MAX_NEURONS:].values
            # Filter spikes
            spikes = [all_spikes[i] for i in selected_indices]
            n_genes = MAX_NEURONS
        else:
            spikes = all_spikes
            n_genes = n_orig_genes
            
        # Initialize STDP from config
        stdp_params = config.get("training", {}).get("stdp", {})
        stdp_rule = CausalSTDP(
            learning_rate=stdp_params.get("learning_rate", 0.01),
            tau_plus=stdp_params.get("tau_plus", 20.0),
            tau_minus=stdp_params.get("tau_minus", 20.0)
        )
        
        # Instantiate Trainer
        trainer = Trainer(n_genes=n_genes)
        trainer.network.stdp = stdp_rule
        
        # Calc duration
        max_time = 0
        for s in spikes:
            if len(s) > 0: max_time = max(max_time, s.max())
        duration = max_time + 100.0
        
        # Train
        weights = trainer.train_cohort(spikes, duration_ms=duration, dt=config.get("training", {}).get("dt", 1.0))
        
        # Save
        np.save(weights_dir / "trained_weights.npy", weights)
        np.save(weights_dir / "selected_indices.npy", np.array(selected_indices))
        
        # Save Gene Names for later GRN extraction
        gene_names = df.columns[selected_indices].tolist()
        with open(weights_dir / "gene_names.json", "w") as f:
            json.dump(gene_names, f)
            
        stats = {
            "n_genes": n_genes,
            "duration": duration,
            "mean_weight": float(np.mean(np.abs(weights))),
            "max_weight": float(np.max(weights)),
            "min_weight": float(np.min(weights)),
            "normalization": "Log2(CPM+1)" # From previous step
        }
        with open(logs_dir / "training_stats.json", "w") as f:
            json.dump(stats, f, indent=2)
            
        logger.info(f"Completed {accession}: Mean weight {stats['mean_weight']:.4f}")
        
    except Exception as e:
        logger.error(f"Training failed for {accession}: {e}")
    finally:
        del df
        del all_spikes
        gc.collect()

def main():
    config = load_config()
    registry_path = "data/cohort_index.csv"
    if not os.path.exists(registry_path):
        return
        
    df = pd.read_csv(registry_path)
    
    for _, row in df.iterrows():
        train_cohort(row["accession"], row["disease"], config)

if __name__ == "__main__":
    main()