import logging
import argparse
import sys
import os
from pathlib import Path

try:
    import synapseclient
    from synapseclient.core.exceptions import SynapseError
except ImportError:
    synapseclient = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_synapse(syn_id: str, dest_dir: Path, auth_token: str):
    """
    Downloads a Synapse entity using a Personal Access Token.
    """
    if synapseclient is None:
        logger.error("synapseclient is not installed.")
        return

    if not auth_token:
        logger.error("Missing authentication token for Synapse.")
        return
        
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Connecting to Synapse to download {syn_id}...")
    try:
        syn = synapseclient.Synapse()
        syn.login(authToken=auth_token, silent=True)
        
        entity = syn.get(syn_id, downloadLocation=str(dest_dir))
        logger.info(f"Successfully downloaded {entity.name} ({syn_id}) to {dest_dir}")
        
        # Save metadata
        meta = {
            "name": entity.get("name", "Unknown"),
            "id": syn_id,
            "version": entity.get("versionNumber"),
            "modifiedOn": str(entity.get("modifiedOn", "Unknown"))
        }
        import json
        with open(dest_dir / "metadata.json", "w") as f:
            json.dump(meta, f, indent=2)
            
    except SynapseError as e:
        logger.error(f"Synapse error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Download controlled access datasets from Synapse.")
    parser.add_argument("--syn_id", required=True, help="Synapse ID (e.g., syn123456)")
    parser.add_argument("--token", help="Synapse Personal Access Token")
    parser.add_argument("--output_dir", default="data/raw/Synapse")
    
    args = parser.parse_args()
    
    # Priority: arg > env
    token = args.token or os.environ.get("SYNAPSE_AUTH_TOKEN")
    
    if not token:
        logger.error("No Synapse token provided via --token or SYNAPSE_AUTH_TOKEN environment variable.")
        sys.exit(1)
        
    dest_dir = Path(args.output_dir) / args.syn_id
    download_synapse(args.syn_id, dest_dir, token)

if __name__ == "__main__":
    main()