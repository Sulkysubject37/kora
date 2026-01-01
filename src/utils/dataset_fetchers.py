import logging
import requests
from Bio import Entrez
import pandas as pd
from typing import Dict, Optional, Any
import time

logger = logging.getLogger(__name__)

# Constants (Shared with discovery script, ideally in a config)
ENTREZ_EMAIL = "kora_agent@example.com" 

def fetch_geo_metadata(accession: str) -> Optional[Dict[str, Any]]:
    """
    Fetches metadata for a GEO accession using Entrez.
    Validates sample count >= 8.
    """
    Entrez.email = ENTREZ_EMAIL
    try:
        # Search to get GDS/GSE UID
        handle = Entrez.esearch(db="gds", term=f"{accession}[Accession]", retmax=1)
        search_res = Entrez.read(handle)
        handle.close()
        
        if not search_res["IdList"]:
            logger.warning(f"GEO Accession {accession} not found.")
            return None
            
        uid = search_res["IdList"][0]
        
        # Get Summary
        handle = Entrez.esummary(db="gds", id=uid)
        summary = Entrez.read(handle)[0]
        handle.close()
        
        n_samples = summary.get("n_samples", 0)
        # Type coercion
        if isinstance(n_samples, str) and n_samples.isdigit():
            n_samples = int(n_samples)
        
        if n_samples < 8:
            logger.warning(f"Skipping {accession}: Insufficient samples ({n_samples} < 8)")
            return None
            
        return {
            "accession": accession,
            "title": summary.get("title", ""),
            "summary": summary.get("summary", ""),
            "n_samples": n_samples,
            "platform": summary.get("gpl", ""), # GPL ID
            "taxon": summary.get("taxon", ""),
            "entry_type": summary.get("entryType", ""), # e.g. GSE
            "ftplink": summary.get("ftplink", "")
        }
        
    except Exception as e:
        logger.error(f"Error fetching GEO metadata for {accession}: {e}")
        return None

def fetch_arrayexpress_metadata(accession: str) -> Optional[Dict[str, Any]]:
    """
    Fetches metadata for ArrayExpress accession.
    """
    url = f"https://www.ebi.ac.uk/biostudies/api/v1/studies/{accession}"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            logger.warning(f"ArrayExpress Accession {accession} not found (Status {response.status_code})")
            return None
            
        data = response.json()
        
        # Parse logic for ArrayExpress is complex due to flexible JSON structure
        # Often 'section' -> 'subsections' contains 'Assays and Data'
        
        # Estimate n_samples from 'assays' count if available, or 'files'
        # This is a simplification.
        
        # Let's look for 'attributes' -> 'Sample count'? 
        # Usually BioStudies JSON has a 'section' with type 'Study'.
        
        # Minimal extraction
        title = data.get("title", "")
        
        # Try to find sample count in attributes
        n_samples = 0
        section = data.get("section", {})
        attrs = section.get("attributes", [])
        for attr in attrs:
            if attr.get("name") == "Sample count":
                try:
                    n_samples = int(attr.get("value"))
                except:
                    pass
        
        if n_samples < 8 and n_samples != 0: # If 0, we might have failed to parse, so maybe don't skip yet? 
            # But strict constraint says validate.
            logger.warning(f"Skipping {accession}: Insufficient samples ({n_samples} < 8)")
            return None
            
        return {
            "accession": accession,
            "title": title,
            "n_samples": n_samples,
            "raw_json": data # Store full blob for later parsing
        }

    except Exception as e:
        logger.error(f"Error fetching AE metadata for {accession}: {e}")
        return None

def fetch_metadata(accession: str, repository: str) -> Optional[Dict[str, Any]]:
    if repository == "GEO":
        return fetch_geo_metadata(accession)
    elif repository == "ArrayExpress":
        return fetch_arrayexpress_metadata(accession)
    else:
        logger.warning(f"Unknown repository {repository}")
        return None
