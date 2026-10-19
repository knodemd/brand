import SwiftUI
#if canImport(AppKit)
import AppKit
#endif

/// The menu bar icon of Knode Service: the Knode icon as an 18 pt template image.
/// macOS tints it to match the menu bar; the paused state is the same glyph, dimmed.
public enum KnodeMenuBarIcon {
    /// Asset names in the package catalog.
    public static let activeName = "MenuBarIcon"
    public static let pausedName = "MenuBarIconPaused"

    /// For `MenuBarExtra` labels and other SwiftUI views.
    public static func image(paused: Bool = false) -> Image {
        Image(paused ? pausedName : activeName, bundle: .module).renderingMode(.template)
    }

    #if canImport(AppKit)
    /// For `NSStatusItem.button?.image`. Marked as a template so AppKit tints it.
    public static func nsImage(paused: Bool = false) -> NSImage? {
        let image = Bundle.module.image(forResource: paused ? pausedName : activeName)
        image?.isTemplate = true
        image?.accessibilityDescription = paused ? "Knode, paused" : "Knode"
        return image
    }
    #endif
}
