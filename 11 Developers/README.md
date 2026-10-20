# Knode Developers

Knode written in characters, for places that only have characters: the CLI and its output,
READMEs, changelogs, terminal themes and plain text. It is the same brand, with the same mark and
inks, in Geist Mono. It is not a separate website: developer pages live at knode.md/developers with
the main brand. The full rules are in `../01 Brand Guidelines`, section 09.

| Folder | What's inside |
|---|---|
| `Logo` | The logotype (symbol and KNODE) at 56, 90, 120 characters wide, the symbol at 22, 44, 60, and the compact lockup |
| `Icons` | All 78 interface icons and 18 platform icons in characters: painted 14 wide, and one character per cell in `Link/`; TXT and `icons.json` |
| `Terminal Themes` | Ghostty (`knode.ghostty`, copy to `~/.config/ghostty/themes/`) and iTerm2 |
| `README-header.md` | A ready GitHub README header |

## Which width

- **22 characters:** the smallest symbol that keeps the slot.
- **44 to 60:** the symbol on its own, for READMEs and terminals.
- **90 to 120:** the logotype, for banners in plain text. Below 90 the letters stop being legible.

## Rules

- **Characters:** the density ramp `.:-=+*#%@` (light to dark) paints every shape. Boxes use round
  corners: `╭─╮ │ ╰─╯`. No block characters.
- **Type:** Geist Mono. Normal capitalisation: Knode, GitHub, CLI. Commands, paths and output stay as
  they are typed: `knode import`, `.knode`, `[ok]`.
- **States:** `[ok]` done (indigo), `[..]` running (grey), `[--]` skipped, with a reason, ` !! ` error
  (inverted). No green and no red: the brand has three inks.
