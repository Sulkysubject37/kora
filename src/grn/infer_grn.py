import numpy as np
import networkx as nx
from typing import Tuple, Dict
import logging

logger = logging.getLogger(__name__)

class GRNExtractor:
    """
    Extracts stable Gene Regulatory Networks from SNN weights.
    """
    
    def __init__(self, 
                 weight_threshold: float = 0.1, 
                 stability_window: int = 5):
        self.threshold = weight_threshold
        self.stability_window = stability_window
        
    def extract(self, weights: np.ndarray, gene_names: list = None) -> nx.DiGraph:
        """
        Converts weight matrix to Directed Graph.
        
        Args:
            weights: (n_genes, n_genes) matrix. Rows=Pre(Source), Cols=Post(Target).
            gene_names: Optional list of gene names.
            
        Returns:
            NetworkX DiGraph with edge attributes 'weight' and 'sign'.
        """
        n_genes = weights.shape[0]
        G = nx.DiGraph()
        
        if gene_names is None:
            gene_names = [f"Gene_{i}" for i in range(n_genes)]
            
        G.add_nodes_from(gene_names)
        
        # Normalize weights? No, raw weights from STDP are interpretable.
        
        # Filter by threshold
        rows, cols = np.where(np.abs(weights) > self.threshold)
        
        for r, c in zip(rows, cols):
            if r == c: continue # No self-loops
            
            w = weights[r, c]
            sign = 1 if w > 0 else -1
            
            G.add_edge(gene_names[r], gene_names[c], weight=float(w), sign=sign)
            
        return G
        
    def compare_with_ground_truth(self, 
                                inferred_graph: nx.DiGraph, 
                                true_adj_path: str) -> Dict[str, float]:
        """
        Compares inferred graph with ground truth.
        """
        # Load truth
        true_adj = np.loadtxt(true_adj_path)
        
        # Convert inferred to adj
        nodes = sorted(list(inferred_graph.nodes()))
        n = len(nodes)
        node_map = {name: i for i, name in enumerate(nodes)}
        
        inferred_adj = np.zeros((n, n))
        for u, v, data in inferred_graph.edges(data=True):
            if u in node_map and v in node_map:
                inferred_adj[node_map[u], node_map[v]] = data['sign']
                
        # Compare
        # Binary classification metrics
        flat_true = (true_adj != 0).flatten()
        flat_pred = (inferred_adj != 0).flatten()
        
        tp = np.sum(flat_true & flat_pred)
        fp = np.sum((~flat_true) & flat_pred)
        fn = np.sum(flat_true & (~flat_pred))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "edges_true": int(np.sum(flat_true)),
            "edges_inferred": int(np.sum(flat_pred))
        }
