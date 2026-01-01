import pandas as pd
import requests
from Bio import Entrez
import logging
from typing import List, Dict
import time
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
ENTREZ_EMAIL = "kora_agent@example.com"  # Using a placeholder as per plan
DISEASE_TERMS = [
    "Alzheimer's Disease",
    "Parkinson's Disease",
    "Amyotrophic Lateral Sclerosis",
    "Huntington's Disease",
    "Frontotemporal Dementia"
]

def search_geo(term: str, retmax: int = 20) -> List[Dict]:
    """
    Searches GEO via Entrez for human expression data.
    """
    Entrez.email = ENTREZ_EMAIL
    
    # Query: term AND "Homo sapiens"[Organism] AND "Expression profiling by array"[DataSet Type] OR "Expression profiling by high throughput sequencing"[DataSet Type]
    # Simplified for robust hits: term AND "Homo sapiens"[Organism] AND "gse"[Entry Type]
    query = f'("{term}") AND "Homo sapiens"[Organism] AND "gse"[Entry Type]'
    
    logger.info(f"Searching GEO for: {term}")
    
    try:
        handle = Entrez.esearch(db="gds", term=query, retmax=retmax, usehistory="y")
        results = Entrez.read(handle)
        handle.close()
        
        id_list = results["IdList"]
        if not id_list:
            return []
            
        # Fetch details (esummary)
        # Note: GDS db returns GDS IDs or GSE IDs depending on query. 
        # Usually for 'gse'[Entry Type], we get GDS uids that link to GSE.
        # Let's try to search 'gds' database but look for GSE accessions in summary.
        
        webenv = results["WebEnv"]
        query_key = results["QueryKey"]
        
        handle = Entrez.esummary(db="gds", query_key=query_key, WebEnv=webenv)
        summaries = Entrez.read(handle)
        handle.close()
        
        dataset_list = []
        for doc in summaries:
            # Extract relevant fields
            # doc is a dict. Structure varies.
            # Look for 'Accession' usually starting with GSE
            accession = doc.get("Accession", "")
            if not accession.startswith("GSE"):
                continue
                
            dataset_list.append({
                "accession": accession,
                "repository": "GEO",
                "disease_term": term,
                "num_samples_estimate": doc.get("n_samples", "Unknown"),
                "data_type": doc.get("gdsType", "Unknown"), # e.g., 'Expression profiling by array'
                "metadata_source": "Entrez",
                "raw_link_endpoint": f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={accession}"
            })
            
        return dataset_list

    except Exception as e:
        logger.error(f"Error searching GEO for {term}: {e}")
        return []

def search_arrayexpress(term: str) -> List[Dict]:
    """
    Searches ArrayExpress/BioStudies via REST API.
    """
    base_url = "https://www.ebi.ac.uk/biostudies/api/v1/search"
    
    # Query structure
    params = {
        "query": f"{term} AND organism:\"Homo sapiens\"",
        "page": 1,
        "pageSize": 20
    }
    
    logger.info(f"Searching ArrayExpress for: {term}")
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        dataset_list = []
        for hit in data.get("hits", []):
            accession = hit.get("accession", "")
            
            # Simple heuristic for samples count (often in 'content')
            # But specific metadata requires detail fetch. We just estimate or leave blank.
            # ArrayExpress hits usually have 'files' or 'links' count, but not explicit samples in search hit.
            
            # Check if it looks like transcriptomics
            # content can contain 'RNA-seq', 'microarray'
            content_str = str(hit).lower()
            data_type = "Unknown"
            if "rna-seq" in content_str:
                data_type = "RNA-seq"
            elif "array" in content_str:
                data_type = "Microarray"
            
            dataset_list.append({
                "accession": accession,
                "repository": "ArrayExpress",
                "disease_term": term,
                "num_samples_estimate": "Unknown", # Need deeper fetch
                "data_type": data_type,
                "metadata_source": "BioStudies API",
                "raw_link_endpoint": f"https://www.ebi.ac.uk/biostudies/studies/{accession}"
            })
            
        return dataset_list
        
    except Exception as e:
        logger.error(f"Error searching ArrayExpress for {term}: {e}")
        return []

def main():
    all_datasets = []
    
    for term in DISEASE_TERMS:
        # GEO
        geo_hits = search_geo(term)
        all_datasets.extend(geo_hits)
        time.sleep(1) # Courtesy delay
        
        # ArrayExpress
        ae_hits = search_arrayexpress(term)
        all_datasets.extend(ae_hits)
        time.sleep(1)
        
    # Convert to DataFrame
    df = pd.DataFrame(all_datasets)
    
    # Remove duplicates (some studies cover multiple terms)
    df = df.drop_duplicates(subset=["accession"])
    
    output_path = "data/dataset_index.csv"
    df.to_csv(output_path, index=False)
    logger.info(f"Saved {len(df)} unique datasets to {output_path}")
    
    # Print sample
    print(df.head())

if __name__ == "__main__":
    main()
