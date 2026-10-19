import SwiftUI

/// The three inks. Nothing else: no gradients, no supporting colours.
public enum KnodeColor {
    /// #0B0B14, main background, text on paper and indigo.
    public static let ink = Color(red: 11 / 255, green: 11 / 255, blue: 20 / 255)
    /// #F3F2EE, light background, text on ink.
    public static let paper = Color(red: 243 / 255, green: 242 / 255, blue: 238 / 255)
    /// #818CF8, the mark, accents, active state. Never text on paper.
    public static let indigo = Color(red: 129 / 255, green: 140 / 255, blue: 248 / 255)
    /// #6E6D8C, Knode Developers only: secondary text in the terminal.
    public static let terminalGrey = Color(red: 110 / 255, green: 109 / 255, blue: 140 / 255)
}

extension ShapeStyle where Self == Color {
    public static var knodeInk: Color { KnodeColor.ink }
    public static var knodePaper: Color { KnodeColor.paper }
    public static var knodeIndigo: Color { KnodeColor.indigo }
}
