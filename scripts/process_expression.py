import pandas as pd
import numpy as np
import GEOparse
import logging
from pathlib import Path
import os
import glob
from sklearn.preprocessing import MinMaxScaler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_geo_soft(soft_path: Path, output_dir: Path):
    """
    Parses SOFT file, extracts expression matrix, normalizes.
    """
    logger.info(f"Processing {soft_path}...")
    try:
        gse = GEOparse.get_GEO(filepath=str(soft_path), silent=True)
        
        # Merge GSMs into a DataFrame
        # This can be heavy. GEOparse pivots automatically?
        # gse.pivot_samples(values="VALUE") is the common way.
        
        df = gse.pivot_samples("VALUE")
        
        if df.empty:
            logger.warning(f"No data found in {soft_path}")
            return

        # Check for NaNs
        df = df.dropna()
        
        # Normalization
        # 1. Log2 if not logged (Heuristic: max > 50)
        if df.max().max() > 50:
            logger.info("Data appears unlogged. Applying log2(x+1).")
            df = np.log2(df + 1)
            
        # 2. MinMax Scaling to [0, 1] for SNN encoding
        scaler = MinMaxScaler()
        # Scale per gene (rows) or per sample (cols)?
        #df is Genes x Samples.
        # We usually want to normalize dynamics per gene to [0, 1] range to drive spikes.
        # Transpose to Samples x Genes for scaler (scales columns)
        
        df_T = df.T # Now Samples x Genes
        scaled_data = scaler.fit_transform(df_T)
        df_scaled = pd.DataFrame(scaled_data, index=df_T.index, columns=df_T.columns)
        
        # Save
        output_path = output_dir / "expression.csv"
        df_scaled.to_csv(output_path)
        logger.info(f"Saved processed data to {output_path}")
        
    except Exception as e:
        logger.error(f"Error processing {soft_path}: {e}")

def main():
    raw_dir = Path("data/raw")
    processed_dir = Path("data/processed")
    
    # GEO
    geo_dir = raw_dir / "GEO"
    if geo_dir.exists():
        for accession_dir in geo_dir.iterdir():
            if not accession_dir.is_dir():
                continue
                
            accession = accession_dir.name
            
            # Look for SOFT file
            soft_files = list(accession_dir.glob("*_family.soft.gz"))
            if not soft_files:
                soft_files = list(accession_dir.glob("*.soft"))
                
            if soft_files:
                out_dir = processed_dir / accession
                out_dir.mkdir(parents=True, exist_ok=True)
                process_geo_soft(soft_files[0], out_dir)
    
    # AE - To be implemented
    
    logger.info("Processing complete.")

if __name__ == "__main__":
    main()
