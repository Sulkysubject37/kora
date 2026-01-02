import Foundation
import CoreML

// Simple argument parsing
let args = CommandLine.arguments

guard args.count >= 3 else {
    print("Usage: KORAInference <model_path> <n_genes> [batch_size]")
    exit(1)
}

let modelPath = args[1]
let nGenes = Int(args[2]) ?? 5000
let batchSize = args.count > 3 ? Int(args[3]) : 100

print("Loading model from \(modelPath)...")
let url = URL(fileURLWithPath: modelPath)

do {
    let model = try ModelLoader.loadModel(at: url)
    print("Model loaded. Description: \(model.modelDescription.metadata[MLModelMetadataKey.description] ?? "")")
    
    // Check Compute Unit
    let config = MLModelConfiguration()
    // By default it uses all. We can force CPU later for benchmarks.
    
    let runner = InferenceRunner(model: model)
    
    print("Running benchmark (Batch size: \(batchSize), Genes: \(nGenes))...")
    let duration = BatchExecutor.benchmark(runner: runner, nGenes: nGenes, batchSize: batchSize ?? 100)
    
    print("Done.")
    print("Total time: \(String(format: "%.4f", duration))s")
    print("Throughput: \(String(format: "%.2f", Double(batchSize ?? 100) / duration)) samples/s")
    
    // Save minimal result
    let result = ["throughput": Double(batchSize ?? 100) / duration, "latency": duration / Double(batchSize ?? 100)]
    // ... writer implementation later
    
} catch {
    print("Error: \(error)")
    exit(1)
}
