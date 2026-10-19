import SwiftUI

/// One of the 63 Knode icons, tinted with the foreground style.
public struct KnodeIconView: View {
    public var icon: KnodeIcon

    public init(_ icon: KnodeIcon) { self.icon = icon }

    public var body: some View {
        KnodeGridShape(rows: icon.rows)
            .fill(.foreground, style: FillStyle(eoFill: true))
            .aspectRatio(1, contentMode: .fit)
            .accessibilityLabel(icon.title)
    }
}

/// The Knode mark: two blocks joined by a bridge, on its 10 x 25 half-cell grid.
public struct KnodeMark: View {
    public init() {}

    public static let rows = KnodeMarkData.rows

    public var body: some View {
        KnodeGridShape(rows: Self.rows, radius: 1)
            .fill(.foreground)
            .aspectRatio(CGFloat(Self.rows[0].count) / CGFloat(Self.rows.count), contentMode: .fit)
            .accessibilityLabel("Knode")
    }
}

/// The horizontal logo: the mark at cap height followed by KNODE in Knode Block.
public struct KnodeLogo: View {
    public var markColor: Color
    public var height: CGFloat

    public init(markColor: Color = KnodeColor.indigo, height: CGFloat = 24) {
        self.markColor = markColor
        self.height = height
    }

    public var body: some View {
        HStack(spacing: height * 0.32) {
            KnodeMark().foregroundStyle(markColor).frame(height: height)
            Text("KNODE").font(.knodeBlock(height * 1.4)).fixedSize()
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("Knode")
    }
}

#Preview("Icons") {
    ScrollView {
        LazyVGrid(columns: [GridItem(.adaptive(minimum: 64))], spacing: 16) {
            ForEach(KnodeIcon.allCases, id: \.self) { icon in
                VStack(spacing: 6) {
                    KnodeIconView(icon).frame(width: 28, height: 28)
                    Text(icon.title).font(.caption2).foregroundStyle(.secondary)
                }
            }
        }
        .padding()
    }
    .foregroundStyle(KnodeColor.paper)
    .background(KnodeColor.ink)
}

#Preview("Logo") {
    VStack(spacing: 24) {
        KnodeLogo(height: 32).foregroundStyle(KnodeColor.paper)
        Text("CONNECT YOUR THOUGHTS.").font(.knodeBlock(28)).foregroundStyle(KnodeColor.paper)
        Text("NATURALLY.").font(.knodeBlock(28)).foregroundStyle(KnodeColor.indigo)
        Text("IMPORTED CONVERSATIONS").font(.knodeLine(14)).foregroundStyle(KnodeColor.paper.opacity(0.6))
    }
    .padding(40)
    .background(KnodeColor.ink)
}
