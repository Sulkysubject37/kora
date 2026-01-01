import pandas as pd
import numpy as np
import logging
from pathlib import Path
import pickle
from src.encoding.spike_encoding import SpikeEncoder
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def encode_cohort(cohort_dir: Path, output_filename="spikes.pkl"):
    csv_path = cohort_dir / "expression.csv"
    if not csv_path.exists():
        return
        
    logger.info(f"Encoding {cohort_dir.name}...")
    
    try:
        df = pd.read_csv(csv_path, index_col=0)
        
        # Ensure values in [0, 1]
        if df.max().max() > 1.0 or df.min().min() < 0.0:
            logger.warning("Data outside [0, 1]. Clipping...")
            df = df.clip(0, 1)
            
        data = df.values # (Samples, Genes)
        
        # Initialize Encoder
        # Parameters could be loaded from config
        encoder = SpikeEncoder(dt=1.0, max_freq=100.0)
        
        # Encode
        # We treat the entire dataframe as one long time series for encoding
        # duration = n_samples * dt? 
        # Or we treat each sample as a static input for T ms?
        # The 'encode' method in spike_encoding.py handles 1D (constant) or 2D (time-varying).
        # We pass 2D: (Time, Genes).
        
        duration_ms = len(df) * 1.0 # 1ms per sample? That's too fast.
        # Let's say each sample is held for 100ms?
        # Or we interpolate?
        # Task 6 says "Binning parameters via config".
        # Let's assume 1 sample = 1 step for now (simplest), or 20ms.
        
        step_per_sample = 20.0
        duration_ms = len(df) * step_per_sample
        
        # We need to upsell the data if we want 'step_per_sample' resolution
        # simple repeat?
        # For now, let's just pass the raw data and let the encoder handle it.
        # The encoder implementation I wrote in Task 3:
        # "If 2D ... assumes expression_data points are equally spaced over duration_ms"
        # So passing duration_ms = len * 20.0 will effectively space them 20ms apart.
        
        spikes = encoder.encode(data, duration_ms=duration_ms)
        
        # Save
        out_path = cohort_dir / output_filename
        with open(out_path, "wb") as f:
            pickle.dump(spikes, f)
            
        logger.info(f"Saved spikes to {out_path}")
        
    except Exception as e:
        logger.error(f"Error encoding {cohort_dir}: {e}")

def main():
    processed_dir = Path("data/processed")
    
    # 1. Real Data
    for p in processed_dir.iterdir():
        if p.name == "synthetic": continue
        if p.is_dir():
            encode_cohort(p)
            
    # 2. Synthetic Data
    synth_dir = processed_dir / "synthetic"
    if synth_dir.exists():
        for p in synth_dir.iterdir():
            if p.is_dir():
                encode_cohort(p)

if __name__ == "__main__":
    main()
