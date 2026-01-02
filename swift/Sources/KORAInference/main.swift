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
    // 1. CPU Benchmark
    print("\n--- CPU Only ---")
    let cpuRunner = try InferenceRunner.load(at: url, computeUnit: .cpuOnly)
    let cpuTime = BatchExecutor.benchmark(runner: cpuRunner, nGenes: nGenes, batchSize: batchSize)
    print("Time: \(String(format: "%.4f", cpuTime))s")
    print("Throughput: \(String(format: "%.2f", Double(batchSize) / cpuTime)) samples/s")
    
    // 2. NPU/All Benchmark
    print("\n--- NPU/All ---")
    let npuRunner = try InferenceRunner.load(at: url, computeUnit: .all)
    let npuTime = BatchExecutor.benchmark(runner: npuRunner, nGenes: nGenes, batchSize: batchSize)
    print("Time: \(String(format: "%.4f", npuTime))s")
    print("Throughput: \(String(format: "%.2f", Double(batchSize) / npuTime)) samples/s")
    
    // CSV Output
    let csv = "device,time,throughput\ncpu,\(cpuTime),\(Double(batchSize)/cpuTime)\nnpu,\(npuTime),\(Double(batchSize)/npuTime)"
    let outputPath = "results/benchmarks/benchmark_\(nGenes).csv"
    // Write to file (simple shell redirect or file manager)
    // For now just print to stdout for capture
    print("\nCSV_RESULT:\n\(csv)")
    
} catch {
    print("Error: \(error)")
    exit(1)
}
