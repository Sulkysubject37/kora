import coremltools as ct
import numpy as np
from typing import Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def export_to_coreml(operators: Dict[str, Any], output_path: str, model_name: str = "KoraGRN"):
    """
    Exports distilled operators to CoreML model.
    """
    weights = operators["weights"]
    bias = operators["bias"]
    n_genes = weights.shape[0]
    
    # Define CoreML inputs/outputs
    input_features = [ct.TensorType(name="expression_t", shape=(n_genes,))]
    output_features = [ct.TensorType(name="expression_t_plus_1")]
    
    # We construct a simple linear layer followed by activation
    # However, coremltools is often used to convert from Torch/TF.
    # Building from scratch using MIL (Model Intermediate Language).
    
    from coremltools.converters.mil import Builder as mb
    from coremltools.converters.mil import register_op
    from coremltools.converters.mil.frontend.milproto.load import load as load_mil
    
    @mb.program(input_specs=[mb.TensorSpec(shape=(n_genes,), name="expression_t")])
    def prog(expression_t):
        # Linear projection: Wx + b
        # weights is (out, in)
        # linear expects (out, in) ?? Check MIL docs. 
        # linear(x, weight, bias) -> x @ weight.T + bias usually.
        # If x is (Batch, In), weight is (Out, In). 
        # x @ weight.T -> (Batch, Out).
        
        # Ensure weights are float32
        W = weights.astype(np.float32)
        b = bias.astype(np.float32)
        
        # MIL Linear
        # x: (..., Din)
        # weight: (Dout, Din)
        # bias: (Dout)
        
        # linear layer
        x = mb.linear(x=expression_t, weight=W, bias=b, name="linear_layer")
        
        # Activation
        if operators["activation"] == "sigmoid":
            res = mb.sigmoid(x=x, name="activation")
        elif operators["activation"] == "relu":
            res = mb.relu(x=x, name="activation")
        else:
            res = x # Linear
            
        return res
        
    # Convert MIL program to MLModel
    model = ct.convert(prog, 
                       inputs=input_features, 
                       outputs=output_features,
                       minimum_deployment_target=ct.target.iOS16)
                       
    model.author = "KORA Project"
    model.short_description = "Distilled GRN Inference Model"
    
    # Save
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(output_path))
    
    logger.info(f"Exported CoreML model to {output_path}")
    
if __name__ == "__main__":
    # Test export with dummy data
    logging.basicConfig(level=logging.INFO)
    dummy_ops = {
        "weights": np.eye(10),
        "bias": np.zeros(10),
        "activation": "sigmoid"
    }
    export_to_coreml(dummy_ops, "models/coreml/test_model.mlmodel")
