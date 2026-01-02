import pandas as pd
import numpy as np
import logging
from pathlib import Path
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def normalize_cpm(df):
    """
    Computes CPM: (counts / total_counts) * 1e6
    """
    library_sizes = df.sum(axis=1)
    library_sizes[library_sizes == 0] = 1
    cpm = df.div(library_sizes, axis=0) * 1e6
    return cpm

def process_cohort(accession, disease):
    disease_safe = disease.replace(" ", "_")
    processed_dir = Path(f"data/processed/{disease_safe}/{accession}")
    
    if not processed_dir.exists():
        # Fallback
        processed_dir = Path(f"data/processed/{accession}")
        if not processed_dir.exists():
            logger.warning(f"Skipping {accession}: Directory not found.")
            return

    input_path = processed_dir / "expression_genes.csv"
    output_path = processed_dir / "expression_log_normalized.csv"
    
    if not input_path.exists():
        logger.warning(f"Skipping {accession}: No harmonized expression_genes.csv found.")
        return
        
    if output_path.exists():
        logger.info(f"Skipping {accession}: Already normalized.")
        return

    logger.info(f"Normalizing {accession}...")
    try:
        df = pd.read_csv(input_path, index_col=0)
    except Exception as e:
        logger.error(f"Failed to read {input_path}: {e}")
        return

    # Check data characteristics
    data_max = df.max().max()
    data_min = df.min().min()
    
    method = "Unknown"
    
    # Heuristics
    if data_max > 1000:
        # Likely raw counts or intensity
        if (df % 1 == 0).all().all():
            # All integers -> Counts
            logger.info(f"{accession} looks like Raw Counts. Applying CPM + Log2.")
            df = normalize_cpm(df)
            df = np.log2(df + 1)
            method = "Log2(CPM+1)"
        else:
            # Floats but high values -> Intensity or unnormalized counts
            logger.info(f"{accession} looks like Raw Intensity/Floats. Applying Log2.")
            df = np.log2(df + 1)
            method = "Log2(Intensity+1)"
    elif data_min < 0:
        # Already Z-scored or centered?
        logger.info(f"{accession} has negative values. Assuming already normalized.")
        method = "Pass-through"
    elif data_max < 100:
        # Likely already Log2
        logger.info(f"{accession} max value is {data_max:.2f}. Assuming already Log2.")
        method = "Pass-through"
    else:
        # Gray area (100-1000). Safety log.
        logger.info(f"{accession} max {data_max:.2f} (Gray area). Applying Log2(x+1).")
        df = np.log2(df + 1)
        method = "Log2(x+1)"

    # Save
    df.to_csv(output_path)
    logger.info(f"Saved {accession} normalized matrix. Method: {method}")

def main():
    registry_path = "data/cohort_index.csv"
    if not os.path.exists(registry_path):
        return
    
    df = pd.read_csv(registry_path)
    for _, row in df.iterrows():
        process_cohort(row["accession"], row["disease"])

if __name__ == "__main__":
    main()
