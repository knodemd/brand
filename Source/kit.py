"""Build the complete Knode brand kit from brand.json.

    python3 Source/kit.py            (run from the Brand folder)

Needs Python 3 with fontTools, brotli and Pillow, plus Inkscape (SVG -> PNG/PDF),
Google Chrome (templates and the guidelines PDF) and iconutil (macOS, for .icns).
Every shape comes from engine.py: grid rows become outlines where every corner,
convex or concave, is a quarter arc of half a cell.
"""
import base64
import json
import os
import plistlib
import re
import shutil
import struct
import subprocess
import sys
import urllib.parse

from engine import path_d, polyline

SRC = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(SRC)
STAGE = os.path.join(os.environ.get("TMPDIR", "/tmp"), "knode-kit-stage")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
INKSCAPE = shutil.which("inkscape") or "/opt/homebrew/bin/inkscape"

B = json.load(open(os.path.join(SRC, "brand.json")))
C = B["colors"]
INK, PAPER, INDIGO, GREY = C["ink"], C["paper"], C["indigo"], C["terminalGrey"]
LOGO = B["logo"]["rows"]
LW, LH = len(LOGO[0]), len(LOGO)
LOGO_D = path_d(LOGO, 1.0)

# The kit is laid out the way a brand studio delivers one: identity, system, applications, developers.
D_GUIDE, D_LOGO, D_COLOUR, D_TYPE = "01 Brand Guidelines", "02 Logo", "03 Colour", "04 Typography"
D_ICONS, D_VEC, D_ICON, D_WEB = "05 Icons", "06 Graphic Elements", "07 App Icon", "08 Web"
D_BANNERS, D_TEMPLATES, D_DEV, D_CODE = "09 Banners", "10 Templates", "11 Developers", "12 Code"
D_ICON_APP = D_ICON
D_POSTS = f"{D_TEMPLATES}/Posts & Stories"
D_PATTERNS = f"{D_VEC}/Patterns"
LOGO_FOLDERS = {"Horizontal": "Horizontal", "Stacked": "Stacked", "Mark": "Symbol", "Wordmark": "Wordmark"}

jobs = []          # (svg text, [(relative output path, width or None)])


