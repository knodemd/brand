# App icon

The symbol inside the app icon shape, for Apple platforms. For a square logo anywhere else
(profile pictures, directories, press), use `../02 Logo/Symbol/With Background`.


- **Icon Composer/**: the layers of the macOS 26 and iOS 26 icon: indigo `#818CF8`
  `background.svg` and the ink `foreground.svg`. The finished document is `macOS/AppIcon.icon`.
- **iOS/**: full-bleed 1024 px square (the system rounds it).
- **macOS/**: everything the Mac app needs, ready to drop into Xcode:
  - `AppIcon.icon`: the Icon Composer document for macOS 26 and later, with light
    (ink on indigo), dark (indigo on ink) and tinted (paper glyph, tinted by the system)
    appearances. Glass effects stay at their defaults. Xcode 26 builds the older sizes from it.
  - `AppIcon.appiconset`: the classic squircle at every size with its `Contents.json`, for
    an asset catalog or for targets before macOS 26.
  - `AppIcon.icns`, every size as PNG in `PNG/`, the squircle SVGs and a dark variant.
  - `Preview/`: renders of `AppIcon.icon` in each appearance, made with `ictool`.
- **Menu Bar/**: the template image for Knode Service in the menu bar. See its README.
- **Document/**: the `.knode` file icon.
