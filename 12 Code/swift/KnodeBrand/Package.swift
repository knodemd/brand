// swift-tools-version: 6.2

import PackageDescription

let package = Package(
    name: "KnodeBrand",
    platforms: [
        .macOS(.v26),
        .iOS(.v26),
    ],
    products: [
        .library(name: "KnodeBrand", targets: ["KnodeBrand"]),
    ],
    targets: [
        .target(name: "KnodeBrand", resources: [.copy("Resources/Fonts")]),
        .testTarget(name: "KnodeBrandTests", dependencies: ["KnodeBrand"]),
    ]
)
