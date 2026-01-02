import GEOparse
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def inspect_gpl(gpl_name):
    """
    Downloads a GPL, prints its columns and the first 5 rows of its table.
    """
    try:
        logger.info(f"Fetching GPL: {gpl_name}...")
        gpl = GEOparse.get_GEO(geo=gpl_name, silent=True)
        
        print("\n" + "="*20)
        print(f"GPL: {gpl_name}")
        print(f"Title: {gpl.metadata.get('title', ['N/A'])[0]}")
        print(f"Columns: {gpl.table.columns.tolist()}")
        print("="*20 + "\n")
        
        print("Head of GPL table:")
        print(gpl.table.head())
        
    except Exception as e:
        logger.error(f"Failed to fetch or parse GPL {gpl_name}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect a GEO Platform (GPL) annotation table.")
    parser.add_argument("gpl_name", type=str, help="The GPL accession name (e.g., GPL570).")
    args = parser.parse_args()
    
    inspect_gpl(args.gpl_name)
