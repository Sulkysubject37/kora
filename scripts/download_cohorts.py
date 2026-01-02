import pandas as pd
import GEOparse
import logging
from pathlib import Path
import os
import shutil
import argparse
import subprocess
import re
from src.utils.dataset_fetchers import fetch_metadata

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def sanitize_dirname(name):
    if not isinstance(name, str):
        return "Uncategorized"
    return name.replace(" ", "_").replace("'", "").replace("/", "_")

def download_file_wget(url, dest_path):
    try:
        cmd = ["wget", "-q", "-O", str(dest_path), url]
        subprocess.check_call(cmd)
        logger.info(f"Downloaded {dest_path.name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to download {url}: {e}")
        return False
    except FileNotFoundError:
        logger.error("wget not found.")
        return False

def download_supp_files(gse, dest_dir: Path):
    """
    Downloads count matrices or normalized data from supplementary files.
    """
    supp_files = gse.metadata.get("supplementary_file", [])
    if isinstance(supp_files, str):
        supp_files = [supp_files]
        
    logger.info(f"Found {len(supp_files)} supplementary files.")
    
    # Priority patterns for RNA-seq matrices
    useful_patterns = [r"count", r"matrix", r"fpkm", r"tpm", r"norm", r"expression", r"raw"]
    
    for url in supp_files:
        filename = url.split("/")[-1]
        
        # Skip raw sequencing reads
        if "fastq" in filename.lower() or "sra" in filename.lower() or "bam" in filename.lower():
            continue
            
        # Check usefulness
        is_useful = any(re.search(p, filename, re.IGNORECASE) for p in useful_patterns)
        
        # Also download standard txt/csv/tsv if not explicitly raw reads, as they might be the matrix
        if not is_useful and filename.endswith((".txt.gz", ".csv.gz", ".tsv.gz", ".xlsx", ".txt", ".csv", ".tsv")):
             # Weak match, but better than nothing for HTS
             is_useful = True
             
        if is_useful:
            logger.info(f"Downloading supplementary: {filename}")
            download_file_wget(url, dest_dir / filename)

def process_dataset(accession, disease, dest_dir):
    """
    Downloads SOFT and Supplementary files.
    """
    logger.info(f"Processing {accession} ({disease}) -> {dest_dir}")
    
    soft_path = dest_dir / f"{accession}_family.soft.gz"
    
    try:
        # 1. Download SOFT (Metadata)
        if not soft_path.exists():
            gse = GEOparse.get_GEO(geo=accession, destdir=str(dest_dir), silent=True)
        else:
            gse = GEOparse.get_GEO(filepath=str(soft_path), silent=True)
            
        # 2. Check for Data Table
        has_table = False
        try:
            # We don't want to load full table into memory if huge, but we need to check existence.
            # GEOparse loads it by default.
            if not gse.gsms: 
                # Series without samples in SOFT?
                pass
            else:
                # Check a sample
                pass
                
            # Try pivoting to see if value exists (small check)
            # This is expensive. Let's just check metadata 'type'.
            
            # If HTS, prioritize supplementary
            # But we download supplementary anyway to be safe as per user request ("properly this time")
            download_supp_files(gse, dest_dir)
            
        except Exception as e:
            logger.warning(f"Error checking table: {e}. Downloading supp files.")
            download_supp_files(gse, dest_dir)

    except Exception as e:
        logger.error(f"Failed to process {accession}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Download cohorts from GEO.")
    parser.add_argument("--index", default="data/dataset_index.csv", help="Path to dataset index.")
    parser.add_argument("--limit", type=int, default=20, help="Max datasets per disease.")
    parser.add_argument("--output_dir", default="data/raw/GEO", help="Output directory root.")
    args = parser.parse_args()
    
    if not os.path.exists(args.index):
        logger.error(f"Index file {args.index} not found.")
        return

    df = pd.read_csv(args.index)
    
    # Filter for GEO
    df_geo = df[df["repository"] == "GEO"]
    
    grouped = df_geo.groupby("disease_term")
    
    for disease, group in grouped:
        safe_disease = sanitize_dirname(disease)
        logger.info(f"=== {disease} ({len(group)} datasets available) ===")
        
        count = 0
        for _, row in group.iterrows():
            if count >= args.limit:
                break
                
            accession = row["accession"]
            
            # Structure: data/raw/GEO/{Disease}/{Accession}
            dest_dir = Path(args.output_dir) / safe_disease / accession
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            process_dataset(accession, disease, dest_dir)
            count += 1
            
    logger.info("Batch download complete.")

if __name__ == "__main__":
    main()
