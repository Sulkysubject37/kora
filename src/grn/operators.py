import numpy as np
import networkx as nx
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class OperatorDistiller:
    """
    Distills learned GRN weights into fixed linear/non-linear operators for CoreML.
    """
    
    def __init__(self, activation_fn: str = "sigmoid"):
        self.activation = activation_fn
        
    def distill(self, grn: nx.DiGraph, n_genes: int) -> Dict[str, Any]:
        """
        Converts GRN graph to operator matrices.
        
        Args:
            grn: Inferred GRN.
            n_genes: Total genes (dimension).
            
        Returns:
            Dictionary containing 'weights', 'bias', 'activation'.
        """
        # Create sparse weight matrix
        # CoreML usually likes dense for small/medium, or sparse storage.
        # We'll export dense for simplicity as n_genes is likely < 1000 for local models.
        
        W = np.zeros((n_genes, n_genes), dtype=np.float32)
        node_list = sorted(list(grn.nodes()))
        # Map node names "Gene_i" to index i
        # Assumes format "Gene_0", "Gene_1"...
        
        mapping = {}
        for node in node_list:
            try:
                idx = int(node.split('_')[1])
                mapping[node] = idx
            except:
                logger.warning(f"Could not parse index from node name {node}")
                
        for u, v, data in grn.edges(data=True):
            if u in mapping and v in mapping:
                # W_ij means j -> i usually in NN, but here we used row=source, col=target in GRN extraction
                # W[row, col] -> row affects col.
                # So if u -> v, then u is source, v is target.
                # In standard NN: y = Wx + b. x is input (source), y is output (target).
                # y_v = sum(W_vu * x_u).
                # So W_matrix should be (n_targets, n_sources).
                # GRN extraction stored weights[r, c] where r=source, c=target.
                # So we need to transpose to get W_vu.
                
                idx_u = mapping[u] # Source
                idx_v = mapping[v] # Target
                W[idx_v, idx_u] = data['weight'] # Transposed
                
        return {
            "weights": W,
            "bias": np.zeros(n_genes, dtype=np.float32), # Assuming zero bias for now
            "activation": self.activation
        }
