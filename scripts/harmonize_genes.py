import pandas as pd
import logging
from pathlib import Path
import sys
import os

# Add src to path
sys.path.append(os.path.abspath("."))

from src.utils.gene_mapping import map_ensembl_to_symbol, map_probes_to_symbol, map_entrez_to_symbol

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def harmonize_dataset(accession, disease):
    disease_safe = disease.replace(" ", "_")
    processed_dir = Path(f"data/processed/{disease_safe}/{accession}")
    if not processed_dir.exists():
        # Fallback to flat structure if not found (backward compatibility or partial migration)
        flat_dir = Path(f"data/processed/{accession}")
        if flat_dir.exists():
            processed_dir = flat_dir
    
    input_path = processed_dir / "expression.csv"
    output_path = processed_dir / "expression_genes.csv"
    
    if not input_path.exists():
        logger.warning(f"Skipping {accession}: No expression.csv found.")
        return
        
    if output_path.exists():
        logger.info(f"Skipping {accession}: Already harmonized.")
        return

    if accession == "GSE158947":
        logger.info(f"Skipping {accession} temporarily due to size.")
        return

    logger.info(f"Harmonizing {accession}...")
    try:
        df = pd.read_csv(input_path, index_col=0)
    except Exception as e:
        logger.error(f"Could not read {input_path}: {e}")
        return

    # Check ID type based on first few columns
    sample_ids = [str(c) for c in df.columns]
    
    # Heuristics
    is_ensembl = any(c.startswith("ENSG") for c in sample_ids[:10])
    is_entrez = all(c.isdigit() for c in sample_ids[:10]) if sample_ids else False
    is_illumina = any(c.startswith("ILMN_") for c in sample_ids[:10])
    
    mapping = {}
    if is_ensembl:
        logger.info(f"{accession} appears to use Ensembl IDs.")
        mapping = map_ensembl_to_symbol(df.columns)
    elif is_entrez:
        logger.info(f"{accession} appears to use Entrez IDs.")
        mapping = map_entrez_to_symbol(df.columns)
    else:
        logger.info(f"{accession} appears to use Probe or other IDs. Checking SOFT...")
        mapping = map_probes_to_symbol(df.columns, accession, disease)
        
    if not mapping:
        logger.warning(f"No mapping found for {accession}.")
        # Check if already symbols (Heuristic: many columns, not mostly digits, mostly uppercase/alphanumeric)
        likely_symbols = all(not c.isdigit() for c in sample_ids[:10]) and len(sample_ids) > 0
        if likely_symbols:
            logger.info(f"{accession} might already be using symbols. Saving as is.")
            df.to_csv(output_path)
        return

    # Apply mapping
    cols_to_keep = []
    new_names = []
    
    for c in df.columns:
        if c in mapping:
            cols_to_keep.append(c)
            new_names.append(mapping[c])
            
    if not cols_to_keep:
        logger.warning(f"Mapping resulted in 0 genes for {accession}.")
        return
        
    df_subset = df[cols_to_keep]
    df_subset.columns = new_names
    
    # Aggregate duplicates (mean)
    df_final = df_subset.groupby(df_subset.columns, axis=1).mean()
    
    logger.info(f"Mapped {len(df.columns)} features -> {len(df_final.columns)} genes.")
    df_final.to_csv(output_path)

def main():
    index_path = "data/cohort_index.csv"
    if not os.path.exists(index_path):
        logger.error("Cohort index not found.")
        return
        
    df_index = pd.read_csv(index_path)
    
    for _, row in df_index.iterrows():
        harmonize_dataset(row["accession"], row["disease"])

if __name__ == "__main__":
    main()
