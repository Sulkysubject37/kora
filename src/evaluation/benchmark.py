import numpy as np
import coremltools as ct
import time
from typing import Dict, Any, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class InferenceBenchmark:
    """
    Benchmarks GRN inference: CPU (NumPy) vs CoreML.
    """
    
    def __init__(self, model_path: str, operators: Dict[str, Any]):
        self.model_path = model_path
        self.operators = operators
        self.coreml_model = None
        
    def load_coreml(self):
        logger.info(f"Loading CoreML model from {self.model_path}")
        self.coreml_model = ct.models.MLModel(self.model_path)
        
    def run_cpu_inference(self, data: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Runs inference using NumPy (Matrix Multiplication).
        Data: (n_samples, n_genes)
        """
        W = self.operators["weights"] # (Out, In) or (In, Out)? 
        # In distillation: W[idx_v, idx_u] = weight. u->v.
        # u is source (in), v is target (out).
        # So W is (n_genes, n_genes).
        # x is (n_samples, n_genes).
        # y = x @ W.T + b
        
        b = self.operators["bias"]
        activation = self.operators["activation"]
        
        start_time = time.time()
        
        # Linear
        # x shape: (N, G)
        # W shape: (G, G)
        # Result: (N, G)
        z = data @ W.T + b
        
        # Activation
        if activation == "sigmoid":
            y = 1 / (1 + np.exp(-z))
        elif activation == "relu":
            y = np.maximum(0, z)
        else:
            y = z
            
        end_time = time.time()
        return y, end_time - start_time
        
    def run_coreml_inference(self, data: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Runs inference using CoreML.
        """
        if self.coreml_model is None:
            self.load_coreml()
            
        n_samples = data.shape[0]
        n_genes = data.shape[1]
        
        # CoreML usually takes dictionaries or individual inputs.
        # Batch prediction is supported in newer versions but depends on model config.
        # Our model was defined with input `expression_t` shape (n_genes,).
        # So it might expect single inputs unless we redefine it for batching.
        
        # For true benchmarking, we should ideally use batch processing if available,
        # but standard looping is the baseline for "simple" usage.
        
        # However, calling predict n_samples times in Python is slow due to overhead.
        # We will time the aggregate.
        
        predictions = []
        start_time = time.time()
        
        for i in range(n_samples):
            input_dict = {"expression_t": data[i]}
            out = self.coreml_model.predict(input_dict)
            
            # Use specific key if available, else first key
            if "expression_t_plus_1" in out:
                predictions.append(out["expression_t_plus_1"])
            else:
                key = list(out.keys())[0]
                predictions.append(out[key])
            
        end_time = time.time()
        
        return np.array(predictions), end_time - start_time

    def compare(self, cpu_out: np.ndarray, coreml_out: np.ndarray):
        """
        Compares numerical consistency.
        """
        mse = np.mean((cpu_out - coreml_out) ** 2)
        max_diff = np.max(np.abs(cpu_out - coreml_out))
        
        logger.info(f"Comparison Results:")
        logger.info(f"MSE: {mse:.6e}")
        logger.info(f"Max Diff: {max_diff:.6e}")
        
        if max_diff > 1e-4:
            logger.warning("Significant numerical divergence detected!")
        else:
            logger.info("Outputs are numerically consistent.")
