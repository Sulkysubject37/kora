import pandas as pd
import numpy as np
import GEOparse
import logging
from pathlib import Path
import os
import glob
from sklearn.preprocessing import MinMaxScaler
import gc
import sys
import gzip

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 500MB safety
FILE_SIZE_LIMIT_BYTES = 500 * 1024 * 1024 

def load_dataset_index(index_path="data/dataset_index.csv"):
    if not os.path.exists(index_path):
        return {}
    try:
        df = pd.read_csv(index_path)
        return dict(zip(df["accession"], df["disease_term"]))
    except Exception:
        return {}

def sanitize_dirname(name):
    if not isinstance(name, str): return "Uncategorized"
    return name.replace(" ", "_").replace("'", "").replace("/", "_")

def normalize_dataframe(df):
    """
    Standardizes a gene expression dataframe (samples x genes).
    """
    # Ensure numeric
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    
    # 1. Log2 if max > 50
    if df.max().max() > 50:
        logger.info("Applying log2(x+1).")
        df = np.log2(df + 1)
        
    # 2. MinMax Scaling to [0, 1]
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df) # Scaler works on columns. We want to scale each gene (col) or sample (row)?
    # Usually: normalize expression of a gene across samples [0,1] or normalize sample to [0,1]?
    # KORA SNN spike encoding usually wants input in [0, 1].
    # SpikeEncoder takes (Time/Samples, Genes).
    # We want each gene's expression to drive firing rate.
    # So we scale each GENE column to [0, 1].
    
    df_scaled = pd.DataFrame(scaled, index=df.index, columns=df.columns)
    return df_scaled

def process_supp_file(file_path):
    """
    Tries to parse a supplementary file into a DataFrame.
    """
    logger.info(f"Parsing supplementary: {file_path.name}")
    
    # Detect delimiter
    if "csv" in file_path.name.lower():
        sep = ","
    else:
        sep = "\t" # default
        
    try:
        if file_path.suffix == ".gz":
            with gzip.open(file_path, 'rt') as f:
                df = pd.read_csv(f, sep=sep, index_col=0)
        elif file_path.suffix == ".tar":
            logger.warning("Skipping tar archive (needs extraction).")
            return None
        elif file_path.suffix == ".xlsx":
            df = pd.read_excel(file_path, index_col=0)
        else:
            df = pd.read_csv(file_path, sep=sep, index_col=0)
            
        # Orient: Samples (rows) x Genes (cols)
        # Heuristic: Genes > Samples usually.
        if df.shape[0] > df.shape[1]:
            df = df.T
            
        return df
    except Exception as e:
        logger.warning(f"Failed to parse {file_path}: {e}")
        return None

def process_directory(accession, input_dir, output_dir):
    try:
        # 1. Check SOFT
        soft_files = list(input_dir.glob("*_family.soft.gz"))
        df = None
        
        if soft_files:
            try:
                gse = GEOparse.get_GEO(filepath=str(soft_files[0]), silent=True)
                df = gse.pivot_samples("VALUE")
                if df.empty:
                    df = None
                else:
                    df = df.T # Samples x Genes
            except Exception as e:
                logger.warning(f"SOFT parse failed for {accession}: {e}")
        
        # 2. If no SOFT table, look for supplementary
        if df is None or df.empty:
            supp_files = [f for f in input_dir.iterdir() if f.name != soft_files[0].name and not f.name.startswith("metadata")]
            # Filter for likely matrix files
            matrices = [f for f in supp_files if "count" in f.name.lower() or "matrix" in f.name.lower() or "norm" in f.name.lower() or "fpkm" in f.name.lower() or "tpm" in f.name.lower()]
            
            if matrices:
                # Pick largest or first?
                # Sometimes multiple files (one per sample). We need robust merging.
                # For now, pick the first single matrix file.
                target = matrices[0]
                df = process_supp_file(target)
                
        if df is not None and not df.empty:
            df_norm = normalize_dataframe(df)
            
            out_path = output_dir / "expression.csv"
            df_norm.to_csv(out_path)
            logger.info(f"Saved {accession} expression.csv ({df_norm.shape})")
        else:
            logger.warning(f"No usable data found for {accession}")

    except Exception as e:
        logger.error(f"Crash processing {accession}: {e}")
    finally:
        gc.collect()

def main():
    raw_dir = Path("data/raw/GEO")
    processed_dir = Path("data/processed")
    
    if not raw_dir.exists():
        logger.error("No raw data found.")
        return

    # Iterate Disease dirs
    for disease_dir in raw_dir.iterdir():
        if not disease_dir.is_dir(): continue
        
        disease_name = disease_dir.name
        logger.info(f"Processing disease group: {disease_name}")
        
        for accession_dir in disease_dir.iterdir():
            if not accession_dir.is_dir(): continue
            
            accession = accession_dir.name
            out_dir = processed_dir / disease_name / accession
            
            if (out_dir / "expression.csv").exists():
                logger.info(f"Skipping {accession}: Already processed.")
                continue
                
            out_dir.mkdir(parents=True, exist_ok=True)
            process_directory(accession, accession_dir, out_dir)

if __name__ == "__main__":
    main()