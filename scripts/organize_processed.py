import pandas as pd
import shutil
import logging
from pathlib import Path
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    registry_path = "data/cohort_index.csv"
    if not os.path.exists(registry_path):
        logger.error("Cohort index not found.")
        return
        
    df = pd.read_csv(registry_path)
    processed_root = Path("data/processed")
    
    for _, row in df.iterrows():
        accession = row["accession"]
        disease = row["disease"].replace(" ", "_") # Safety
        
        # Old path
        old_path = processed_root / accession
        
        # New path
        new_disease_dir = processed_root / disease
        new_path = new_disease_dir / accession
        
        if old_path.exists() and old_path.is_dir():
            if new_path.exists():
                logger.warning(f"Destination {new_path} already exists. Skipping move for {accession}.")
                continue
                
            logger.info(f"Moving {accession} -> {disease}/{accession}")
            new_disease_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(old_path), str(new_path))
            
    # Cleanup empty flat dirs if any left (optional)
    
if __name__ == "__main__":
    main()
