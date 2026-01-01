import pandas as pd
import GEOparse
import logging
from pathlib import Path
import os
import shutil
import argparse
from src.utils.dataset_fetchers import fetch_metadata

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_geo(accession: str, dest_dir: Path):
    """
    Downloads GEO dataset (SOFT file) using GEOparse.
    """
    logger.info(f"Downloading {accession} to {dest_dir}...")
    try:
        # GEOparse downloads to CWD by default or specific path.
        # destdir param exists.
        
        # Check if already exists
        if (dest_dir / f"{accession}_family.soft.gz").exists():
            logger.info(f"{accession} already exists.")
            return

        gse = GEOparse.get_GEO(geo=accession, destdir=str(dest_dir), silent=True)
        logger.info(f"Successfully downloaded {accession}")
        
    except Exception as e:
        logger.error(f"Failed to download {accession}: {e}")

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
    
    # Create raw dir
    root_dir = Path(args.output_dir)
    root_dir.mkdir(parents=True, exist_ok=True)
    
    # Group by disease
    grouped = df.groupby("disease_term")
    
    for disease, group in grouped:
        logger.info(f"Processing {disease}...")
        
        count = 0
        for _, row in group.iterrows():
            if count >= args.limit:
                break
                
            accession = row["accession"]
            repo = row["repository"]
            
            # Create accession dir
            # Structure: data/raw/{repo}/{accession}/
            dest_dir = root_dir / repo / accession
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Fetch metadata first to validate
            meta = fetch_metadata(accession, repo)
            if not meta:
                continue
                
            # Save metadata
            import json
            with open(dest_dir / "metadata.json", "w") as f:
                # Handle non-serializable? meta contains simple types mostly.
                # AE returns raw_json which is fine.
                try:
                    json.dump(meta, f, indent=2, default=str)
                except Exception as e:
                    logger.warning(f"Could not save metadata JSON: {e}")
            
            # Download Data
            if repo == "GEO":
                download_geo(accession, dest_dir)
                count += 1
            elif repo == "ArrayExpress":
                # AE download logic is complex (ftp listing). 
                # For this iteration, we log as pending implementation or manual.
                logger.warning(f"ArrayExpress download automated logic not fully implemented. Skipping {accession}.")
                # In a real scenario, we'd use 'ftplib' or requests on the 'files' endpoint.
                pass
            
            # Check if we should stop for this disease
            
    logger.info("Download batch complete.")

if __name__ == "__main__":
    main()
