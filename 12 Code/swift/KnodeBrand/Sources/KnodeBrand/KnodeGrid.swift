import SwiftUI

/// Turns grid rows into outlines where every corner, convex or concave, is a
/// quarter arc. This is the single rule behind the Knode mark, typefaces and icons.
public enum KnodeGrid {
    struct Point: Hashable {
        var x: Int
        var y: Int
    }

    /// Closed outlines of the filled cells, in cell units. Outer contours run
    /// clockwise on screen and holes run the other way, so either fill rule works.
    static func contours(_ rows: [String]) -> [[Point]] {
        let grid = rows.map { Array($0) }
        let height = grid.count
        let width = grid.map(\.count).max() ?? 0
        func filled(_ x: Int, _ y: Int) -> Bool {
            y >= 0 && y < height && x >= 0 && x < grid[y].count && grid[y][x] == "#"
        }

        var edges: [Point: [Point]] = [:]
        func add(_ a: Point, _ b: Point) { edges[a, default: []].append(b) }
        for y in 0..<height {
            for x in 0..<width where filled(x, y) {
                if !filled(x, y - 1) { add(Point(x: x, y: y), Point(x: x + 1, y: y)) }
                if !filled(x + 1, y) { add(Point(x: x + 1, y: y), Point(x: x + 1, y: y + 1)) }
                if !filled(x, y + 1) { add(Point(x: x + 1, y: y + 1), Point(x: x, y: y + 1)) }
                if !filled(x - 1, y) { add(Point(x: x, y: y + 1), Point(x: x, y: y)) }
            }
        }

        var loops: [[Point]] = []
        while let start = edges.keys.min(by: { ($0.y, $0.x) < ($1.y, $1.x) }) {
            var loop: [Point] = []
            var previous: Point?
            var current = start
            while var next = edges[current], !next.isEmpty {
                var pick = 0
                if next.count > 1, let p = previous {
                    // Cells touching only at a corner stay separate: turn right.
                    let dx = current.x - p.x, dy = current.y - p.y
                    pick = next.firstIndex { $0.x - current.x == -dy && $0.y - current.y == dx } ?? 0
                }
                let step = next.remove(at: pick)
                edges[current] = next.isEmpty ? nil : next
                loop.append(current)
                previous = current
                current = step
                if current == start && edges[start] == nil { break }
            }
            let n = loop.count
            let corners = loop.indices.filter { i in
                let a = loop[(i - 1 + n) % n], p = loop[i], b = loop[(i + 1) % n]
                return (a.x - p.x) * (b.y - p.y) - (a.y - p.y) * (b.x - p.x) != 0
            }.map { loop[$0] }
            if corners.count >= 4 { loops.append(corners) }
        }
        return loops
    }

    /// The outline in cell units, with `radius` (in cells) on every corner.
    public static func path(_ rows: [String], radius: CGFloat = 0.5) -> Path {
        var path = Path()
        for pts in contours(rows) {
            let n = pts.count
            func cg(_ p: Point) -> CGPoint { CGPoint(x: p.x, y: p.y) }
            func cornerRadius(_ i: Int) -> CGFloat {
                let p = pts[(i - 1 + n) % n], v = pts[i], q = pts[(i + 1) % n]
                let l1 = CGFloat(abs(v.x - p.x) + abs(v.y - p.y))
                let l2 = CGFloat(abs(q.x - v.x) + abs(q.y - v.y))
                return min(radius, l1 / 2, l2 / 2)
            }
            // Start just past corner 0, then round every corner in turn.
            let v0 = pts[0], q0 = pts[1 % n]
            let r0 = cornerRadius(0)
            let len0 = CGFloat(abs(q0.x - v0.x) + abs(q0.y - v0.y))
            path.move(to: CGPoint(x: CGFloat(v0.x) + CGFloat(q0.x - v0.x) / len0 * r0,
                                  y: CGFloat(v0.y) + CGFloat(q0.y - v0.y) / len0 * r0))
            for i in 1...n {
                let v = pts[i % n], q = pts[(i + 1) % n]
                path.addArc(tangent1End: cg(v), tangent2End: cg(q), radius: cornerRadius(i % n))
            }
            path.closeSubpath()
        }
        return path
    }
}

/// A grid drawing scaled to fit its frame, centred, keeping square cells.
public struct KnodeGridShape: Shape {
    public var rows: [String]
    public var radius: CGFloat

    public init(rows: [String], radius: CGFloat = 0.5) {
        self.rows = rows
        self.radius = radius
    }

    public func path(in rect: CGRect) -> Path {
        let w = CGFloat(rows.map(\.count).max() ?? 1), h = CGFloat(max(rows.count, 1))
        let s = min(rect.width / w, rect.height / h)
        let transform = CGAffineTransform(translationX: rect.minX + (rect.width - w * s) / 2,
                                          y: rect.minY + (rect.height - h * s) / 2).scaledBy(x: s, y: s)
        return KnodeGrid.path(rows, radius: radius).applying(transform)
    }
}
