# Code

- `tokens.json` · design tokens (W3C format): colours, typefaces, radius, tagline.
- `web/` · `tokens.css`, `fonts.css` with the Knode woff2 files, `icons.svg` sprite, Tailwind preset.
- `swift/KnodeBrand` · SwiftUI package: colours, Knode Block and Line, and the mark, logo and
  {len(B["icons"])} icons as native shapes. Add it as a local package in Xcode.

```swift
import KnodeBrand

KnodeLogo(height: 24).foregroundStyle(KnodeColor.paper)
KnodeIconView(.node).frame(width: 18, height: 18)
Text("NATURALLY.").font(.knodeBlock(28)).foregroundStyle(.knodeIndigo)
```
