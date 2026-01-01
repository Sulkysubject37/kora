import numpy as np
import logging
from pathlib import Path
from src.evaluation.benchmark import InferenceBenchmark
from src.grn.operators import OperatorDistiller
from models.coreml.export.export_to_coreml import export_to_coreml
import networkx as nx

logger = logging.getLogger(__name__)

def run_benchmark_pipeline():
    logging.basicConfig(level=logging.INFO)
    
    # 1. Setup Dummy Data and Model
    n_genes = 100
    n_samples = 1000
    
    logger.info("Generating random operators...")
    # Random sparse graph
    G = nx.fast_gnp_random_graph(n_genes, 0.1, directed=True)
    # Relabel nodes to "Gene_i"
    mapping = {i: f"Gene_{i}" for i in range(n_genes)}
    G = nx.relabel_nodes(G, mapping)
    
    for u, v in G.edges():
        G[u][v]['weight'] = np.random.uniform(-1, 1)
        
    # Distill
    distiller = OperatorDistiller(activation_fn="sigmoid")
    operators = distiller.distill(G, n_genes)
    
    # Export
    model_path = "models/coreml/benchmark_model.mlpackage"
    export_to_coreml(operators, model_path)
    
    # Generate Test Data
    data = np.random.rand(n_samples, n_genes).astype(np.float32)
    
    # 2. Run Benchmark
    benchmark = InferenceBenchmark(model_path, operators)
    
    logger.info(f"Running CPU inference on {n_samples} samples...")
    cpu_out, cpu_time = benchmark.run_cpu_inference(data)
    logger.info(f"CPU Time: {cpu_time:.4f}s")
    
    logger.info(f"Running CoreML inference on {n_samples} samples...")
    try:
        # Check if we are on Mac, otherwise skip CoreML run to avoid crash if libs missing (though we have requirements)
        import platform
        if platform.system() == "Darwin":
            coreml_out, coreml_time = benchmark.run_coreml_inference(data)
            logger.info(f"CoreML Time: {coreml_time:.4f}s")
            
            # Compare
            benchmark.compare(cpu_out, coreml_out)
        else:
            logger.info("Skipping CoreML run (not on Darwin).")
            
    except Exception as e:
        logger.error(f"CoreML Inference failed: {e}")

if __name__ == "__main__":
    run_benchmark_pipeline()
