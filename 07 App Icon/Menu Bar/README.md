# Menu bar icon

The icon of Knode Service in the macOS menu bar. It is a template image: black with alpha,
so macOS draws it in the menu bar colour (dark or light, selected or not) by itself.

- 18 x 18 pt. The glyph is the Knode icon on the 7 x 7 grid at 2 pt per
  cell (14 pt), with 2 pt clear on every side and the half-cell radius on every corner. Each cell
  is a whole number of pixels at 1x and 2x, so the edges stay sharp.
- **Active**: `knode-menu-bar`, full black.
- **Paused**: `knode-menu-bar-paused`, the same glyph at 35 % alpha. A dimmed status
  item is how macOS says "off", and keeping the shape means the icon is still found at a glance.

Each state comes as SVG, PDF (vector, 18 pt), PNG at 1x (18 px) and 2x (36 px), and an
Xcode image set with `"template-rendering-intent": "template"`: `MenuBarIcon.imageset` and
`MenuBarIconPaused.imageset`. Drop both into the app's asset catalog, or use the copies in the
`KnodeBrand` Swift package:

```swift
import KnodeBrand

MenuBarExtra { ... } label: { KnodeMenuBarIcon.image(paused: isPaused) }
statusItem.button?.image = KnodeMenuBarIcon.nsImage(paused: isPaused)
```

## Why the Knode icon

The default is the Knode icon, the symbol of the logo redrawn on the 7 x 7 grid. It is the one
shape that says "Knode" at 14 pt, and its solid mass holds up next to the system icons.
`Alternative/` has the Node icon (a ring with four spokes around a dot) with the same states and image sets
(`MenuBarIconNode`). Its one-cell lines are lighter, closer to the weight of SF Symbols, but it
reads as a generic gear or target rather than as Knode.
