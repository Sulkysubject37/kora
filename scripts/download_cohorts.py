import pandas as pd
import GEOparse
import logging
from pathlib import Path
import os
import shutil
import argparse
import requests
import re
from src.utils.dataset_fetchers import fetch_metadata

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_file(url, dest_path):
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(dest_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        logger.info(f"Downloaded {dest_path.name}")
        return True
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        return False

def download_supp_files(gse, dest_dir: Path):
    """
    Downloads count matrices or normalized data from supplementary files.
    """
    # GEOparse puts metadata in gse.metadata (dict)
    # But usually links are in the relations or explicit fields?
    # Actually, GEOparse has gse.relations -> but that's for samples.
    # We want Series Supplementary File.
    
    # In SOFT format: !Series_supplementary_file = ftp://...
    
    supp_files = gse.metadata.get("supplementary_file", [])
    if isinstance(supp_files, str):
        supp_files = [supp_files]
        
    logger.info(f"Found {len(supp_files)} supplementary files.")
    
    # Filter for useful files
    useful_patterns = [r"count", r"matrix", r"fpkm", r"tpm", r"norm", r"expression"]
    
    for url in supp_files:
        filename = url.split("/")[-1]
        
        # Check if useful
        is_useful = any(re.search(p, filename, re.IGNORECASE) for p in useful_patterns)
        
        # Also include generic .txt.gz or .csv.gz if we are desperate, but usually specific names exist.
        # If it's a tar of raw fastq, skip.
        if "fastq" in filename.lower() or "sra" in filename.lower():
            continue
            
        if is_useful:
            logger.info(f"Downloading supplementary: {filename}")
            download_file(url, dest_dir / filename)

def download_geo(accession: str, dest_dir: Path):
    """
    Downloads GEO dataset (SOFT file) using GEOparse.
    Checks for HTS and downloads supplementary if needed.
    """
    logger.info(f"Processing {accession} in {dest_dir}...")
    
    soft_path = dest_dir / f"{accession}_family.soft.gz"
    
    try:
        # 1. Download SOFT (Metadata + Array Data)
        if not soft_path.exists():
            gse = GEOparse.get_GEO(geo=accession, destdir=str(dest_dir), silent=True)
            logger.info(f"Downloaded SOFT for {accession}")
        else:
            logger.info(f"SOFT file exists for {accession}")
            # Load it to check for Supp Files
            gse = GEOparse.get_GEO(filepath=str(soft_path), silent=True)

        # 2. Check if we need Supplementary Files (HTS check)
        # Heuristic: Check if 'platform_id' contains 'GPL' that is Illumina? 
        # Or check if pivot_samples fails / returns empty?
        
        try:
            df = gse.pivot_samples("VALUE")
            if df.empty:
                logger.info(f"{accession} has no data table. Attempting supplementary download.")
                download_supp_files(gse, dest_dir)
            else:
                logger.info(f"{accession} has data table in SOFT.")
                
        except Exception as e:
            logger.info(f"{accession} table parse error ({e}). Attempting supplementary download.")
            download_supp_files(gse, dest_dir)

    except Exception as e:
        logger.error(f"Failed to process {accession}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Download cohorts from public repositories.")
    parser.add_argument("--index", default="data/dataset_index.csv", help="Path to dataset index.")
    parser.add_argument("--limit", type=int, default=1, help="Max datasets to download per disease.")
    parser.add_argument("--output_dir", default="data/raw", help="Output directory.")
    args = parser.parse_args()
    
    if not os.path.exists(args.index):
        logger.error(f"Index file {args.index} not found. Run discover_datasets.py first.")
        return

    df = pd.read_csv(args.index)
    
    root_dir = Path(args.output_dir)
    root_dir.mkdir(parents=True, exist_ok=True)
    
    grouped = df.groupby("disease_term")
    
    for disease, group in grouped:
        logger.info(f"Processing batch for {disease}...")
        
        count = 0
        for _, row in group.iterrows():
            if count >= args.limit:
                break
                
            accession = row["accession"]
            repo = row["repository"]
            
            dest_dir = root_dir / repo / accession
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            if repo == "GEO":
                download_geo(accession, dest_dir)
                count += 1
            elif repo == "ArrayExpress":
                pass
            
    logger.info("Download batch complete.")

if __name__ == "__main__":
    main()