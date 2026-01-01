import numpy as np
import pandas as pd
import networkx as nx
from pathlib import Path
from typing import Tuple, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class SyntheticGenerator:
    """
    Generates synthetic transcriptomic data for GRN inference benchmarking.
    Simulates temporal gene expression with progressive dysregulation and regulatory delays.
    """
    
    def __init__(self, n_genes: int = 100, n_timepoints: int = 50, n_cohorts: int = 1000, seed: int = 42):
        self.n_genes = n_genes
        self.n_timepoints = n_timepoints
        self.n_cohorts = n_cohorts
        self.rng = np.random.default_rng(seed)
        self.ground_truth_graph = None
        self.interaction_matrix = None
        
    def generate_ground_truth_grn(self, density: float = 0.1) -> nx.DiGraph:
        """
        Generates a random scale-free directed graph as the ground truth GRN.
        """
        # Using scale-free topology which is common in biological networks
        G = nx.scale_free_graph(self.n_genes, alpha=0.41, beta=0.54, gamma=0.05, seed=int(self.rng.integers(1000)))
        G = nx.DiGraph(G) # Convert multi-graph to simple directed graph
        
        # Remove self-loops and fix node indices
        G.remove_edges_from(nx.selfloop_edges(G))
        mapping = {n: i for i, n in enumerate(sorted(G.nodes()))}
        G = nx.relabel_nodes(G, mapping)
        
        # Ensure we have exactly n_genes (scale_free_graph might vary slightly or have disconnected components)
        # We'll just stick to the nodes 0..n_genes-1
        # Add random edges if density is too low or prune if too high, but scale-free is usually sparse.
        
        # Assign weights (regulatory strength): -1 (inhibitory) or +1 (excitatory)
        # Biology is often sparse.
        self.interaction_matrix = np.zeros((self.n_genes, self.n_genes))
        
        for u, v in G.edges():
            if u < self.n_genes and v < self.n_genes:
                weight = self.rng.choice([-1, 1], p=[0.3, 0.7]) # 70% excitatory
                G[u][v]['weight'] = weight
                self.interaction_matrix[u, v] = weight
                
        self.ground_truth_graph = G
        return G

    def simulate_dynamics(self, noise_level: float = 0.1, decay: float = 0.2) -> np.ndarray:
        """
        Simulates gene expression dynamics using a linear non-linear model with delay.
        x(t+1) = (1-decay)*x(t) + sigmoid(W * x(t)) + noise
        
        Returns:
            tensor of shape (n_cohorts, n_timepoints, n_genes)
        """
        if self.interaction_matrix is None:
            raise ValueError("GRN not generated. Call generate_ground_truth_grn first.")
            
        # Initialize cohorts
        # Shape: (n_cohorts, n_timepoints, n_genes)
        data = np.zeros((self.n_cohorts, self.n_timepoints, self.n_genes))
        
        # Initial state (t=0) - random baseline expression
        # Genes have baseline expression between 0 and 1
        data[:, 0, :] = self.rng.uniform(0, 0.5, size=(self.n_cohorts, self.n_genes))
        
        # W: Adjacency matrix (Source -> Target)
        # We need Target <- Source for multiplication: x_target = W.T @ x_source
        W = self.interaction_matrix.T
        
        # Simulation loop
        for t in range(self.n_timepoints - 1):
            current_state = data[:, t, :] # (Batch, Genes)
            
            # Regulatory input
            regulatory_input = current_state @ W.T # (Batch, Genes)
            
            # Activation function (sigmoid to keep bounded)
            activation = 1 / (1 + np.exp(-regulatory_input))
            
            # Update rule with decay and noise
            # progressive dysregulation could be modeled by drifting parameters, 
            # but here we model it as the natural evolution of the system from a perturbed state 
            # or just the dynamics themselves.
            
            noise = self.rng.normal(0, noise_level, size=(self.n_cohorts, self.n_genes))
            
            next_state = (1 - decay) * current_state + decay * activation + noise
            
            # Clip to biological range [0, 1] (normalized expression)
            next_state = np.clip(next_state, 0, 1)
            
            data[:, t+1, :] = next_state
            
        return data

    def save_data(self, output_dir: Path, data: np.ndarray):
        """
        Saves the generated data and ground truth.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save Ground Truth
        # nx.write_adjacency_matrix is removed in NetworkX 3.0+
        adj_matrix = nx.to_numpy_array(self.ground_truth_graph)
        np.savetxt(output_dir / "ground_truth_adj.txt", adj_matrix)
        
        # Save Interaction Matrix explicitly for easier loading
        np.save(output_dir / "ground_truth_matrix.npy", self.interaction_matrix)
        
        # Save Expression Data (as .npy for efficiency with large cohorts)
        np.save(output_dir / "expression_data.npy", data)
        
        # Also save a sample CSV for inspection (first 5 cohorts)
        for i in range(min(5, self.n_cohorts)):
            df = pd.DataFrame(data[i], columns=[f"Gene_{j}" for j in range(self.n_genes)])
            df.index.name = "Timepoint"
            df.to_csv(output_dir / f"sample_cohort_{i}.csv")
            
        logger.info(f"Saved synthetic data to {output_dir}")

def run_synthesis(output_dir: str = "data/processed/synthetic", 
                 n_genes: int = 50, 
                 n_cohorts: int = 1000):
    gen = SyntheticGenerator(n_genes=n_genes, n_cohorts=n_cohorts)
    gen.generate_ground_truth_grn()
    data = gen.simulate_dynamics()
    gen.save_data(output_dir, data)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_synthesis()
