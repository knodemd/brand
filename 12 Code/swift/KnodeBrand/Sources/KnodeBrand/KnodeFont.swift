import CoreText
import SwiftUI

/// Knode Block (headlines, numbers, brand) and Knode Line (labels, short UI text).
/// Text everywhere else uses the system font in the app and Geist on the web.
public enum KnodeFonts {
    public static let blockName = "KnodeBlock-Regular"
    public static let lineName = "KnodeLine-Regular"

    /// Registers both typefaces for this process. Safe to call many times.
    @discardableResult
    public static func register() -> Bool { registered }

    private static let registered: Bool = {
        for file in ["KnodeBlock", "KnodeLine"] {
            guard let url = Bundle.module.url(forResource: file, withExtension: "ttf", subdirectory: "Fonts") else { return false }
            CTFontManagerRegisterFontsForURL(url as CFURL, .process, nil)
        }
        return isAvailable(blockName) && isAvailable(lineName)
    }()

    static func isAvailable(_ postScriptName: String) -> Bool {
        let font = CTFontCreateWithName(postScriptName as CFString, 12, nil)
        return CTFontCopyPostScriptName(font) as String == postScriptName
    }
}

extension Font {
    /// Knode Block. Uppercase display face with a two-cell stroke.
    public static func knodeBlock(_ size: CGFloat) -> Font {
        KnodeFonts.register()
        return .custom(KnodeFonts.blockName, fixedSize: size)
    }

    /// Knode Line. Same skeleton as Block with the one-cell stroke of the icons.
    public static func knodeLine(_ size: CGFloat) -> Font {
        KnodeFonts.register()
        return .custom(KnodeFonts.lineName, fixedSize: size)
    }
}
