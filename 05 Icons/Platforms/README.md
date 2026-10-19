# Platform icons

Two sets, for links such as "Follow us on GitHub". Both name platforms that belong to their owners;
use them only to link to Knode on that platform, and never combine them with the Knode logo.

| Set | Use it for |
|---|---|
| `Knode Grid` | Knode's own interfaces: footers, link lists, settings, anywhere they sit next to Knode icons |
| `Official` | Anywhere the platform's own mark is expected or its guidelines ask for it: badges, partner pages, press |

Each set has `SVG/` with `fill="currentColor"`, so the icon takes the colour of the surrounding text,
and `PNG/` in ink, paper and indigo at 64 and 256 px.

## Knode Grid

18 platforms redrawn on the 7 × 7 grid, with the half-cell radius of every Knode icon. Solid
where the platform's mark is solid, so each one is recognised at a glance. `sprite.svg` has them all
as `<symbol id="knode-…">`; `platforms.json` has the grid rows.

| Platform | File |
|---|---|
| GitHub | `github.svg` |
| X | `x.svg` |
| LinkedIn | `linkedin.svg` |
| YouTube | `youtube.svg` |
| Instagram | `instagram.svg` |
| TikTok | `tiktok.svg` |
| Bluesky | `bluesky.svg` |
| Mastodon | `mastodon.svg` |
| Discord | `discord.svg` |
| Reddit | `reddit.svg` |
| Telegram | `telegram.svg` |
| Facebook | `facebook.svg` |
| Twitch | `twitch.svg` |
| Product Hunt | `product-hunt.svg` |
| Hacker News | `hacker-news.svg` |
| Substack | `substack.svg` |
| App Store | `app-store.svg` |
| Apple | `apple.svg` |

## Official

The marks **as they are**: never redrawn, recoloured outside one flat colour, or altered.

| Platform | File |
|---|---|
| Apple | `apple.svg` |
| App Store | `appstore.svg` |
| Bluesky | `bluesky.svg` |
| Discord | `discord.svg` |
| Facebook | `facebook.svg` |
| Figma | `figma.svg` |
| GitHub | `github.svg` |
| Homebrew | `homebrew.svg` |
| Instagram | `instagram.svg` |
| Mastodon | `mastodon.svg` |
| Medium | `medium.svg` |
| npm | `npm.svg` |
| Product Hunt | `producthunt.svg` |
| Reddit | `reddit.svg` |
| Spotify | `spotify.svg` |
| Substack | `substack.svg` |
| Telegram | `telegram.svg` |
| Threads | `threads.svg` |
| TikTok | `tiktok.svg` |
| Twitch | `twitch.svg` |
| WhatsApp | `whatsapp.svg` |
| X | `x.svg` |
| Y Combinator | `ycombinator.svg` |
| YouTube | `youtube.svg` |

Source: [Simple Icons](https://simpleicons.org) 16.34.0 (CC0 for the drawings; the trademarks remain
their owners'). Follow each platform's brand guidelines.

**LinkedIn** has no official mark here: LinkedIn asked Simple Icons to remove it. Download it from
[brand.linkedin.com](https://brand.linkedin.com), save the SVG as `Source/platforms/linkedin.svg`
(with a `<title>LinkedIn</title>`), and run `python3 Source/kit.py platforms inkscape`.

For a generic link to the web, email, a feed, code or a terminal, use the Knode icons Web, Mail,
RSS, Code and Terminal instead.
