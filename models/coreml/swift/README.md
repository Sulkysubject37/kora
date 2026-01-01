# Using KORA CoreML Models in Swift

This directory contains the exported CoreML models for GRN inference.

## Loading the Model

```swift
import CoreML

guard let model = try? KoraGRN(configuration: MLModelConfiguration()) else {
    fatalError("Could not load model")
}
```

## Inference

The model expects an input tensor `expression_t` representing the gene expression levels at time `t`. It predicts the expression at `t+1`.

```swift
let input = KoraGRNInput(expression_t: yourExpressionArray)
guard let output = try? model.prediction(input: input) else {
    fatalError("Prediction failed")
}

let nextState = output.expression_t_plus_1
```