# ------------------------------------------------------------------ helpers
def out(rel):
    path = os.path.join(KIT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def write(rel, text, mode="w"):
    with open(out(rel), mode) as f:
        f.write(text)


def kebab(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def svg(view, body, w=None, h=None):
    size = f' width="{w}" height="{h}"' if w else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}"{size}>{body}</svg>\n'


def word(text, glyphs, x0=0.0, y0=0.0):
    """A word set in a grid typeface; cap height 5 cells, top of caps at y0."""
    d, x = "", x0
    for ch in text.upper():
        if ch == " ":
            x += 3
            continue
        g = glyphs.get(ch)
        if g:
            d += path_d(g, .5, x, y0 - 2)
            x += len(g[0]) + 1
    return d, x - 1 - x0


def export(svg_text, outputs):
    """Queue an SVG for Inkscape: outputs are (relative path, width) pairs; width None for PDF."""
    jobs.append((svg_text, outputs))


def run_inkscape():
    os.makedirs(STAGE, exist_ok=True)
    lines, moves = [], []
    for n, (text, outputs) in enumerate(jobs):
        src = os.path.join(STAGE, f"j{n}.svg")
        open(src, "w").write(text)
        acts = [f"file-open:{src}"]
        for k, (rel, width) in enumerate(outputs):
            ext = os.path.splitext(rel)[1]
            tmp = os.path.join(STAGE, f"j{n}_{k}{ext}")
            acts += [f"export-filename:{tmp}"] + ([f"export-width:{width}"] if width else []) + ["export-do"]
            moves.append((tmp, out(rel)))
        lines.append("; ".join(acts + ["file-close"]))
    subprocess.run([INKSCAPE, "--shell"], input="\n".join(lines) + "\nquit\n", text=True, capture_output=True, check=False)
    missing = [dst for tmp, dst in moves if not os.path.exists(tmp)]
    for tmp, dst in moves:
        if os.path.exists(tmp):
            shutil.move(tmp, dst)
    if missing:
        sys.exit("inkscape did not produce: " + ", ".join(missing[:5]))


def font_face_css(base):
    """@font-face rules pointing at the kit's font files, relative to `base`."""
    def url(rel):
        return urllib.parse.quote(os.path.relpath(os.path.join(KIT, rel), base))
    faces = [("Knode Block", f"{D_TYPE}/Knode Block/KnodeBlock.woff2", 400), ("Knode Line", f"{D_TYPE}/Knode Line/KnodeLine.woff2", 400)]
    for w, n in [(400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold")]:
        faces.append(("Geist", f"{D_TYPE}/Geist/ttf/Geist-{n}.ttf", w))
        faces.append(("Geist Mono", f"{D_TYPE}/Geist Mono/ttf/GeistMono-{n}.ttf", w))
    return "".join(f'@font-face{{font-family:"{f}";src:url("{url(p)}");font-weight:{w};font-display:block}}\n' for f, p, w in faces)


def chrome(html, png=None, pdf=None, size=None, transparent=False):
    page = os.path.join(STAGE, f"page{len(os.listdir(STAGE)) if os.path.isdir(STAGE) else 0}.html")
    os.makedirs(STAGE, exist_ok=True)
    open(page, "w").write(html)
    args = [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
            "--allow-file-access-from-files", "--virtual-time-budget=4000", "--run-all-compositor-stages-before-draw"]
    if transparent:
        args.append("--default-background-color=00000000")
    if png:
        args += [f"--window-size={size[0]},{size[1]}", f"--screenshot={out(png)}"]
    if pdf:
        args += ["--no-pdf-header-footer", f"--print-to-pdf={out(pdf)}"]
    subprocess.run(args + ["file://" + page], capture_output=True, check=False)


# ------------------------------------------------------------------ 06 typography
def typography():
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    U = 140
    for family, ps, key, folder, file in [("Knode Block", "KnodeBlock-Regular", "block", "Knode Block", "KnodeBlock"),
                                          ("Knode Line", "KnodeLine-Regular", "line", "Knode Line", "KnodeLine")]:
        glyphs = B[key]
        order = [".notdef", "space"] + ["uni%04X" % ord(c) for c in glyphs]
        gl = {".notdef": TTGlyphPen(None).glyph(), "space": TTGlyphPen(None).glyph()}
        mt = {".notdef": (2 * U, 0), "space": (3 * U, 0)}
        cmap = {32: "space"}
        for c, rows in glyphs.items():
            n = "uni%04X" % ord(c)
            pen = TTGlyphPen(None)
            for ring in polyline(rows, .5, 6):
                pts = [(round((x + .5) * U), round((7 - y) * U)) for x, y in reversed(ring)]
                pts = [p for i, p in enumerate(pts) if p != pts[i - 1]]
                pen.moveTo(pts[0])
                for p in pts[1:]:
                    pen.lineTo(p)
                pen.closePath()
            gl[n] = pen.glyph()
            mt[n] = (round((len(rows[0]) + 1) * U), round(.5 * U))
            cmap[ord(c)] = n
            if c.lower() != c:
                cmap[ord(c.lower())] = n
        fb = FontBuilder(1000, isTTF=True)
        fb.setupGlyphOrder(order)
        fb.setupCharacterMap(cmap)
        fb.setupGlyf(gl)
        fb.setupHorizontalMetrics(mt)
        fb.setupHorizontalHeader(ascent=1000, descent=-150)
        fb.setupNameTable({"familyName": family, "styleName": "Regular", "psName": ps, "fullName": f"{family} Regular",
                           "uniqueFontIdentifier": f"knode.md:{ps}", "copyright": "Knode"})
        fb.setupOS2(sTypoAscender=1000, sTypoDescender=-150, usWinAscent=1000, usWinDescent=150, sCapHeight=700, sxHeight=700)
        fb.setupPost()
        fb.save(out(f"{D_TYPE}/{folder}/{file}.ttf"))
        fb.font.flavor = "woff2"
        fb.save(out(f"{D_TYPE}/{folder}/{file}.woff2"))
    geist = os.environ.get("GEIST_DIR")
    if geist:
        for fam in ["Geist", "GeistMono"]:
            dst = "Geist Mono" if fam == "GeistMono" else "Geist"
            for sub in ["ttf", "variable"]:
                d = os.path.join(KIT, D_TYPE, dst, sub)
                shutil.rmtree(d, ignore_errors=True)
                shutil.copytree(os.path.join(geist, fam, sub), d)
            shutil.copy(os.path.join(geist, "OFL.txt"), os.path.join(KIT, D_TYPE, dst, "OFL.txt"))
    write(f"{D_TYPE}/README.md", f"""# Typography

| Role | Typeface | Use |
|---|---|---|
| Display | **Knode Block** | Headlines, big numbers, the wordmark. Uppercase only. 2-cell stroke. |
| Interface | **Knode Line** | Labels, section titles, short UI text. Uppercase only. 1-cell stroke, same weight as the icons. |
| Text | **Geist** 400 to 700 | Everything that is read: body, interface, buttons. In the native apps, the system font. |
| Technical | **Geist Mono** 400 to 600 | File names, codes, data. Leads in Knode Developers. |

Install: double-click each `.ttf` (or select them all and choose *Install* in Font Book).
Web: use `../{D_CODE}/web/fonts.css` or the `.woff2` files.

Scale (desktop): Block 72 · Line 20 · Text 600/40 · Text 500/22 · Text 400/16 · Mono 13.
Knode Block and Knode Line are generated from `Source/brand.json`. Geist and Geist Mono are
by Vercel under the SIL Open Font License (see `OFL.txt` in each folder).
""")


# ------------------------------------------------------------------ 02 logo
COLOURWAYS = {   # name: (mark, text, typical background)
    "Primary": (INDIGO, PAPER, INK),     # indigo K, paper KNODE · on ink and dark backgrounds
    "Ink": (INK, INK, PAPER),            # one colour · on paper, light backgrounds and indigo
    "Paper": (PAPER, PAPER, INK),        # one colour, reversed · on photos and dark backgrounds
}


def logo_svgs(mark, text):
    wd, ww = word("KNODE", B["block"], LW / 2 + 1.6)
    sd, sw = word("KNODE", B["block"])
    mk = f'<path d="{LOGO_D}" fill="{mark}"/>'
    return {
        "Mark": svg(f"0 0 {LW} {LH}", mk),
        "Horizontal": svg(f"0 0 {LW / 2 + 1.6 + ww} 5", f'<g transform="scale(.5)">{mk}</g><path d="{wd}" fill="{text}" fill-rule="evenodd"/>'),
        "Stacked": svg(f"0 0 {sw} 12", f'<g transform="translate({(sw - LW / 2) / 2} 0) scale(.5)">{mk}</g>'
                                         f'<g transform="translate(0 7)"><path d="{sd}" fill="{text}" fill-rule="evenodd"/></g>'),
        "Wordmark": svg(f"0 0 {sw} 5", f'<path d="{sd}" fill="{text}" fill-rule="evenodd"/>'),
    }


def logos():
    BACKS = {"ink": (INK, INDIGO, PAPER), "paper": (PAPER, INK, INK), "indigo": (INDIGO, INK, INK)}   # background, symbol, KNODE
    for cw, (mark, text, _) in COLOURWAYS.items():
        for kind, form in logo_svgs(mark, text).items():
            label = "symbol" if kind == "Mark" else kebab(kind)
            base = f"{D_LOGO}/{LOGO_FOLDERS[kind]}/Transparent"
            name = f"knode-{label}-{kebab(cw)}"
            write(f"{base}/SVG/{name}.svg", form)
            export(form, [(f"{base}/PDF/{name}.pdf", None), (f"{base}/PNG/{name}-1000px.png", 1000), (f"{base}/PNG/{name}-4000px.png", 4000)])
    for bgname, (bg, mark, text) in BACKS.items():
        for kind, form in logo_svgs(mark, text).items():
            label = "symbol" if kind == "Mark" else kebab(kind)
            base = f"{D_LOGO}/{LOGO_FOLDERS[kind]}/With Background"
            vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', form).group(1).split()]
            inner = re.search(r'viewBox="[^"]+">(.*)</svg>', form, re.S).group(1)
            cw, ch = vb[2], vb[3]
            if kind in ("Mark", "Stacked"):
                # square canvas, logo centred: the symbol square doubles as the profile picture
                W = H = 1000
                k = min(W * (0.56 if kind == "Mark" else 0.52) / cw, H * 0.6 / ch)
                sizes = [(f"{n}px", n) for n in (1024, 2048, 4096)]
            else:
                # wide canvas with clear space: the slot width (2.5 letter cells) twice on every side
                pad = 5
                W, H = (cw + 2 * pad) * 100, (ch + 2 * pad) * 100
                k = 100
                sizes = [(f"{n}px", n) for n in (2400, 4800)]
            tx, ty = (W - cw * k) / 2, (H - ch * k) / 2
            placed = svg(f"0 0 {W:g} {H:g}", f'<rect width="{W:g}" height="{H:g}" fill="{bg}"/>'
                                            f'<g transform="translate({tx:.2f} {ty:.2f}) scale({k:.4f})">{inner}</g>')
            name = f"knode-{label}-on-{bgname}"
            write(f"{base}/SVG/{name}.svg", placed)
            export(placed, [(f"{base}/PDF/{name}.pdf", None)] + [(f"{base}/PNG/{name}-{tag}.png", n) for tag, n in sizes])
    write(f"{D_LOGO}/README.md", f"""# Logo

One logo, four forms. Each folder has the same two sub-folders:

- **Transparent** · no background, to place on your own design. Colourways `primary` (indigo
  symbol, paper KNODE, for dark backgrounds), `ink` (for light backgrounds and indigo) and `paper`
  (for photos).
- **With Background** · already placed and centred on ink, paper or indigo, ready to upload.

| Form | What it is | With Background comes as |
|---|---|---|
| `Horizontal` | Symbol + KNODE side by side (combination mark). The primary logo. | wide, with clear space · 2400 and 4800 px |
| `Stacked` | Symbol over KNODE (combination mark). | square · 1024, 2048, 4096 px |
| `Symbol` | The K alone (isotype). | square · 1024, 2048, 4096 px · **this is the profile picture** for any platform |
| `Wordmark` | KNODE alone (logotype). | wide, with clear space · 2400 and 4800 px |

Formats: SVG (master, web, Figma) · PDF (print, Affinity, Illustrator, Keynote) · PNG.

Rules: clear space = the slot width (x) on every side · minimum size: symbol 16 px, horizontal
88 px wide · don't stretch, outline, rotate, recolour outside the three inks, or add effects.
""")


# ------------------------------------------------------------------ 03 app icon
def app_icon():
    s = 1024 * 0.66 / LW
    tx, ty = (1024 - LW * s) / 2, (1024 - LH * s) / 2
    fg = f'<g transform="translate({tx:.2f} {ty:.2f}) scale({s:.4f})"><path d="{LOGO_D}" fill="{INK}"/></g>'
    write(f"{D_ICON_APP}/Icon Composer/foreground.svg", svg("0 0 1024 1024", fg))
    write(f"{D_ICON_APP}/Icon Composer/background.svg", svg("0 0 1024 1024", f'<rect width="1024" height="1024" fill="{INDIGO}"/>'))
    full = svg("0 0 1024 1024", f'<rect width="1024" height="1024" fill="{INDIGO}"/>{fg}')
    write(f"{D_ICON_APP}/knode-app-icon-square.svg", full)
    export(full, [(f"{D_ICON_APP}/iOS/knode-app-icon-ios-1024.png", 1024)])
    # macOS (pre Icon Composer) squircle on the 1024 grid: 824 px body, 100 px margin
    body = 824
    s2 = body * 0.66 / LW
    tx2, ty2 = (1024 - LW * s2) / 2, (1024 - LH * s2) / 2
    mac = svg("0 0 1024 1024", f'<rect x="100" y="100" width="{body}" height="{body}" rx="185" fill="{INDIGO}"/>'
                               f'<g transform="translate({tx2:.2f} {ty2:.2f}) scale({s2:.4f})"><path d="{LOGO_D}" fill="{INK}"/></g>')
    write(f"{D_ICON_APP}/macOS/knode-app-icon-macos.svg", mac)
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    export(mac, [(f"{D_ICON_APP}/macOS/PNG/knode-app-icon-macos-{n}.png", n) for n in sizes])
    dark = svg("0 0 1024 1024", f'<rect x="100" y="100" width="{body}" height="{body}" rx="185" fill="{INK}"/>'
                                f'<g transform="translate({tx2:.2f} {ty2:.2f}) scale({s2:.4f})"><path d="{LOGO_D}" fill="{INDIGO}"/></g>')
    write(f"{D_ICON_APP}/macOS/knode-app-icon-macos-dark.svg", dark)
    export(dark, [(f"{D_ICON_APP}/macOS/PNG/knode-app-icon-macos-dark-1024.png", 1024)])
    # .knode document icon: paper sheet with a folded corner, the mark, and .KNODE in Knode Line
    km = 400 / LW
    td, tw = word(".KNODE", B["line"])
    doc = svg("0 0 1024 1024", f'<path d="M232 100H640L792 252V924H232Z" fill="{PAPER}"/><path d="M640 100V252H792Z" fill="#D9D7E2"/>'
                               f'<g transform="translate({512 - LW * km / 2:.2f} {470 - LH * km / 2:.2f}) scale({km:.4f})"><path d="{LOGO_D}" fill="{INDIGO}"/></g>'
                               f'<g transform="translate({512 - tw * 9 / 2:.2f} 720) scale(9)"><path d="{td}" fill="{INK}" fill-rule="evenodd"/></g>')
    write(f"{D_ICON_APP}/Document/knode-document-icon.svg", doc)
    export(doc, [(f"{D_ICON_APP}/Document/knode-document-icon-512.png", 512), (f"{D_ICON_APP}/Document/knode-document-icon-1024.png", 1024)])
    write(f"{D_ICON_APP}/README.md", f"""# App icon

The symbol inside the app icon shape, for Apple platforms. For a square logo anywhere else
(profile pictures, directories, press), use `../02 Logo/Symbol/With Background`.


- **Icon Composer/** · the source for macOS 26 and iOS 26. In Icon Composer, set the
  background to indigo `{INDIGO}` (or drop in `background.svg`) and add `foreground.svg`
  as the only layer. Leave the glass effects at their defaults.
- **iOS/** · full-bleed 1024 px square (the system rounds it).
- **macOS/** · the classic squircle on the 1024 grid, `AppIcon.icns`, every size as PNG, and a dark variant.
- **Document/** · the `.knode` file icon.
""")


def icns():
    iconset = os.path.join(STAGE, "AppIcon.iconset")
    shutil.rmtree(iconset, ignore_errors=True)
    os.makedirs(iconset)
    png = lambda n: os.path.join(KIT, D_ICON_APP, "macOS", "PNG", f"knode-app-icon-macos-{n}.png")
    for n in [16, 32, 128, 256, 512]:
        shutil.copy(png(n), os.path.join(iconset, f"icon_{n}x{n}.png"))
        shutil.copy(png(n * 2), os.path.join(iconset, f"icon_{n}x{n}@2x.png"))
    subprocess.run(["iconutil", "-c", "icns", iconset, "-o", out(f"{D_ICON_APP}/macOS/AppIcon.icns")], check=True)


# ------------------------------------------------------------------ 04 vectors · alphabet, grid, readme
def glyph_file(c):
    return f"{c}.svg" if c.isalnum() and c.isascii() else f"U+{ord(c):04X}.svg"


def alphabet():
    for folder, key in [("Knode Block", "block"), ("Knode Line", "line")]:
        for c, rows in B[key].items():
            w, h = len(rows[0]), len(rows)
            write(f"{D_VEC}/Alphabet/{folder}/{glyph_file(c)}", svg(f"0 0 {w} {h}", f'<path d="{path_d(rows, .5)}" fill="currentColor" fill-rule="evenodd"/>'))
    lines = "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="{LH}"/>' for x in range(LW + 1)) + "".join(f'<line x1="0" y1="{y}" x2="{LW}" y2="{y}"/>' for y in range(LH + 1))
    cons = svg(f"-1 -1 {LW + 2} {LH + 2}", f'<rect x="-1" y="-1" width="{LW + 2}" height="{LH + 2}" fill="{INK}"/><path d="{LOGO_D}" fill="{INDIGO}"/>'
                                         f'<g stroke="{PAPER}" stroke-opacity=".25" stroke-width=".04">{lines}</g>'
                                         f'<rect width="10" height="10" fill="none" stroke="{PAPER}" stroke-width=".1" stroke-dasharray=".4 .3"/>'
                                         f'<circle cx="1" cy="1" r="1" fill="none" stroke="{INK}" stroke-width=".12"/>')
    write(f"{D_VEC}/Grid/knode-mark-construction.svg", cons)
    export(cons, [(f"{D_VEC}/Grid/knode-mark-construction.png", 2400), (f"{D_VEC}/Grid/knode-mark-construction.pdf", None)])
    rule = svg("-0.5 -0.5 8 6", f'<rect x="-.5" y="-.5" width="8" height="6" fill="{INK}"/><path d="{path_d(["###....", "###....", "#######", "#######", "#######"], .5)}" fill="{INDIGO}"/>'
                                + "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="5" stroke="{PAPER}" stroke-opacity=".3" stroke-width=".03"/>' for x in range(8))
                                + "".join(f'<line x1="0" y1="{y}" x2="7" y2="{y}" stroke="{PAPER}" stroke-opacity=".3" stroke-width=".03"/>' for y in range(6)))
    write(f"{D_VEC}/Grid/knode-radius-rule.svg", rule)
    export(rule, [(f"{D_VEC}/Grid/knode-radius-rule.png", 1600)])
    write(f"{D_VEC}/README.md", """# Graphic elements

The building blocks to design anything new with the system.

- `Patterns/` · node field, cell screen, mark repeat · SVG and PNG.
- `Alphabet/` · every Knode Block and Knode Line character as its own SVG (currentColor);
  punctuation is named by code point (`U+002E.svg` is the full stop).
- `Grid/` · the construction of the mark on its 10 × 25 grid, and the radius rule
  (every corner, convex or concave, is half a cell).

Anything new: draw it on the cell grid, round every corner with half a cell, and it belongs to Knode.
""")


# ------------------------------------------------------------------ 03 icon · favicon & web
def favicon():
    k = B["block"]["K"][2:]                        # the square K of Knode Block (5 x 5)
    tile = svg("0 0 32 32", f'<rect width="32" height="32" rx="7" fill="{INDIGO}"/><g transform="translate(6 6) scale(4)"><path d="{path_d(k, .5)}" fill="{INK}"/></g>')
    write(f"{D_WEB}/favicon.svg", tile)
    export(tile, [(f"{D_WEB}/favicon-16.png", 16), (f"{D_WEB}/favicon-32.png", 32), (f"{D_WEB}/favicon-48.png", 48)])
    full = svg("0 0 180 180", f'<rect width="180" height="180" fill="{INDIGO}"/><g transform="translate(40 40) scale(20)"><path d="{path_d(k, .5)}" fill="{INK}"/></g>')
    export(full, [(f"{D_WEB}/apple-touch-icon.png", 180)])
    maskable = svg("0 0 512 512", f'<rect width="512" height="512" fill="{INDIGO}"/><g transform="translate(166 166) scale(36)"><path d="{path_d(k, .5)}" fill="{INK}"/></g>')
    export(maskable, [(f"{D_WEB}/icon-192.png", 192), (f"{D_WEB}/icon-512.png", 512)])
    write(f"{D_WEB}/site.webmanifest", json.dumps({
        "name": "Knode", "short_name": "Knode", "description": B["tagline"], "theme_color": INK, "background_color": INK,
        "display": "standalone", "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
                                           {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]}, indent=2) + "\n")
    write(f"{D_WEB}/README.md", """# Web

`favicon.svg`, `favicon.ico` (16, 32, 48) and PNGs · `apple-touch-icon.png` (180) · `icon-192/512.png`
for installable web apps · `site.webmanifest` · `og-image.png` (the link preview, 1200 × 630) ·
`head.html` with the tags to paste into `<head>`. The favicon uses the square K of Knode Block,
which stays legible at 16 px.
""")
    write(f"{D_WEB}/head.html", f"""<!-- Knode · paste into <head> -->
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="{INK}">
<meta property="og:title" content="Knode">
<meta property="og:description" content="{B['tagline']}">
<meta property="og:image" content="https://{B['domain']}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
""")


def favicon_ico():
    from PIL import Image
    imgs = [Image.open(os.path.join(KIT, D_WEB, f"favicon-{n}.png")).convert("RGBA") for n in (16, 32, 48)]
    imgs[-1].save(out(f"{D_WEB}/favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)], append_images=imgs[:-1])


# ------------------------------------------------------------------ 05 colour
def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def cmyk(h):
    r, g, b = (v / 255 for v in hex_rgb(h))
    k = 1 - max(r, g, b)
    if k >= 1:
        return (0, 0, 0, 100)
    return tuple(round(v * 100) for v in ((1 - r - k) / (1 - k), (1 - g - k) / (1 - k), (1 - b - k) / (1 - k), k))


def hsl(h):
    import colorsys
    r, g, b = (v / 255 for v in hex_rgb(h))
    hh, l, s = colorsys.rgb_to_hls(r, g, b)
    return round(hh * 360), round(s * 100), round(l * 100)


def colour():
    palette = [("Ink", INK, "Main background · text on paper and indigo"), ("Paper", PAPER, "Light background · text on ink"),
               ("Indigo", INDIGO, "Mark, accents, active state · never text on paper"),
               ("Terminal Grey", GREY, "Knode Developers only · secondary text in the terminal")]
    # Adobe Swatch Exchange (Affinity, Illustrator, Photoshop, InDesign)
    blocks = b""
    for name, hx, _ in palette:
        nm = (name + "\0").encode("utf-16-be")
        body = struct.pack(">H", len(name) + 1) + nm + b"RGB " + struct.pack(">fff", *(v / 255 for v in hex_rgb(hx))) + struct.pack(">H", 0)
        blocks += struct.pack(">HI", 0x0001, len(body)) + body
    write(f"{D_COLOUR}/Knode.ase", b"ASEF" + struct.pack(">HHI", 1, 0, len(palette)) + blocks, "wb")
    rows = "\n".join(f"| **{n}** | `{hx}` | {', '.join(map(str, hex_rgb(hx)))} | {'%d° %d%% %d%%' % hsl(hx)} | {' '.join(map(str, cmyk(hx)))} | {u} |" for n, hx, u in palette)
    write(f"{D_COLOUR}/README.md", f"""# Colour

Three inks, nothing else: no gradients, no tints, no supporting colours.

| Name | HEX | RGB | HSL | CMYK (approx.) | Use |
|---|---|---|---|---|---|
{rows}

Proportion: ink 60 · paper 30 · indigo 10.

Pairings: indigo on ink 6.6:1 (any size) · paper on ink and ink on paper 17.9:1 (text) ·
ink on indigo 6.6:1 (buttons, mark) · indigo on paper 2.7:1 (large shapes only, never text) ·
paper on indigo: do not use.

Files: `Knode.ase` (Adobe and Affinity), `Knode.clr` (macOS colour picker: copy to
`~/Library/Colors/`), `swatches.png`, and tokens in `../{D_CODE}/`.
CMYK values are a straight conversion; proof them on the press for print.
""")
    sw = "".join(f'<rect x="{i * 400}" y="0" width="400" height="400" fill="{hx}"/>'
                 f'<text x="{i * 400 + 28}" y="340" font-family="Geist Mono, monospace" font-size="26" fill="{PAPER if hx in (INK, GREY) else INK}">{n} {hx}</text>'
                 for i, (n, hx, _) in enumerate(palette))
    write(f"{D_COLOUR}/swatches.svg", svg("0 0 1600 400", sw))
    swift = f"""import AppKit
let list = NSColorList(name: "Knode")
{chr(10).join(f'list.setColor(NSColor(srgbRed: {r / 255:.4f}, green: {g / 255:.4f}, blue: {b / 255:.4f}, alpha: 1), forKey: "{n}")' for n, hx, _ in palette for r, g, b in [hex_rgb(hx)])}
try! list.write(to: URL(fileURLWithPath: CommandLine.arguments[1]))
"""
    script = os.path.join(STAGE, "clr.swift")
    os.makedirs(STAGE, exist_ok=True)
    open(script, "w").write(swift)
    subprocess.run(["swift", script, out(f"{D_COLOUR}/Knode.clr")], capture_output=True, check=False)


# ------------------------------------------------------------------ 07 icons
def icons():
    syms, data = [], {}
    for name, rows in B["icons"].items():
        d = path_d(rows, .5)
        k = kebab(name)
        data[name] = rows
        write(f"{D_ICONS}/SVG/{k}.svg", svg("0 0 7 7", f'<path d="{d}" fill="currentColor" fill-rule="evenodd"/>'))
        syms.append(f'<symbol id="knode-{k}" viewBox="0 0 7 7"><path d="{d}" fill-rule="evenodd"/></symbol>')
        for cname, hx in [("Ink", INK), ("Paper", PAPER), ("Indigo", INDIGO)]:
            s = svg("0 0 7 7", f'<path d="{d}" fill="{hx}" fill-rule="evenodd"/>')
            outs = [(f"{D_ICONS}/PNG/{cname}/64/{k}.png", 64), (f"{D_ICONS}/PNG/{cname}/256/{k}.png", 256)]
            if cname == "Ink":
                outs.append((f"{D_ICONS}/PDF/{k}.pdf", None))
            export(s, outs)
    write(f"{D_ICONS}/sprite.svg", '<svg xmlns="http://www.w3.org/2000/svg" style="display:none">' + "".join(syms) + "</svg>\n")
    write(f"{D_ICONS}/icons.json", json.dumps({"grid": "7x7", "radius": "0.5 cell", "categories": B["iconCategories"], "icons": data}, indent=1) + "\n")
    cats = "\n".join(f"- **{c}**: " + ", ".join(ns) for c, ns in B["iconCategories"].items())
    write(f"{D_ICONS}/README.md", f"""# Icons

{len(B["icons"])} icons on a 7 × 7 grid with a one-cell stroke (the weight of Knode Line) and a half-cell
radius on every corner. Fills are kept for the mark and for active states. Import and Export
also cover download and upload.

- `SVG/` · `fill="currentColor"`, so they take the text colour in code and in Figma.
- `PDF/` · ink, vector, for Affinity, Illustrator and Keynote.
- `PNG/` · ink, paper and indigo at 64 and 256 px, transparent.
- `sprite.svg` · every icon as a `<symbol id="knode-…">` for the web.
- `icons.json` · the grid rows, to rebuild them anywhere.

Minimum size 16 px; draw them at multiples of 7 px for crisp edges (14, 21, 28…).

{cats}
""")


# ------------------------------------------------------------------ 05 icons · platform marks
PLATFORMS = os.path.join(SRC, "platforms")


def platforms():
    """Other companies' marks, unmodified, in one colour. Sources: Simple Icons (CC0) or the owner's brand site."""
    rows = []
    for f in sorted(os.listdir(PLATFORMS)):
        if not f.endswith(".svg"):
            continue
        raw = open(os.path.join(PLATFORMS, f)).read()
        title = re.search(r"<title>(.*?)</title>", raw).group(1)
        view = re.search(r'viewBox="([^"]+)"', raw).group(1)
        d = re.search(r'<path d="([^"]+)"', raw).group(1)
        slug = f[:-4]
        write(f"{D_ICONS}/Platforms/SVG/{slug}.svg", svg(view, f'<title>{title}</title><path d="{d}" fill="currentColor"/>'))
        for cname, hx in [("Ink", INK), ("Paper", PAPER), ("Indigo", INDIGO)]:
            export(svg(view, f'<path d="{d}" fill="{hx}"/>'), [(f"{D_ICONS}/Platforms/PNG/{cname}/{n}/{slug}.png", n) for n in (64, 256)])
        rows.append(f"| {title} | `{slug}.svg` |")
    write(f"{D_ICONS}/Platforms/README.md", f"""# Platform marks

Logos of other platforms, for links such as "Follow us on GitHub". They belong to their owners and
are **used as they are**: never redrawn on the Knode grid, recoloured outside one flat colour, or
combined with the Knode logo. Use them only to link to Knode on that platform.

| Platform | File |
|---|---|
{chr(10).join(rows)}

- `SVG/` has `fill="currentColor"`, so each mark takes the colour of the surrounding text.
- `PNG/` has ink, paper and indigo versions at 64 and 256 px.

Source: [Simple Icons](https://simpleicons.org) 16.34.0 (CC0 for the drawings; the trademarks remain
their owners'). Follow each platform's brand guidelines.

**LinkedIn** isn't included: LinkedIn asked Simple Icons to remove it. Download the official mark from
[brand.linkedin.com](https://brand.linkedin.com), save the SVG as `Source/platforms/linkedin.svg`
(with a `<title>LinkedIn</title>`), and run `python3 Source/kit.py platforms inkscape`.

For a generic link to the web, email, a feed, code or a terminal, use the Knode icons Web, Mail,
RSS, Code and Terminal instead.
""")


# ------------------------------------------------------------------ 08 patterns
def coverage_dots(rows, radius, cols):
    """The mark as a screen of dots: sample each cell's coverage of the outline."""
    rings = polyline(rows, radius, 8)
    def inside(x, y):
        c = False
        for ring in rings:
            for i in range(len(ring)):
                (x1, y1), (x2, y2) = ring[i - 1], ring[i]
                if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                    c = not c
        return c
    w, h = len(rows[0]), len(rows)
    step = w / cols
    out_dots = []
    for j in range(int(h / step)):
        for i in range(cols):
            n = sum(inside((i + (a + .5) / 4) * step, (j + (b + .5) / 4) * step) for a in range(4) for b in range(4))
            out_dots.append((i, j, n / 16))
    return out_dots, step


def patterns():
    for pname, rows in B["patterns"].items():
        h, w = len(rows), len(rows[0])
        d = path_d(rows, .5)
        for cw, (bg, fg) in {"indigo-on-ink": (INK, INDIGO), "ink-on-indigo": (INDIGO, INK), "ink-on-paper": (PAPER, INK), "transparent-indigo": (None, INDIGO)}.items():
            rect = f'<rect x="-1" y="-1" width="{w + 2}" height="{h + 2}" fill="{bg}"/>' if bg else ""
            s = svg(f"-1 -1 {w + 2} {h + 2}", rect + f'<path d="{d}" fill="{fg}" fill-rule="evenodd"/>')
            name = f"knode-{kebab(pname)}-{cw}"
            write(f"{D_PATTERNS}/{name}.svg", s)
            export(s, [(f"{D_PATTERNS}/PNG/{name}.png", 3000)])
    dots, step = coverage_dots(LOGO, 1.0, 34)
    body = "".join(f'<circle cx="{(i + .5) * step:.3f}" cy="{(j + .5) * step:.3f}" r="{step * .46 * (v ** .5):.3f}" fill="{INDIGO}"/>' for i, j, v in dots if v > .02)
    rows_n = max(j for _, j, _ in dots) + 1
    s = svg(f"0 0 {LW} {rows_n * step}", f'<rect width="{LW}" height="{rows_n * step}" fill="{INK}"/>' + body)
    write(f"{D_PATTERNS}/knode-cell-screen.svg", s)
    export(s, [(f"{D_PATTERNS}/PNG/knode-cell-screen.png", 3000)])
    tile_w, tile_h = LW * 1.25, LH * 1.6
    rep = svg(f"0 0 {tile_w * 4} {tile_h * 4}", f'<rect width="{tile_w * 4}" height="{tile_h * 4}" fill="{INK}"/>' + "".join(
        f'<path transform="translate({x * tile_w + (tile_w / 2 if y % 2 else 0) - tile_w / 4} {y * tile_h + 4})" d="{LOGO_D}" fill="{INDIGO}"/>'
        for y in range(4) for x in range(5)))
    write(f"{D_PATTERNS}/knode-mark-repeat.svg", rep)
    export(rep, [(f"{D_PATTERNS}/PNG/knode-mark-repeat.png", 3000)])
    write(f"{D_PATTERNS}/README.md", """# Patterns

- **Node field** (wide and square) · blocks joined by bridges, the idea of the K multiplied.
  In indigo on ink, ink on indigo, ink on paper, and transparent.
- **Cell screen** · the mark made of round cells.
- **Mark repeat** · the mark on an offset grid.

SVG masters scale to any size; PNGs are 3000 px wide. Use them as backgrounds at full
strength or faded (10 to 20 % opacity) behind type.
""")


# ------------------------------------------------------------------ 09 templates
def h_svg(text, glyphs, size, fill, x=0, y=0):
    """Outlined grid-type line: cap height = `size` px, top-left at (x, y)."""
    d, w = word(text, glyphs)
    k = size / 5
    return f'<g transform="translate({x} {y}) scale({k})"><path d="{d}" fill="{fill}" fill-rule="evenodd"/></g>', w * k


def logo_g(x, y, height, mark, text):
    wd, ww = word("KNODE", B["block"], LW / 2 + 1.6)
    k = height / 5
    return (f'<g transform="translate({x} {y}) scale({k})"><g transform="scale(.5)"><path d="{LOGO_D}" fill="{mark}"/></g>'
            f'<path d="{wd}" fill="{text}" fill-rule="evenodd"/></g>'), (LW / 2 + 1.6 + ww) * k


def field_g(name, x, y, width, fill, opacity):
    rows = B["patterns"][name]
    k = width / len(rows[0])
    return f'<g opacity="{opacity}" transform="translate({x} {y}) scale({k})"><path d="{path_d(rows, .5)}" fill="{fill}" fill-rule="evenodd"/></g>'


def text_el(x, y, s, size, fill, weight=400, family="Geist", width=None, lh=1.4):
    lines = s.split("\n")
    spans = "".join(f'<tspan x="{x}" dy="{0 if i == 0 else size * lh}">{l}</tspan>' for i, l in enumerate(lines))
    return f'<text x="{x}" y="{y}" font-family="{family}, sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}">{spans}</text>'


def headline(lines, size, x, y, fills, gap=1.35):
    parts, cy = [], y
    for line, fill in zip(lines, fills):
        g, _ = h_svg(line, B["block"], size, fill, x, cy)
        parts.append(g)
        cy += size * gap
    return "".join(parts), cy


def templates():
    T = {}
    # social post 1080
    hl, _ = headline(["CONNECT YOUR", "THOUGHTS.", "NATURALLY."], 64, 88, 120, [PAPER, PAPER, INDIGO])
    lg, _ = logo_g(88, 940, 40, INDIGO, PAPER)
    T["post-1080x1080"] = (1080, 1080, f'<rect width="1080" height="1080" fill="{INK}"/>' + field_g("nodeFieldSquare", 380, 380, 760, INDIGO, .16) + hl + lg)
    hl2, _ = headline(["248"], 220, 88, 110, [INK])
    hl3, _ = h_svg("NODES", B["block"], 80, INK, 88, 380)
    lg2, _ = logo_g(88, 940, 40, INK, INK)
    T["post-stat-1080x1080"] = (1080, 1080, f'<rect width="1080" height="1080" fill="{INDIGO}"/>' + hl2 + hl3 +
                                  text_el(88, 620, "Imported from 63 conversations\nin 4 seconds.", 44, INK, 500) + lg2)
    # story 1080 x 1920
    hl, _ = headline(["CONNECT", "YOUR", "THOUGHTS.", "NATURALLY."], 76, 88, 260, [PAPER, PAPER, PAPER, INDIGO])
    lg, _ = logo_g(88, 1740, 52, INDIGO, PAPER)
    T["story-1080x1920"] = (1080, 1920, f'<rect width="1080" height="1920" fill="{INK}"/>' + field_g("nodeFieldSquare", 0, 900, 1080, INDIGO, .16) + hl + lg)
    # open graph 1200 x 630
    hl, _ = headline(["CONNECT YOUR", "THOUGHTS.", "NATURALLY."], 50, 72, 168, [PAPER, PAPER, INDIGO])
    lg, _ = logo_g(72, 72, 44, INDIGO, PAPER)
    T["banner-1200x630"] = (1200, 630, f'<rect width="1200" height="630" fill="{INK}"/>' + field_g("nodeFieldWide", 520, 360, 760, INDIGO, .16) + lg + hl +
                              text_el(72, 540, B["domain"], 26, "#8E8DA8", 500, "Geist Mono"))
    # slides 1920 x 1080
    hl, _ = headline(["CONNECT YOUR", "THOUGHTS.", "NATURALLY."], 120, 120, 300, [PAPER, PAPER, INDIGO])
    lg, _ = logo_g(120, 110, 48, INDIGO, PAPER)
    T["slide-cover-1920x1080"] = (1920, 1080, f'<rect width="1920" height="1080" fill="{INK}"/>' + field_g("nodeFieldWide", 0, 850, 1920, INDIGO, .12) + lg + hl)
    sec, _ = h_svg("01 · SECTION", B["line"], 22, INDIGO, 120, 120)
    tl, _ = h_svg("SLIDE TITLE IN KNODE BLOCK", B["block"], 64, PAPER, 120, 200)
    lg, _ = logo_g(1690, 970, 24, INDIGO, PAPER)
    T["slide-content-1920x1080"] = (1920, 1080, f'<rect width="1920" height="1080" fill="{INK}"/>' + sec + tl +
                                    text_el(120, 400, "Body text in Geist 400 at 36 px. Keep lines under\n65 characters and slides to one idea each.", 36, "#C9C8DA") +
                                    text_el(120, 620, "map.knode · 248 nodes · 611 links", 26, "#8E8DA8", 400, "Geist Mono") + lg)
    hl, _ = headline(["THANK YOU."], 120, 120, 420, [INDIGO])
    lg, _ = logo_g(120, 110, 48, INDIGO, PAPER)
    T["slide-end-1920x1080"] = (1920, 1080, f'<rect width="1920" height="1080" fill="{INK}"/>' + lg + hl + text_el(120, 640, B["domain"], 40, PAPER, 500, "Geist Mono"))
    # headers
    lg, _ = logo_g(90, 210, 70, INDIGO, PAPER)
    T["banner-1500x500"] = (1500, 500, f'<rect width="1500" height="500" fill="{INK}"/>' + field_g("nodeFieldWide", 600, -20, 1000, INDIGO, .2) + lg)
    lg, _ = logo_g(560, 168, 60, INDIGO, PAPER)
    T["banner-1584x396"] = (1584, 396, f'<rect width="1584" height="396" fill="{INK}"/>' + field_g("nodeFieldWide", 900, -30, 760, INDIGO, .2) + lg)
    # business card 85 x 55 mm at 12 px per mm
    lg, _ = logo_g(84, 84, 36, INDIGO, PAPER)
    nm, _ = h_svg("ÁNGEL MARTÍN", B["line"], 26, PAPER, 84, 452)
    T["business-card-front-85x55mm"] = (1020, 660, f'<rect width="1020" height="660" fill="{INK}"/>' + lg + nm +
                                        text_el(84, 540, f"hello@{B['domain']} · {B['domain']}", 24, "#8E8DA8", 400, "Geist Mono"))
    T["business-card-back-85x55mm"] = (1020, 660, f'<rect width="1020" height="660" fill="{INDIGO}"/><g transform="translate({510 - LW * 8} {330 - LH * 8}) scale(16)"><path d="{LOGO_D}" fill="{INK}"/></g>')
    lg, lw = logo_g(0, 0, 64, INDIGO, PAPER)
    T["banner-1280x640"] = (1280, 640, f'<rect width="1280" height="640" fill="{INK}"/>' + field_g("nodeFieldWide", 0, 440, 1280, INDIGO, .14)
                                           + f'<g transform="translate({640 - lw / 2:.1f} 200)">{lg}</g>'
                                           + text_el(640, 340, B["tagline"].lower(), 34, "#B9B8CC", 500, "Geist Mono").replace("<text ", '<text text-anchor="middle" '))
    lg, lw = logo_g(0, 0, 96, INDIGO, PAPER)
    T["banner-2560x1440"] = (2560, 1440, f'<rect width="2560" height="1440" fill="{INK}"/>' + field_g("nodeFieldWide", 0, 900, 2560, INDIGO, .12)
                                     + f'<g transform="translate({1280 - lw / 2:.1f} 640)">{lg}</g>')
    GROUP = {"post": D_POSTS, "story": D_POSTS, "banner": D_BANNERS, "slide": f"{D_TEMPLATES}/Presentation",
             "business-card": f"{D_TEMPLATES}/Stationery"}
    for name, (w, h, body) in T.items():
        grp = next(v for k, v in GROUP.items() if name.startswith(k))
        s = svg(f"0 0 {w} {h}", body, w, h)
        write(f"{grp}/SVG/{name}.svg", s)
        html = (f'<!doctype html><meta charset=utf-8><style>{font_face_css(STAGE)}html,body{{margin:0}}svg{{display:block}}'
                + ('@page{size:85mm 55mm;margin:0}@media print{svg{width:85mm;height:55mm}}' if "business-card" in name else "") + f'</style>{s}')
        chrome(html, png=f"{grp}/PNG/{name}.png", size=(w, h))
        if "Stationery" in grp:
            chrome(html, pdf=f"{grp}/PDF/{name}.pdf")
    shutil.copy(os.path.join(KIT, D_BANNERS, "PNG", "banner-1200x630.png"), out(f"{D_WEB}/og-image.png"))
    write(f"{D_BANNERS}/README.md", """# Banners

Wide images with the logo, named by size. Editable SVG and PNG.

| File | Size | Typical use |
|---|---|---|
| banner-1200x630 | 1200 × 630 | Link previews (Open Graph) for the website and shared links |
| banner-1280x640 | 1280 × 640 | Repository social preview |
| banner-1500x500 | 1500 × 500 | Profile header (3:1) |
| banner-1584x396 | 1584 × 396 | Profile and page banner (4:1) |
| banner-2560x1440 | 2560 × 1440 | Channel art; the logo sits inside the central 1546 × 423 safe area |

## Repository Previews

One 1280 × 640 image per repository in the knodemd organisation: the image shown when a link to
the repository is shared. Upload it in the repository's *Settings → General → Social preview*.
To add a repository, add a line to `REPOS` in `Source/kit.py` and run `python3 Source/kit.py repo_previews`.
""")
    write(f"{D_TEMPLATES}/README.md", """# Templates

Editable SVG sources (open in Figma, Affinity or Illustrator) and finished PNGs.
Headlines are outlined Knode Block / Knode Line so they render anywhere; body copy is live
Geist / Geist Mono text, so install the fonts from `04 Typography` before editing.

| Folder | Template | Size |
|---|---|---|
| `Posts & Stories` | post, post-stat | 1080 × 1080 |
| `Posts & Stories` | story | 1080 × 1920 |
| `Presentation` | slide-cover, slide-content, slide-end | 1920 × 1080 |
| `Stationery` | business-card front and back (print PDFs, no bleed) | 85 × 55 mm |

Banners are in `../09 Banners`.

To change a headline, set it in Knode Block in your design tool or regenerate with `Source/kit.py`.
""")


# ------------------------------------------------------------------ 09 banners · repository previews
REPOS = [   # (repository, description) · add a line for every new repository in the knodemd organisation
    ("brand", "The brand kit: logo, colour, type, icons and templates."),
    ("handbook", "How Knode works, and how we build it in public."),
    (".github", "The organisation profile and the files every repository shares."),
]


def repo_previews():
    W, H = 1280, 640
    for repo, desc in REPOS:
        lg, _ = logo_g(80, 72, 34, INDIGO, PAPER)
        title, tw = h_svg(repo.upper(), B["block"], 104, PAPER, 80, 300)
        if tw > W - 160:                                  # long names shrink to fit the margins
            title, tw = h_svg(repo.upper(), B["block"], 104 * (W - 160) / tw, PAPER, 80, 300)
        body = (f'<rect width="{W}" height="{H}" fill="{INK}"/>' + field_g("nodeFieldWide", 0, 470, W, INDIGO, .14) + lg
                + text_el(80, 262, "knodemd /", 30, "#8E8DA8", 500, "Geist Mono") + title
                + text_el(80, 476, desc, 32, "#C9C8DA", 400))
        s = svg(f"0 0 {W} {H}", body, W, H)
        name = f"repo-preview-{kebab(repo) or 'github'}"
        write(f"{D_BANNERS}/Repository Previews/SVG/{name}.svg", s)
        html = f'<!doctype html><meta charset=utf-8><style>{font_face_css(STAGE)}html,body{{margin:0}}svg{{display:block}}</style>{s}'
        chrome(html, png=f"{D_BANNERS}/Repository Previews/PNG/{name}.png", size=(W, H))


# ------------------------------------------------------------------ 10 developers
def developers():
    rows = []
    for y in range(0, LH, 2):
        line = ""
        for x in range(LW):
            a, b = LOGO[y][x] == "#", y + 1 < LH and LOGO[y + 1][x] == "#"
            line += "█" if a and b else "▀" if a else "▄" if b else " "
        rows.append(line.rstrip())
    write(f"{D_DEV}/mark-blocks.txt", "\n".join(rows) + "\n")
    # density ASCII (" .:-=+*#%@") sampled from the vector mark, 60 columns, characters ~0.6 wide
    rings = polyline(LOGO, 1.0, 8)
    def inside(x, y):
        c = False
        for ring in rings:
            for i in range(len(ring)):
                (x1, y1), (x2, y2) = ring[i - 1], ring[i]
                if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                    c = not c
        return c
    ramp, cols = " .:-=+*#%@", 60
    cw = LW / cols
    ch = cw / 0.6
    lines = []
    for j in range(int(LH / ch)):
        l = ""
        for i in range(cols):
            n = sum(inside((i + (a + .5) / 3) * cw, (j + (b + .5) / 3) * ch) for a in range(3) for b in range(3))
            l += ramp[round(n / 9 * 9)]
        lines.append(l.rstrip())
    write(f"{D_DEV}/mark-ascii.txt", "\n".join(lines) + "\n")
    write(f"{D_DEV}/README-header.md", "```\n" + "\n".join(rows) + "\n```\n\n**knode** · connect your thoughts. naturally.\n\n"
          "turns your notes and ai conversations into a map of knowledge. yours, in an open .knode file.\n\n```sh\nbrew install knode\n```\n")
    write(f"{D_DEV}/Terminal Themes/knode.ghostty",
          "# Knode Developers · Ghostty theme\n"
          f"background = {INK[1:].lower()}\nforeground = {PAPER[1:].lower()}\ncursor-color = {INDIGO[1:].lower()}\nselection-background = 2b2f66\n"
          + "".join(f"palette = {i}={c}\n" for i, c in enumerate(["0b0b14", "c9c8da", "818cf8", "f3f2ee", "818cf8", "a5adfb", "c9c8da", "c9c8da",
                                                                    "3a3a58", "f3f2ee", "a5adfb", "f3f2ee", "a5adfb", "c7ccfd", "f3f2ee", "f3f2ee"])))
    def comp(h):
        r, g, b = hex_rgb(h)
        return {"Color Space": "sRGB", "Red Component": r / 255, "Green Component": g / 255, "Blue Component": b / 255, "Alpha Component": 1.0}
    ansi = ["#0B0B14", "#C9C8DA", "#818CF8", "#F3F2EE", "#818CF8", "#A5ADFB", "#C9C8DA", "#C9C8DA",
            "#3A3A58", "#F3F2EE", "#A5ADFB", "#F3F2EE", "#A5ADFB", "#C7CCFD", "#F3F2EE", "#F3F2EE"]
    it = {f"Ansi {i} Color": comp(c) for i, c in enumerate(ansi)}
    it.update({"Background Color": comp(INK), "Foreground Color": comp(PAPER), "Cursor Color": comp(INDIGO),
               "Cursor Text Color": comp(INK), "Selection Color": comp("#2B2F66"), "Selected Text Color": comp(PAPER), "Bold Color": comp(PAPER)})
    with open(out(f"{D_DEV}/Terminal Themes/Knode.itermcolors"), "wb") as f:
        plistlib.dump(it, f)
    write(f"{D_DEV}/README.md", f"""# Knode Developers

The ASCII sub-brand for everything that reads or writes code: CLI, API, MCP, SDKs, docs,
changelog, GitHub. Same mark and inks as Knode, written in characters, with Geist Mono leading.
The full rules are in `../{D_GUIDE}`, section 09.

- `mark-blocks.txt` · the mark in block characters, for READMEs and terminals.
- `mark-ascii.txt` · the mark in density characters (` .:-=+*#%@`).
- `README-header.md` · a ready GitHub README header.
- `Terminal Themes/` · Ghostty (`knode.ghostty`, copy to `~/.config/ghostty/themes/`) and iTerm2.

Output conventions: `[ok]` done (indigo) · `[..]` running (grey) · `[--]` skipped, with a reason ·
` !! ` error (inverted). No green, no red: the brand has three inks.
Characters: density ` .:-=+*#%@`, blocks ` ░▒▓█ ▀▄`, boxes `╭─╮│╰╯├┤┬┴` (always round corners).
""")


# ------------------------------------------------------------------ 11 code
def code():
    tok = {"color": {k: {"$type": "color", "$value": v} for k, v in C.items()},
           "fontFamily": {"display": {"$type": "fontFamily", "$value": "Knode Block"}, "interface": {"$type": "fontFamily", "$value": "Knode Line"},
                          "text": {"$type": "fontFamily", "$value": ["Geist", "system-ui", "sans-serif"]},
                          "mono": {"$type": "fontFamily", "$value": ["Geist Mono", "ui-monospace", "monospace"]}},
           "radius": {"cell": {"$type": "dimension", "$value": "0.5 cell"}},
           "brand": {"tagline": B["tagline"], "domain": B["domain"]}}
    write(f"{D_CODE}/tokens.json", json.dumps(tok, indent=2) + "\n")
    css_vars = "".join(f"  --knode-{kebab(k)}: {v};\n" for k, v in C.items())
    write(f"{D_CODE}/web/tokens.css", ":root {\n" + css_vars +
          '  --knode-font-display: "Knode Block", monospace;\n  --knode-font-interface: "Knode Line", monospace;\n'
          '  --knode-font-text: "Geist", system-ui, sans-serif;\n  --knode-font-mono: "Geist Mono", ui-monospace, monospace;\n}\n')
    shutil.copy(os.path.join(KIT, D_ICONS, "sprite.svg"), out(f"{D_CODE}/web/icons.svg"))
    for f in ["KnodeBlock.woff2", "KnodeLine.woff2"]:
        folder = "Knode Block" if "Block" in f else "Knode Line"
        shutil.copy(os.path.join(KIT, D_TYPE, folder, f), out(f"{D_CODE}/web/fonts/{f}"))
    write(f"{D_CODE}/web/fonts.css", """@font-face { font-family: "Knode Block"; src: url("fonts/KnodeBlock.woff2") format("woff2"); font-display: swap; }
@font-face { font-family: "Knode Line"; src: url("fonts/KnodeLine.woff2") format("woff2"); font-display: swap; }
/* Geist and Geist Mono: https://fonts.google.com/specimen/Geist or the files in 04 Typography */
""")
    write(f"{D_CODE}/web/tailwind-preset.js", f"""// Knode · Tailwind preset: presets: [require("./tailwind-preset")]
module.exports = {{
  theme: {{
    extend: {{
      colors: {{ ink: "{INK}", paper: "{PAPER}", indigo: {{ DEFAULT: "{INDIGO}" }}, "terminal-grey": "{GREY}" }},
      fontFamily: {{
        block: ["Knode Block", "monospace"],
        line: ["Knode Line", "monospace"],
        sans: ["Geist", "system-ui", "sans-serif"],
        mono: ["Geist Mono", "ui-monospace", "monospace"],
      }},
    }},
  }},
}};
""")
    # Swift package: regenerate its data and fonts
    swift_root = os.path.join(KIT, D_CODE, "swift", "KnodeBrand")
    res = os.path.join(swift_root, "Sources", "KnodeBrand", "Resources", "Fonts")
    if os.path.isdir(swift_root):
        os.makedirs(res, exist_ok=True)
        shutil.copy(os.path.join(KIT, D_TYPE, "Knode Block", "KnodeBlock.ttf"), res)
        shutil.copy(os.path.join(KIT, D_TYPE, "Knode Line", "KnodeLine.ttf"), res)
        swift_data(os.path.join(swift_root, "Sources", "KnodeBrand", "Generated", "KnodeData.swift"))
    write(f"{D_CODE}/README.md", """# Code

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
""")


SWIFT_KEYWORDS = {"import", "private", "public", "internal", "default", "repeat", "return", "case", "switch", "in", "is", "as",
                  "var", "let", "func", "class", "struct", "enum", "protocol", "extension", "self", "super", "init", "where",
                  "while", "for", "if", "else", "guard", "do", "try", "catch", "throw", "true", "false", "nil", "break",
                  "continue", "static", "operator", "subscript", "typealias"}


def swift_case(name):
    camel = re.sub(r"[^A-Za-z0-9]", "", name.title())
    camel = camel[0].lower() + camel[1:]
    return f"`{camel}`" if camel in SWIFT_KEYWORDS else camel


def swift_data(path):
    lit = lambda rows: "[" + ", ".join(json.dumps(r) for r in rows) + "]"
    cases = "\n".join(f"    case {swift_case(n)}" for n in B["icons"])
    table = "\n".join(f"        case .{swift_case(n)}: {lit(r)}" for n, r in B["icons"].items())
    names = "\n".join(f"        case .{swift_case(n)}: {json.dumps(n)}" for n in B["icons"])
    cats = ",\n".join(f'        ({json.dumps(c)}, [{", ".join("." + swift_case(n) for n in ns)}])' for c, ns in B["iconCategories"].items())
    open(path, "w").write(f"""// Generated by Source/kit.py from brand.json. Do not edit by hand.

/// The {len(B["icons"])} Knode icons, drawn on a 7 x 7 cell grid with a one-cell stroke.
public enum KnodeIcon: String, CaseIterable, Sendable {{
{cases}

    /// Grid rows, top to bottom; `#` is a filled cell.
    public var rows: [String] {{
        switch self {{
{table}
        }}
    }}

    /// English display name.
    public var title: String {{
        switch self {{
{names}
        }}
    }}

    /// Icons grouped as in the brand guide.
    public static let categories: [(name: String, icons: [KnodeIcon])] = [
{cats}
    ]
}}

enum KnodeMarkData {{
    /// The mark on its half-cell grid (10 rows = 5 letter cells).
    static let rows: [String] = {lit(LOGO)}
}}
""")


# ------------------------------------------------------------------ licences
def legal():
    ofl = open(os.path.join(KIT, D_TYPE, "Geist", "OFL.txt")).read()
    body = ofl[ofl.index("This Font Software is licensed"):]
    for folder in ["Knode Block", "Knode Line"]:
        write(f"{D_TYPE}/{folder}/OFL.txt", "Copyright 2026 The Knode Project Authors (https://knode.md)\n\n" + body)
    write("LICENSE.md", """# Licences

Knode is open source. This brand kit is too, with one distinction: the files are free to use,
the name and logo still identify the project.

| What | Licence |
|---|---|
| Knode Block and Knode Line typefaces (`04 Typography`) | [SIL Open Font License 1.1](04%20Typography/Knode%20Block/OFL.txt) |
| Geist and Geist Mono | SIL Open Font License 1.1, by Vercel (`OFL.txt` in their folders) |
| Everything else: logo files, icons, graphic elements, templates, guidelines | [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/) |
| Code in `12 Code` and `Source` | MIT |

The Knode name and logo are covered by the [trademark policy](TRADEMARK.md): the licences above
cover the files, not permission to present something else as Knode.
""")
    write("TRADEMARK.md", """# Knode trademark policy

Knode is open source; its name and logo signal the official project. Use them freely to talk
about Knode, as long as nobody could think something unofficial comes from the project.

**You can, without asking:**
- use the logo and name to refer to Knode: articles, talks, tutorials, docs, community sites;
- say your project works with Knode, imports `.knode` files or is built on Knode;
- use the logo in community events and integrations, following the brand guidelines.

**Please don't:**
- use the name or logo for a product, fork or service in a way that suggests it is official Knode;
- alter the logo, combine it with your own marks, or use it as your own logo or app icon;
- use "Knode" in your product name (prefer "for Knode" or "works with Knode").

Forks are welcome: rename them and use your own logo.

Questions: oss@knode.md
""")


# ------------------------------------------------------------------ 01 guidelines
def guidelines():
    src = os.path.join(KIT, D_GUIDE, "Knode Brand Guidelines.html")
    if not os.path.exists(src):
        return
    html = open(src).read()
    printable = html.replace("</style>", "@media print{*{-webkit-print-color-adjust:exact;print-color-adjust:exact}.top{position:static!important}"
                                         "section{break-inside:auto}}@page{size:1280px 1800px;margin:0}</style>", 1)
    chrome(printable, pdf=f"{D_GUIDE}/Knode Brand Guidelines.pdf")


if __name__ == "__main__":
    shutil.rmtree(STAGE, ignore_errors=True)
    os.makedirs(STAGE)
    steps = sys.argv[1:] or ["typography", "logos", "app_icon", "favicon", "alphabet", "colour", "icons", "platforms", "patterns", "inkscape",
                             "icns", "favicon_ico", "templates", "repo_previews", "developers", "code", "legal", "guidelines"]
    for step in steps:
        print("·", step, flush=True)
        if step == "inkscape":
            run_inkscape()
        else:
            globals()[step]()
    print("kit written to", KIT)
