# Knode Developers

The sub-brand for everything that reads or writes code: CLI, API, MCP, SDKs, docs, changelog,
GitHub and developers.knode.md. It is the Knode brand written in characters: the same mark, the
same three inks, and only Geist Mono. Logos, icons, buttons and links are all text. The full
rules are in `../01 Brand Guidelines`, section 09.

| Folder | What's inside |
|---|---|
| `Logo` | The logotype (symbol and KNODE) at 56, 90, 120 characters wide, the symbol at 22, 44, 60, and the compact lockup |
| `Icons` | All 68 interface icons and 18 platform icons in characters: painted 14 wide, and one character per cell in `Link/` for links; TXT and `icons.json` |
| `Favicon` | The Knode Block K in characters, indigo on ink: SVG, ICO and PNG (16, 32, 180, 192, 512) |
| `Terminal Themes` | Ghostty (`knode.ghostty`, copy to `~/.config/ghostty/themes/`) and iTerm2 |
| `README-header.md` | A ready GitHub README header |

## Which width

- **22 characters:** the smallest symbol that keeps the slot. Headers and the compact lockup.
- **44 to 60:** the symbol on its own, for READMEs, terminals and narrow screens.
- **90 to 120:** the logotype, for heroes and banners. Below 90 the letters stop being legible.

## Rules

- **Characters:** the density ramp `.:-=+*#%@` (light to dark) paints every shape. Boxes use round
  corners: `╭─╮ │ ╰─╯`. No block characters.
- **Type:** Geist Mono for everything, running text included. Lowercase voice.
- **Buttons:** a label inside a round box, `╭──╮ │ label │ ╰──╯`. The primary one is indigo.
- **Links:** text, each with its icon written one character per grid cell (`Icons/Link`).
- **States:** `[ok]` done (indigo), `[..]` running (grey), `[--]` skipped, with a reason, ` !! ` error
  (inverted). No green and no red: the brand has three inks.
- **Handover:** knode.md links here with an ordinary link, "Developers"; this side links back with a
  link in characters, the Back icon and `knode.md`. The two never mix within one piece.
