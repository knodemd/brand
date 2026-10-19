# Knode · Brand Kit

> **Connect your thoughts. Naturally.** · [knode.md](https://knode.md) · v1.0

Everything needed to design, lay out and build Knode, organised the way a brand studio delivers
it: identity first, then the system, then applications. The kit is public, but the brand is
reserved: see the [licences](LICENSE.md) and the [Knode Brand License](https://github.com/knodemd/brand-license).

Every shape comes from one rule: draw with square cells, and round every corner, convex or
concave, with half a cell.

## Contents

| | Folder | What's inside |
|---|---|---|
| **Identity** | `01 Brand Guidelines` | The complete guide: interactive HTML and a 14-page PDF |
| | `02 Logo` | `Horizontal` · `Stacked` · `Symbol` · `Wordmark`, each with **Transparent** (primary, ink, paper) and **With Background** (placed on ink, paper, indigo) · SVG, PDF, PNG |
| **System** | `03 Colour` | Ink, paper, indigo · `Knode.ase`, `Knode.clr`, HEX / RGB / HSL / CMYK |
| | `04 Typography` | Knode Block, Knode Line, Geist, Geist Mono |
| | `05 Icons` | 68 interface icons (SVG, PDF, PNG, sprite, JSON) and platform icons: 18 on the Knode grid and 24 official marks |
| | `06 Graphic Elements` | Patterns · Alphabet (every letter as SVG) · Grid |
| **Applications** | `07 App Icon` | Icon Composer layers, iOS, macOS `.icns`, `.knode` document icon |
| | `08 Web` | Favicons, touch and app icons, manifest, link preview, `<head>` snippet |
| | `09 Banners` | Wide banners named by size (1200×630, 1280×640, 1500×500, 1584×396, 2560×1440) |
| | `10 Templates` | Posts & stories · presentation slides · stationery |
| **Developers** | `11 Developers` | Knode Developers (ASCII sub-brand): text marks, README header, terminal themes |
| | `12 Code` | Design tokens, CSS, web fonts, icon sprite, Tailwind preset, `KnodeBrand` Swift package |
| | `Source` | `brand.json` (source of truth), the generator, the grid playground |

## Find it fast

| I need… | Go to |
|---|---|
| The logo for a website, README or document | `02 Logo/Horizontal/Transparent` |
| A square logo, ready to upload (profile picture, avatar) | `02 Logo/Symbol/With Background` |
| The logo already placed on a colour | `02 Logo/<form>/With Background` |
| A banner or header image | `09 Banners` |
| A post or story to edit | `10 Templates/Posts & Stories` |
| The app icon | `07 App Icon` |
| Favicons and link previews | `08 Web` |
| An interface icon | `05 Icons` |
| A platform icon to sit next to Knode icons (GitHub, X, YouTube…) | `05 Icons/Platforms/Knode Grid` |
| A platform's official mark, unmodified | `05 Icons/Platforms/Official` |
| The colours for my design app | `03 Colour` |
| The fonts | `04 Typography` |

## The essentials

| | |
|---|---|
| **Logo** | Symbol (the K) + wordmark (KNODE in Knode Block). Clear space: the slot width. Minimum: symbol 16 px, horizontal 88 px wide. |
| **Colour** | Ink `#0B0B14` · Paper `#F3F2EE` · Indigo `#818CF8` · 60 / 30 / 10. Indigo is never text on paper. No gradients. |
| **Type** | Knode Block (display, uppercase) · Knode Line (labels, uppercase) · Geist (text) · Geist Mono (technical). |
| **Icons** | 7 × 7 grid, 1-cell stroke. Fills only for the symbol and active states. Platforms: Knode grid versions in Knode interfaces, official marks unmodified elsewhere. |
| **Voice** | Clear, yours, calm. English first. Short sentences, plain words, no magic. |
| **Developers** | Same logo and inks written in characters, Geist Mono leading. Never mixed with the vector brand in one piece. |

## Start here

1. **Fonts:** open `04 Typography`, select every `.ttf` and choose *Install*.
2. **Colours:** double-click `03 Colour/Knode.ase` (Adobe, Affinity) or copy `Knode.clr` to `~/Library/Colors/`.
3. **Design:** start from the SVGs in `09 Banners` and `10 Templates` (Figma, Affinity, Illustrator) and place logos from `02 Logo`.
4. **Build:** websites use `12 Code/web`; Apple apps add `12 Code/swift/KnodeBrand` as a local Swift package.

## Change anything

Edit `Source/brand.json` (or design in `Source/playground.html` and copy the rows across) and run
the generator; it rebuilds every file in this kit. See [Source/README.md](Source/README.md).
