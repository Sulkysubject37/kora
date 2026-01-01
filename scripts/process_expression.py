import pandas as pd
import numpy as np
import GEOparse
import logging
from pathlib import Path
import os
import glob
from sklearn.preprocessing import MinMaxScaler
import shutil
import gc
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Memory safety limit (approximate file size in bytes)
# 500MB compressed might expand to 5-10GB in memory dataframe
FILE_SIZE_LIMIT_BYTES = 500 * 1024 * 1024 

def load_dataset_index(index_path="data/dataset_index.csv"):
    if not os.path.exists(index_path):
        return {}
    try:
        df = pd.read_csv(index_path)
        return dict(zip(df["accession"], df["disease_term"]))
    except Exception as e:
        logger.error(f"Failed to load index: {e}")
        return {}

def sanitize_dirname(name):
    if not isinstance(name, str):
        return "Uncategorized"
    return name.replace(" ", "_").replace("'", "").replace("/", "_")

def process_geo_soft(soft_path: Path, output_dir: Path):
    """
    Parses SOFT file, extracts expression matrix, normalizes.
    """
    logger.info(f"Processing {soft_path}...")
    
    # Check file size
    try:
        size = soft_path.stat().st_size
        if size > FILE_SIZE_LIMIT_BYTES:
            logger.warning(f"Skipping {soft_path.name}: File size {size/1024/1024:.2f}MB exceeds limit.")
            return
    except Exception as e:
        logger.warning(f"Could not check file size: {e}")

    gse = None
    df = None
    
    try:
        # Load with minimal metadata if possible, but GEOparse loads all.
        gse = GEOparse.get_GEO(filepath=str(soft_path), silent=True)
        
        # Pivot samples
        # This is the memory intensive part
        df = gse.pivot_samples("VALUE")
        
        if df.empty:
            logger.warning(f"No data found in {soft_path}")
            return

        # Check for NaNs and clean
        df = df.dropna()
        
        # Normalization
        # 1. Log2 if not logged (Heuristic: max > 50)
        if df.max().max() > 50:
            logger.info("Data appears unlogged. Applying log2(x+1).")
            df = np.log2(df + 1)
            
        # 2. MinMax Scaling to [0, 1]
        scaler = MinMaxScaler()
        
        # Transpose to Samples x Genes for scaler
        df_T = df.T 
        scaled_data = scaler.fit_transform(df_T)
        df_scaled = pd.DataFrame(scaled_data, index=df_T.index, columns=df_T.columns)
        
        # Save
        output_path = output_dir / "expression.csv"
        df_scaled.to_csv(output_path)
        logger.info(f"Saved processed data to {output_path}")
        
    except Exception as e:
        logger.error(f"Error processing {soft_path}: {e}")
        
    finally:
        # Aggressive cleanup
        del gse
        del df
        gc.collect()

def main():
    raw_dir = Path("data/raw")
    processed_dir = Path("data/processed")
    
    disease_map = load_dataset_index()
    
    # GEO
    geo_dir = raw_dir / "GEO"
    if geo_dir.exists():
        # Iterate over accessions
        accession_dirs = [d for d in geo_dir.iterdir() if d.is_dir()]
        logger.info(f"Found {len(accession_dirs)} directories in {geo_dir}")
        
        for accession_dir in accession_dirs:
            accession = accession_dir.name
            
            # Determine target subdirectory
            disease_term = disease_map.get(accession, "Uncategorized")
            safe_disease_dir = sanitize_dirname(disease_term)
            
            # Check if output already exists to skip
            out_dir = processed_dir / safe_disease_dir / accession
            if (out_dir / "expression.csv").exists():
                logger.info(f"Skipping {accession}: Already processed.")
                continue
            
            out_dir.mkdir(parents=True, exist_ok=True)
            
            # Look for SOFT file
            soft_files = list(accession_dir.glob("*_family.soft.gz"))
            if not soft_files:
                soft_files = list(accession_dir.glob("*.soft"))
                
            if soft_files:
                try:
                    process_geo_soft(soft_files[0], out_dir)
                except KeyboardInterrupt:
                    logger.error("Interrupted by user.")
                    sys.exit(1)
                except Exception as e:
                    logger.error(f"Unexpected crash processing {accession}: {e}")
            else:
                logger.debug(f"No SOFT file in {accession}")
    
    logger.info("Processing complete.")

if __name__ == "__main__":
    main()
