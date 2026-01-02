// swift-tools-version:5.5
import PackageDescription

let package = Package(
    name: "KORAInference",
    platforms: [
        .macOS(.v12)
    ],
    products: [
        .executable(name: "KORAInference", targets: ["KORAInference"]),
    ],
    dependencies: [
        // No external dependencies for now, CoreML is built-in
    ],
    targets: [
        .executableTarget(
            name: "KORAInference",
            dependencies: [],
            path: "Sources/KORAInference"
        ),
    ]
)
