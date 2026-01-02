import pandas as pd
import requests
import logging
import GEOparse
from pathlib import Path
import time

logger = logging.getLogger(__name__)

def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def map_ensembl_to_symbol(ensembl_ids):
    """
    Maps Ensembl IDs to HGNC Symbols using mygene.info API.
    """
    # Remove version numbers if present (ENSG000001.1 -> ENSG000001)
    cleaned_ids = [str(x).split('.')[0] for x in ensembl_ids]
    unique_ids = list(set(cleaned_ids))
    
    mapping = {}
    
    logger.info(f"Querying mygene.info for {len(unique_ids)} Ensembl IDs...")
    
    url = "https://mygene.info/v3/query"
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    
    # Chunking for API limits (1000 per request is usually safe for POST)
    for chunk in chunk_list(unique_ids, 1000):
        params = {
            'q': ",".join(chunk),
            'scopes': 'ensembl.gene',
            'fields': 'symbol',
            'species': 'human'
        }
        try:
            response = requests.post(url, data=params, headers=headers)
            response.raise_for_status()
            for hit in response.json():
                if 'symbol' in hit:
                    mapping[hit['query']] = hit['symbol']
        except Exception as e:
            logger.error(f"mygene.info query failed: {e}")
            time.sleep(1) # Backoff
            
    # Create final map including version handling
    final_map = {}
    for orig in ensembl_ids:
        clean = str(orig).split('.')[0]
        if clean in mapping:
            final_map[orig] = mapping[clean]
    
    return final_map

def map_entrez_to_symbol(entrez_ids):
    """
    Maps Entrez Gene IDs to HGNC Symbols using mygene.info API.
    """
    unique_ids = list(set([str(x) for x in entrez_ids]))
    mapping = {}
    
    logger.info(f"Querying mygene.info for {len(unique_ids)} Entrez IDs...")
    
    url = "https://mygene.info/v3/query"
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    
    for chunk in chunk_list(unique_ids, 1000):
        params = {
            'q': ",".join(chunk),
            'scopes': 'entrezgene',
            'fields': 'symbol',
            'species': 'human'
        }
        try:
            response = requests.post(url, data=params, headers=headers)
            response.raise_for_status()
            for hit in response.json():
                if 'symbol' in hit:
                    mapping[hit['query']] = hit['symbol']
        except Exception as e:
            logger.error(f"mygene.info query failed: {e}")
            time.sleep(1)
            
    final_map = {}
    for orig in entrez_ids:
        s_orig = str(orig)
        if s_orig in mapping:
            final_map[orig] = mapping[s_orig]
            
    return final_map

def extract_symbol_from_complex_string(val):
    """
    Heuristic to extract a gene symbol from a complex annotation string.
    Common formats:
    - Accession // Symbol // Description
    - Description (Symbol), mRNA.
    - Description [Source:HGNC Symbol;Acc:HGNC:123]
    """
    if not val or val.lower() == "nan":
        return None
        
    # Case: Multiple transcripts separated by ///
    if "///" in val:
        val = val.split("///")[0].strip()
        
    # Case: Multiple fields separated by //
    if "//" in val:
        parts = [p.strip() for p in val.split("//")]
        # Usually index 1 is symbol, but let's check index 2 too for Clariom S
        if len(parts) > 1:
            # If part 1 is just a few chars, it's likely the symbol
            if 1 < len(parts[1]) < 20 and parts[1].isupper():
                return parts[1]
            # Try to find (SYMBOL) in part 2 or part 1
            import re
            for p in parts:
                m = re.search(r'\(([A-Z0-9\-]{2,20})\)', p)
                if m:
                    return m.group(1)
                # Try [Source:HGNC Symbol;Acc:HGNC:14825]
                m = re.search(r'Source:HGNC Symbol;Acc:HGNC:(\d+)', p)
                # If we find this, we might need another mapping, but sometimes the symbol is just before it
                # For now, let's look for the symbol in brackets if parentheses fail
                m = re.search(r'\[([A-Z0-9\-]{2,20})\]', p)
                if m:
                    return m.group(1)

    # Fallback: simple split
    if "//" in val:
        return val.split("//")[1].strip()
        
    return val

def map_probes_to_symbol(probe_ids, accession, disease_term):
    """
    Extracts probe->symbol mapping from local SOFT file via GEOparse.
    """
    raw_dir = Path(f"data/raw/GEO/{disease_term.replace(' ', '_')}/{accession}")
    soft_path = raw_dir / f"{accession}_family.soft.gz"
    
    if not soft_path.exists():
        logger.warning(f"SOFT file not found for {accession} at {soft_path}")
        return {}
        
    try:
        gse = GEOparse.get_GEO(filepath=str(soft_path), silent=True)
        
        mapping = {}
        for gpl_name, gpl in gse.gpls.items():
            logger.info(f"Processing platform {gpl_name} for {accession}")
            table = gpl.table
            
            # Find gene symbol column
            symbol_col = None
            candidates = ["Gene Symbol", "Symbol", "Gene_Symbol", "GENE_SYMBOL", 
                          "gene_assignment", "ilmn_gene", "SPOT_ID.1", "SPOT_ID"]
            
            for cand in candidates:
                for col in table.columns:
                    if cand.lower() == col.lower():
                        symbol_col = col
                        break
                if symbol_col:
                    break
            
            if symbol_col:
                logger.info(f"Found symbol column: {symbol_col}")
                for _, row in table.iterrows():
                    pid = str(row["ID"])
                    val = str(row[symbol_col])
                    
                    symbol = extract_symbol_from_complex_string(val)
                    if symbol and symbol.lower() != "nan":
                        mapping[pid] = symbol
            else:
                logger.warning(f"No symbol column found in {gpl_name}. Columns: {list(table.columns)}")
                
        return mapping

    except Exception as e:
        logger.error(f"Failed to parse SOFT for {accession}: {e}")
        return {}
