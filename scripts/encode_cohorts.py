import pandas as pd
import numpy as np
import logging
from pathlib import Path
import pickle
import sys
import os

# Ensure src is importable
sys.path.append(".")
from src.encoding.spike_encoding import SpikeEncoder

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def encode_cohort(accession):
    if accession == "GSE311578":
        logger.info(f"Skipping {accession}: Blacklisted (spike encoding issue).")
        return

    processed_dir = Path(f"data/processed/{accession}")
    input_path = processed_dir / "expression_log_normalized.csv"
    
    if not input_path.exists():
        # Fallback to expression.csv if normalized doesn't exist (shouldn't happen if normalized correctly)
        input_path = processed_dir / "expression.csv"
        if not input_path.exists():
            logger.warning(f"Skipping {accession}: No data found.")
            return

    output_dir = Path(f"data/spikes/{accession}")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "spikes.pkl"
    
    if output_path.exists():
        logger.info(f"Skipping {accession}: Spikes already exist.")
        return

    logger.info(f"Encoding {accession}...")
    
    try:
        df = pd.read_csv(input_path, index_col=0)
        
        # 1. Normalize to [0, 1] for rate encoding
        # Global min/max for the cohort to preserve relative expression differences
        min_val = df.min().min()
        max_val = df.max().max()
        
        if max_val == min_val:
            logger.warning(f"Flat data for {accession}. Skipping.")
            return
            
        df_norm = (df - min_val) / (max_val - min_val)
        
        # 2. Encode
        # Data shape: (Samples, Genes)
        # We treat samples as time steps? 
        # "Time dimension = sample index"
        # dt = 1.0 ms per sample? 
        # Or we hold each sample for T ms?
        # Let's use 20ms per sample to give STDP time to act (tau ~ 20ms).
        
        step_duration = 20.0
        data = df_norm.values
        duration_ms = len(df) * step_duration
        
        encoder = SpikeEncoder(dt=1.0, max_freq=100.0) # 100Hz max
        
        # To simulate "holding" the value, we can repeat the rows or rely on the encoder's interpolation.
        # My encoder implementation (checked previously) handles 2D input by spacing them.
        # But wait, my previous check of `src/encoding/spike_encoding.py` showed:
        # "If 2D ... interpolates or segments ... assumes expression_data points are equally spaced over duration_ms"
        # So passing `duration_ms = len * 20` means it will space points 20ms apart.
        
        spikes = encoder.encode(data, duration_ms=duration_ms)
        
        # Save
        with open(output_path, "wb") as f:
            pickle.dump(spikes, f)
            
        logger.info(f"Encoded {accession}: {len(spikes)} neurons, {duration_ms} ms")
        
    except Exception as e:
        logger.error(f"Failed to encode {accession}: {e}")

def main():
    registry_path = "data/cohort_index.csv"
    if not os.path.exists(registry_path):
        return
        
    df = pd.read_csv(registry_path)
    for _, row in df.iterrows():
        encode_cohort(row["accession"])

if __name__ == "__main__":
    main()
