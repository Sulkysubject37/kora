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

SIZE_LIMIT_BYTES = 500 * 1024 * 1024
BLACKLIST = ["GSE268609"]

def sanitize_dirname(name):
    if not isinstance(name, str):
        return "Uncategorized"
    return name.replace(" ", "_").replace("'", "").replace("/", "_")

def get_remote_file_size(url):
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=10) as response:
            size = response.headers.get('Content-Length')
            if size:
                return int(size)
            return 0
    except Exception as e:
        logger.warning(f"Could not check size for {url}: {e}")
        return 0

def download_file_wget(url, dest_path):
    if dest_path.exists():
        logger.info(f"Skipping {dest_path.name}: Already exists.")
        return True

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
    supp_files = gse.metadata.get("supplementary_file", [])
    if isinstance(supp_files, str):
        supp_files = [supp_files]
        
    logger.info(f"Found {len(supp_files)} supplementary files.")
    useful_patterns = [r"count", r"matrix", r"fpkm", r"tpm", r"norm", r"expression", r"raw"]
    
    for url in supp_files:
        filename = url.split("/")[-1]
        # Skip raw sequencing reads explicitly
        if "fastq" in filename.lower() or "sra" in filename.lower() or "bam" in filename.lower():
            continue
            
        # Skip TAR archives (usually raw data)
        if filename.endswith(".tar") or filename.endswith(".tar.gz"):
            continue
            
        # Check usefulness
        is_useful = any(re.search(p, filename, re.IGNORECASE) for p in useful_patterns)
        if not is_useful and filename.endswith((".txt.gz", ".csv.gz", ".tsv.gz", ".xlsx", ".txt", ".csv", ".tsv")):
             is_useful = True
             
        if is_useful:
            logger.info(f"Attempting download: {filename}")
            download_file_wget(url, dest_dir / filename)

def is_fully_downloaded(dest_dir):
    """
    Checks if SOFT file exists and (if RNA-seq) at least one supplementary file exists.
    """
    soft = list(dest_dir.glob("*_family.soft.gz"))
    if not soft:
        return False
        
    # Heuristic: If we have SOFT, we *might* be done if it's microarray.
    # But if we started downloading supp files, we want to know.
    # Simple check: If folder has > 1 file (SOFT + something else), treat as downloaded.
    # Or just rely on `download_file_wget` skipping existing files.
    # The user asked to "don't download the dataset which is already downloaded" meaning SKIP THE PROCESSING steps too.
    
    # Let's say if SOFT exists, we assume we tried. 
    # But for RNA-seq we need supps.
    
    files = list(dest_dir.glob("*"))
    if len(files) > 1: 
        return True
    return False

def process_dataset(accession, disease, dest_dir):
    if accession in BLACKLIST:
        logger.info(f"Skipping {accession}: Blacklisted.")
        return

    if is_fully_downloaded(dest_dir):
        logger.info(f"Skipping {accession}: Already downloaded.")
        return

    logger.info(f"Processing {accession} ({disease}) -> {dest_dir}")
    
    soft_path = dest_dir / f"{accession}_family.soft.gz"
    
    try:
        if not soft_path.exists():
            try:
                gse = GEOparse.get_GEO(geo=accession, destdir=str(dest_dir), silent=True)
            except Exception as e:
                logger.error(f"SOFT download failed for {accession}: {e}")
                return
        else:
            gse = GEOparse.get_GEO(filepath=str(soft_path), silent=True)
            
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
    df_geo = df[df["repository"] == "GEO"]
    grouped = df_geo.groupby("disease_term")
    
    for disease, group in grouped:
        if any(term in disease for term in ["Alzheimer", "Amyotrophic", "Frontotemporal", "Huntington", "Parkinson"]):
            logger.info(f"Skipping {disease} as requested.")
            continue
            
        safe_disease = sanitize_dirname(disease)
        logger.info(f"=== {disease} ===")
        
        count = 0
        for _, row in group.iterrows():
            if count >= args.limit:
                break
                
            accession = row["accession"]
            dest_dir = Path(args.output_dir) / safe_disease / accession
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            process_dataset(accession, disease, dest_dir)
            
            # Count only if we actually processed or if it was already valid
            count += 1
            
    logger.info("Batch download complete.")

if __name__ == "__main__":
    main()
