import CoreML
import Foundation

public class ModelLoader {
    public static func loadModel(at path: URL) throws -> MLModel {
        let compiledUrl = try MLModel.compileModel(at: path)
        return try MLModel(contentsOf: compiledUrl)
    }
}
