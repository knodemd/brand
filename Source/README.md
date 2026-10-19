# Source

- `brand.json`: the source of truth: grid rows for the mark, Knode Block, Knode Line, the 63 icons and the patterns, plus colours, tagline and domain.
- `engine.py`: turns grid rows into outlines: every corner is a quarter arc of half a cell (one fine cell for the mark, which lives on a half-cell grid).
- `kit.py`: rebuilds the whole kit.
- `playground.html`: the grid editor used to design the system. Open it in a browser; edits stay in that browser, so copy the rows you like into `brand.json`.

## Rebuild

Requirements: Python 3 with `fonttools`, `brotli` and `Pillow`; Inkscape; Google Chrome; macOS (`iconutil`, `swift`).

```sh
pip install fonttools brotli Pillow
brew install --cask inkscape
cd ~/Developer/Knode/Brand
GEIST_DIR=/path/to/geist-font python3 Source/kit.py       # GEIST_DIR only to refresh Geist from a release zip
python3 Source/kit.py templates code                      # or run single steps
cd "12 Code/swift/KnodeBrand" && swift test
```

Steps: typography, logos, app_icon, favicon, alphabet, colour, icons, patterns, inkscape, icns, favicon_ico, templates, developers, code, legal, guidelines.
Steps that queue SVGs (logos, app_icon, favicon, alphabet, icons, patterns) need `inkscape` after them in the same run.
