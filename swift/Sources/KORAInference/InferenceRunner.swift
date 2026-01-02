import CoreML
import Foundation

public class InferenceRunner {
    let model: MLModel
    let inputName = "expression"
    let outputName = "regulation"
    
    public init(model: MLModel) {
        self.model = model
    }
    
    public static func load(at path: URL, computeUnit: MLComputeUnits) throws -> InferenceRunner {
        let config = MLModelConfiguration()
        config.computeUnits = computeUnit
        let compiledUrl = try MLModel.compileModel(at: path)
        let model = try MLModel(contentsOf: compiledUrl, configuration: config)
        return InferenceRunner(model: model)
    }
    
    public func predict(input: [Float]) throws -> [Float] {
        // Convert [Float] to MLMultiArray
        let count = input.count
        let inputPointer = UnsafeMutablePointer<Float>.allocate(capacity: count)
        inputPointer.initialize(from: input, count: count)
        
        let mlArray = try MLMultiArray(
            dataPointer: inputPointer,
            shape: [NSNumber(value: count)],
            dataType: .float32,
            strides: [1]
        )
        
        let inputFeature = try MLDictionaryFeatureProvider(dictionary: [inputName: mlArray])
        let outputFeature = try model.prediction(from: inputFeature)
        
        guard let outputArray = outputFeature.featureValue(for: outputName)?.multiArrayValue else {
            throw NSError(domain: "KORA", code: 1, userInfo: [NSLocalizedDescriptionKey: "Output feature not found"])
        }
        
        // Convert back to [Float]
        let outputCount = outputArray.count
        var result = [Float](repeating: 0.0, count: outputCount)
        
        // Efficient copy if contiguous, else iterate
        // CoreML arrays are often not contiguous float pointers directly accessible safely without blocks
        // Using withUnsafeMutableBufferPointer is better
        
        for i in 0..<outputCount {
            result[i] = outputArray[i].floatValue
        }
        
        inputPointer.deallocate()
        return result
    }
}
