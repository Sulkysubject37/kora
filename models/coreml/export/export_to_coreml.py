import coremltools as ct
from coremltools.models.neural_network import NeuralNetworkBuilder
import coremltools.models.datatypes as datatypes
import numpy as np
import json
import logging
from pathlib import Path
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TARGET_COHORTS = [
    "GSE269316", "GSE290333", # PD
    "GSE307054", "GSE284339", # ALS
    "GSE79557",  "GSE215241", # FTD
    "GSE312139", "GSE309664", # AD
    "GSE217469", "GSE273501"  # HD
]

def export_cohort(accession):
    logger.info(f"Exporting {accession} to CoreML (Signed Operator)...")
    
    # Paths
    base_dir = Path(f"results/{accession}")
    weights_path = base_dir / "weights" / "trained_weights.npy"
    gene_names_path = base_dir / "weights" / "gene_names.json"
    output_dir = Path(f"models/coreml/{accession}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not weights_path.exists():
        logger.error(f"Weights not found for {accession}")
        return

    # Load Data
    weights = np.load(weights_path) # Shape: (N_genes, N_genes) usually
    with open(gene_names_path, "r") as f:
        gene_names = json.load(f)
        
    n_genes = weights.shape[0]
    
    # Clean weights
    weights = np.nan_to_num(weights, nan=0.0, posinf=0.0, neginf=0.0)
    
    # Decompose Weights
    # Weights W[i, j] = connection from i (source) to j (target)
    # CoreML InnerProduct expects W matrix of shape (C_out, C_in)
    # y = W_coreml * x
    # So we need Transpose of our W.
    
    W_T = weights.T
    W_pos = np.maximum(W_T, 0)
    W_neg = np.abs(np.minimum(W_T, 0))
    
    # Define Inputs/Outputs
    input_features = [("expression", datatypes.Array(n_genes))]
    output_features = [("regulation", datatypes.Array(n_genes))]
    
    # Build Network
    builder = NeuralNetworkBuilder(input_features, output_features)
    
    # Layer 1: Excitatory Path (W_pos * input)
    builder.add_inner_product(
        name="excitation",
        W=W_pos,
        b=None,
        input_channels=n_genes,
        output_channels=n_genes,
        has_bias=False,
        input_name="expression",
        output_name="exc_signal"
    )
    
    # Layer 2: Inhibitory Path (W_neg * input)
    builder.add_inner_product(
        name="inhibition",
        W=W_neg,
        b=None,
        input_channels=n_genes,
        output_channels=n_genes,
        has_bias=False,
        input_name="expression",
        output_name="inh_signal"
    )
    
    # Layer 3: Integration (Excitation - Inhibition)
    builder.add_subtract_broadcastable(
        name="integration",
        input_names=["exc_signal", "inh_signal"],
        output_name="net_input"
    )
    
    # Layer 4: Activation (Tanh)
    builder.add_activation(
        name="dynamics",
        non_linearity="TANH",
        input_name="net_input",
        output_name="regulation"
    )
    
    # Metadata
    builder.set_pre_processing_parameters(
        image_input_names=[],
        is_bgr=False,
        red_bias=0.0,
        green_bias=0.0,
        blue_bias=0.0,
        gray_bias=0.0,
        image_scale=1.0
    )
    
    # Save
    mlmodel_path = output_dir / "grn_operator.mlmodel"
    spec = builder.spec
    
    # FIX: Force EXACT_ARRAY_MAPPING (1)
    # This is a field on the neuralNetwork message, not the feature description
    spec.neuralNetwork.arrayInputShapeMapping = 1 
    
    spec.description.metadata.shortDescription = f"Distilled Rate-Based GRN Operator for {accession}"
    spec.description.metadata.author = "KORA Automaton"
    spec.description.metadata.license = "MIT"
    
    mlmodel = ct.models.MLModel(spec)
    mlmodel.save(str(mlmodel_path))
    
    logger.info(f"Saved model to {mlmodel_path}")
    
    # Validation
    validate_model(mlmodel, weights, n_genes, output_dir)

def validate_model(mlmodel, weights, n_genes, output_dir):
    # Generate random input [0, 1]
    dummy_input = np.random.rand(n_genes).astype(np.float32)
    
    # Python Inference
    # Logic: Tanh( (W_pos @ x) - (W_neg @ x) )
    # x is (N,)
    # W_pos is (N, N) (tranposed logic handled in CoreML)
    
    # Python dot product: np.dot(x, W) where x is (1, N) and W is (N, N)
    # This corresponds to x * W in math notation row vector.
    # W_pos_py = max(W, 0)
    # W_neg_py = abs(min(W, 0))
    # exc = dot(x, W_pos_py)
    # inh = dot(x, W_neg_py)
    # net = exc - inh
    # out = tanh(net)
    
    # Note: Using original signed weights gives same result:
    # net = dot(x, W)
    # out = tanh(net)
    
    linear_out = np.dot(dummy_input, weights)
    python_out = np.tanh(linear_out)
    
    # CoreML Inference
    coreml_input = {"expression": dummy_input}
    coreml_out_dict = mlmodel.predict(coreml_input)
    coreml_out = coreml_out_dict["regulation"]
    
    # Compare
    diff = np.abs(python_out - coreml_out)
    max_diff = np.max(diff)
    
    logger.info(f"Validation Max Diff: {max_diff:.6e}")
    
    with open(output_dir / "python_validation.txt", "w") as f:
        f.write(f"Validation Max Diff: {max_diff}\n")
        f.write("Status: " + ("PASS" if max_diff < 1e-3 else "FAIL") + "\n")
        f.write("\nNote: This model is a rate-based proxy of the trained SNN.")

    # Save Metadata
    with open(output_dir / "metadata.json", "w") as f:
        json.dump({
            "n_genes": n_genes,
            "validation_max_diff": float(max_diff),
            "status": "Ready",
            "operator_type": "Signed Tanh"
        }, f, indent=2)

def main():
    for acc in TARGET_COHORTS:
        export_cohort(acc)

if __name__ == "__main__":
    main()