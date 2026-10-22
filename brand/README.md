# SIRA logo kit

The mark spells SIRA in International Morse code, one letter per row:

```
S  · · ·
I  · ·
R  · – ·
A  · –
```

It keeps Morse's own timing: a dot is one unit long, a dash three, and the gap between symbols one. The rows sit half a unit apart. Each letter has its own colour. `tools/logo.py` takes the letters from the full ITU Morse alphabet and, after drawing, decodes the rectangles back into text to check that the mark reads SIRA.

The telegraph was one of the first technologies to reshape society in real time, the kind of change SIRA's fellows study.

## Colours

The "soft" palette, one colour per letter:

| Letter | On light | On dark |
|---|---|---|
| S | Sage `#7fae86` | `#a7d0ad` |
| I | Butter `#e0bd4c` | `#f1d97e` |
| R | Salmon `#e98670` | `#f6a896` |
| A | Sky `#6e9cc4` | `#a6c8e6` |

With: ink `#22313d` (text, one-colour mark), cream `#f7f0e6` (page background), night `#16222b` (dark backgrounds and the icon tile). The website keeps terracotta `#a9532f` for buttons and links.

The butter row is the lightest on cream. On white or cream it reads well from about 24 px up; below that, prefer the night tile.

**Stored alternate palettes (not in use):** Van Gogh (sage `#5f8a6c`, wheat `#c9a227`, roof `#b8502f`, slate `#3e6787`, sampled from the hero painting) and blueprint ramp (`#0d2b4a`, `#1d4f80`, `#2f74b5`, `#5a9bd8`). An earlier two-colour scheme, Van Gogh brick `#7e381d` with sage `#4f6b5a`, is also kept for reference.

## Files

| File | What it is |
|---|---|
| `svg/sira-mark-soft.svg` | The mark in colour, for light backgrounds. The default. |
| `svg/sira-mark-soft-dark.svg` | The mark in the lighter colours, for dark backgrounds. |
| `svg/sira-mark-{ink,cream}.svg` | One-colour versions, for print, embossing, and places colour can't go. |
| `svg/sira-tile-night.svg` | The colour mark on a night square: app icons, social avatars, favicons. The default icon. |
| `svg/sira-tile-{cream,ink}.svg` | The mark on cream (in colour) or on ink (in cream). |
| `svg/sira-tile-*-small.svg` | Less padding around the mark, for 16–48 px. |
| `svg/sira-logo-horizontal-{soft,dark,ink,cream}.svg` | The mark beside "SIRA". Default for headers, documents, slides, and email signatures. |
| `svg/sira-logo-full-*.svg` | The mark, "SIRA", and "Societal Impacts Research on AI". First mentions, title slides, letterheads. |
| `svg/sira-logo-stacked-*.svg` | The mark above "SIRA" in spaced capitals. Posters, banners, merch. |
| `png/` | The same as PNGs with transparent backgrounds (tiles are opaque). Marks and tiles have every edge snapped to a whole pixel (`tools/raster.py`), so they are pin-sharp; only the 16 px icons are anti-aliased. Marks and tiles at 512, 1024, and 2048 px; small tiles at 16–512 px; lockups 1600 px wide (stacked 1000). |
| `png/og-image.png` | 1200 × 630 link-preview image, used by the website. |
| `social/linkedin-banner-company.png` | LinkedIn company page banner (1128 × 191, rendered at 2×). Use `png/sira-tile-night-1024.png` as the page logo. |
| `../favicon.ico`, `../favicon.svg`, `../apple-touch-icon.png` | Browser and phone icons used by the website: the night tile. |
| `contact-sheet.png`, `mockups.png` | Every file at a glance, and the logo in use. |

Lockup colourways: `soft` (colour mark, ink text) for light backgrounds, `dark` (light colours, cream text) for dark backgrounds, `ink` and `cream` for one colour. Prefer the SVGs. Text is converted to outlines; the fonts are Fraunces ("SIRA") and Inter Tight (spaced capitals and the full name), both under the SIL Open Font License.

## Guidelines

- Keep the letters in order, one per row, with their colours: the mark has to decode to SIRA.
- Keep the gaps: one unit between dots and dashes, half a unit between rows.
- Use the `-small` tile at 48 px and below. Keep clear space around the mark of at least one dot's height.
- Don't stretch, rotate, outline, or round the mark or the tile (phones round app icons themselves; that's fine), or recolour it outside the palettes above.

## Regenerating

```
pip install -r tools/requirements.txt
python3 tools/logo.py            # SVGs (downloads the fonts to tools/.cache/fonts)
zsh tools/logo_png.sh            # PNGs, link preview, banner, site icons (needs Google Chrome)
python3 tools/contact_sheet.py   # contact-sheet.png and mockups.png
```
