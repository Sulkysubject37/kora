import Foundation
import CoreML

public class BatchExecutor {
    public static func benchmark(runner: InferenceRunner, nGenes: Int, batchSize: Int) -> Double {
        // Warmup
        let dummy = [Float](repeating: 0.5, count: nGenes)
        _ = try? runner.predict(input: dummy)
        
        let start = DispatchTime.now()
        
        for _ in 0..<batchSize {
            // Generate random input per sample to avoid caching effects (though CoreML doesn't cache typically)
            // Generating random floats in Swift is slow, so pre-generating might be better
            // or just use the same dummy for pure inference speed testing
            _ = try? runner.predict(input: dummy)
        }
        
        let end = DispatchTime.now()
        let nanoTime = end.uptimeNanoseconds - start.uptimeNanoseconds
        return Double(nanoTime) / 1_000_000_000.0 // Seconds
    }
}
