# Typography

| Role | Typeface | Use |
|---|---|---|
| Display | **Knode Block** | Headlines, big numbers, the wordmark. Uppercase only. 2-cell stroke. |
| Interface | **Knode Line** | Labels, section titles, short UI text. Uppercase only. 1-cell stroke, same weight as the icons. |
| Text | **Geist** 400 to 700 | Everything that is read: body, interface, buttons. In the native apps, the system font. |
| Technical | **Geist Mono** 400 to 600 | File names, codes, data. Leads in Knode Developers. |

Install: double-click each `.ttf` (or select them all and choose *Install* in Font Book).
Web: use `../12 Code/web/fonts.css` or the `.woff2` files.

Scale (desktop): Block 72, Line 20, Text 600/40, Text 500/22, Text 400/16, Mono 13.
Knode Block and Knode Line are generated from `Source/brand.json` and are reserved: the
[Knode Brand License](../BRAND-LICENSE.md) says where you may use them. Geist and Geist Mono are
by Vercel under the SIL Open Font License (see `OFL.txt` in their folders).
