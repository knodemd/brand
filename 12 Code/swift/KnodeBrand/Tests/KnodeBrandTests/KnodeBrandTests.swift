import SwiftUI
import Testing
@testable import KnodeBrand

struct KnodeBrandTests {
    @Test func everyIconIsASevenBySevenGrid() {
        #expect(KnodeIcon.allCases.count == 68)
        for icon in KnodeIcon.allCases {
            #expect(icon.rows.count == 7, "\(icon)")
            #expect(icon.rows.allSatisfy { $0.count == 7 }, "\(icon)")
        }
    }

    @Test func categoriesCoverEveryIconOnce() {
        let listed = KnodeIcon.categories.flatMap(\.icons)
        #expect(listed.count == KnodeIcon.allCases.count)
        #expect(Set(listed) == Set(KnodeIcon.allCases))
    }

    @Test func everyIconDrawsInsideItsGrid() {
        for icon in KnodeIcon.allCases {
            let box = KnodeGrid.path(icon.rows).boundingRect
            #expect(!box.isEmpty, "\(icon)")
            let e = 1e-9   // arcs land on the grid edge up to floating-point noise
            #expect(box.minX >= -e && box.minY >= -e && box.maxX <= 7 + e && box.maxY <= 7 + e, "\(icon)")
        }
    }

    @Test func nodeIsFramePortsAndCentreIdea() {
        // Outer outline with four ports, the inner hole, and the centre dot.
        #expect(KnodeGrid.contours(KnodeIcon.node.rows).count == 3)
    }

    @Test func markIsOneShapeFillingItsGrid() {
        #expect(KnodeGrid.contours(KnodeMark.rows).count == 1)
        let box = KnodeGrid.path(KnodeMark.rows, radius: 1).boundingRect
        #expect(abs(box.width - 25) < 0.001 && abs(box.height - 10) < 0.001)
    }

    @Test func radiusNeverExceedsHalfAnEdge() {
        // A single cell becomes a circle of diameter one.
        let box = KnodeGrid.path(["#"], radius: 0.5).boundingRect
        #expect(abs(box.width - 1) < 0.001 && abs(box.height - 1) < 0.001)
    }

    @Test func typefacesRegister() {
        #expect(KnodeFonts.register())
        #expect(KnodeFonts.isAvailable(KnodeFonts.blockName))
        #expect(KnodeFonts.isAvailable(KnodeFonts.lineName))
    }
}
