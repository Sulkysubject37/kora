import pandas as pd
import GEOparse
import logging
from pathlib import Path
import os
import shutil
import argparse
import subprocess
import re
import urllib.request
from src.utils.dataset_fetchers import fetch_metadata

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Size limit: 500 MB
SIZE_LIMIT_BYTES = 500 * 1024 * 1024

def sanitize_dirname(name):
    if not isinstance(name, str):
        return "Uncategorized"
    return name.replace(" ", "_").replace("'", "").replace("/", "_")

def get_remote_file_size(url):
    """
    Gets file size in bytes using HTTP HEAD request or FTP SIZE command via urllib.
    """
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=10) as response:
            size = response.headers.get('Content-Length')
            if size:
                return int(size)
            return 0 # Unknown size
    except Exception as e:
        logger.warning(f"Could not check size for {url}: {e}")
        return 0

def download_file_wget(url, dest_path):
    # Check size first
    size = get_remote_file_size(url)
    if size > SIZE_LIMIT_BYTES:
        logger.warning(f"Skipping {url}: Size {size/1024/1024:.2f}MB exceeds 500MB limit.")
        return False

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
        
        # Skip raw sequencing reads explicitly
        if "fastq" in filename.lower() or "sra" in filename.lower() or "bam" in filename.lower():
            continue
            
        # Check usefulness
        is_useful = any(re.search(p, filename, re.IGNORECASE) for p in useful_patterns)
        
        # Also download standard txt/csv/tsv/xlsx if not explicitly raw reads
        if not is_useful and filename.endswith((".txt.gz", ".csv.gz", ".tsv.gz", ".xlsx", ".txt", ".csv", ".tsv")):
             is_useful = True
             
        if is_useful:
            logger.info(f"Attempting download: {filename}")
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
            # Check SOFT size? SOFT files are usually small (<100MB), but some huge array ones exist.
            # GEOparse downloads directly. We assume SOFT is okay or handle timeout.
            try:
                gse = GEOparse.get_GEO(geo=accession, destdir=str(dest_dir), silent=True)
            except Exception as e:
                logger.error(f"SOFT download failed for {accession}: {e}")
                return
        else:
            gse = GEOparse.get_GEO(filepath=str(soft_path), silent=True)
            
        # 2. Check for Data Table & Download Supp Files
        try:
            download_supp_files(gse, dest_dir)
        except Exception as e:
            logger.warning(f"Error handling supp files for {accession}: {e}")

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
            
            dest_dir = Path(args.output_dir) / safe_disease / accession
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            process_dataset(accession, disease, dest_dir)
            count += 1
            
    logger.info("Batch download complete.")

if __name__ == "__main__":
    main()