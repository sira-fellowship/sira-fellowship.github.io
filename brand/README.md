# SIRA logo kit

The mark is seven bars hanging from a rule. It is drawn from a real punched card: the sample card Charles Babbage printed for his Analytical Engine in *Passages from the Life of a Philosopher* (1864, p. 121). The card holds the number 2303 and its logarithm from a table, 3.3622939. Each digit was punched as that many holes in a column, so each bar is as long as its column of holes: 3, 6, 2, 2, 9, 3, 9. The rule is the card's printed header line. `tools/logo.py` checks that the card really holds log₁₀ 2303 before drawing anything.

The card ties together the two things SIRA is about: the machines that started computing, and the century of social change that came with them.

## Colours

| Name | Hex | Use |
|---|---|---|
| Ink | `#22313d` | The mark and text on light backgrounds. The default. |
| Terracotta | `#a9532f` | Accent: buttons, links, rules, the phone icon. Passes contrast for text on cream (4.7:1) and white text on it (5.3:1). |
| Cream | `#f7f0e6` | Page background; the mark on ink. |
| Night | `#16222b` | Dark backgrounds. |
| Glow | `#e39a74` | The mark on dark backgrounds (the site's dark-mode accent). |

**Stored alternate palette (not in use):** Van Gogh brick `#7e381d` with sage `#4f6b5a`, both sampled from the hero painting, *Factories at Asnières* (1887).

## Files

| File | What it is |
|---|---|
| `svg/sira-mark-{ink,cream,terracotta}.svg` | The mark alone on a transparent background. |
| `svg/sira-mark-*-small.svg` | Heavier bars for 16–48 px. |
| `svg/sira-tile-{ink,cream,terracotta}.svg` | The mark on a solid square: social avatars, app icons, stickers. `-small` versions fill more of the tile for favicons. |
| `svg/sira-logo-horizontal-{ink,cream,dark}.svg` | The mark beside "SIRA". Default for headers, documents, slides, and email signatures. |
| `svg/sira-logo-full-{ink,cream,dark}.svg` | The mark, "SIRA", and "Societal Impacts Research on AI". For first mentions, title slides, and letterheads. |
| `svg/sira-logo-stacked-{ink,cream,dark}.svg` | The mark above "SIRA" in spaced capitals. Posters, banners, merch. |
| `png/` | The same as PNGs with transparent backgrounds (tiles are opaque). Marks and tiles have every edge snapped to a whole pixel (`tools/raster.py`), so they are pin-sharp; only the 16 px icons are anti-aliased. Marks and tiles at 512, 1024, and 2048 px; small tiles at 16–512 px; lockups at 1600 px wide (stacked at 1000). |
| `png/og-image.png` | 1200 × 630 link-preview image, used by the website. |
| `social/linkedin-banner-company.png` | LinkedIn company page banner (1128 × 191, rendered at 2×). Use `png/sira-tile-ink-1024.png` as the page logo. |
| `../favicon.ico`, `../favicon.svg` | Browser tab icons: the ink tile, which turns cream in dark mode (SVG only). |
| `../apple-touch-icon.png` | Phone home-screen icon: the terracotta tile, which stays visible on light and dark wallpapers. |
| `contact-sheet.png`, `mockups.png` | Every file at a glance, and the logo in use. |

Colourway names: `ink` for light backgrounds, `cream` for ink backgrounds and photos, `dark` (glow mark, cream text) for dark backgrounds. Prefer the SVGs; they stay sharp at any size. All text is converted to outlines, so the files look the same without the fonts installed. The fonts are Fraunces ("SIRA") and Inter Tight (spaced capitals and the full name), both free under the SIL Open Font License.

## Guidelines

- Use the `-small` files at 48 px and below.
- Keep clear space around the mark of at least the rule's height times three.
- Keep the bars in order and at their lengths: they are the card's digits.
- Don't stretch, rotate, outline, or add effects to the mark, round the tile's corners (phones do this themselves, which is fine), or recolour it outside the colours above.

## Regenerating

```
pip install -r tools/requirements.txt
python3 tools/logo.py        # SVGs (downloads the fonts to tools/.cache/fonts)
zsh tools/logo_png.sh        # PNGs, link preview, banner, site icons (needs Google Chrome)
python3 tools/contact_sheet.py   # contact-sheet.png and mockups.png
```
