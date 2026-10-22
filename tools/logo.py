"""Draw the SIRA mark, the name in Morse code, and build the SVG logo kit.

    python3 tools/logo.py

The mark spells SIRA in International Morse code, one letter per row:

    S  · · ·
    I  · ·
    R  · – ·
    A  · –

It uses Morse's own timing: a dot is one unit, a dash three, and the gap between symbols one.
Rows are half a unit apart. Before drawing, the script takes each letter from the full ITU
alphabet, then decodes the drawn rectangles back into text and checks it reads "SIRA".

Each letter has its own colour (the "soft" palette: sage, butter, salmon, sky), with a lighter
set for dark backgrounds and one-colour ink and cream versions for places colour can't go.

Writes brand/svg/: the mark, the tile (the mark on a square, for icons), the mark beside the
name, beside the full name, and stacked above it. Text is converted to outlines from Fraunces
and Inter Tight (SIL Open Font License), downloaded to tools/.cache/fonts. Run
tools/logo_png.sh afterwards for PNGs and icons.
"""
import pathlib
import urllib.request

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "tools" / ".cache"
OUT = ROOT / "brand" / "svg"

NAME = "SIRA"
ITU = {  # International Morse code (ITU-R M.1677-1), letters
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.", "G": "--.", "H": "....",
    "I": "..", "J": ".---", "K": "-.-", "L": ".-..", "M": "--", "N": "-.", "O": "---", "P": ".--.",
    "Q": "--.-", "R": ".-.", "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..",
}
DOT, DASH, GAP, ROW_GAP = 1, 3, 1, 0.5

INK, CREAM, NIGHT = "#22313d", "#f7f0e6", "#16222b"
SOFT = ["#7fae86", "#e0bd4c", "#e98670", "#6e9cc4"]        # sage, butter, salmon, sky (light grounds)
SOFT_DARK = ["#a7d0ad", "#f1d97e", "#f6a896", "#a6c8e6"]   # the same, lighter, for dark grounds
FONTS = {
    "Fraunces.ttf": "https://github.com/google/fonts/raw/main/ofl/fraunces/Fraunces%5BSOFT,WONK,opsz,wght%5D.ttf",
    "InterTight.ttf": "https://github.com/google/fonts/raw/main/ofl/intertight/InterTight%5Bwght%5D.ttf",
}


def mark_rects():
    """[(row, x, y, w, h)] in units, one row per letter. Returns (width, height, rects)."""
    rects = []
    for row, letter in enumerate(NAME):
        x = 0
        for sym in ITU[letter]:
            w = DOT if sym == "." else DASH
            rects.append((row, x, row * (1 + ROW_GAP), w, 1))
            x += w + GAP
    width = max(x + w for _, x, _, w, _ in rects)
    height = len(NAME) + (len(NAME) - 1) * ROW_GAP
    return width, height, rects


def decode(rects):
    """Read the drawing back: each row's rectangles left to right, 1 wide = dot, 3 wide = dash."""
    by_row = {}
    for row, x, _, w, _ in rects:
        by_row.setdefault(row, []).append((x, "." if w == DOT else "-"))
    back = {code: letter for letter, code in ITU.items()}
    return "".join(back["".join(s for _, s in sorted(by_row[r]))] for r in sorted(by_row))


def paths(rects, colours, dx=0.0, dy=0.0, s=1.0):
    """One <path> per colour. colours: one per row, or a single colour."""
    groups = {}
    for row, x, y, w, h in rects:
        c = colours[row] if isinstance(colours, list) else colours
        groups.setdefault(c, []).append(f"M{dx + x * s:.3f} {dy + y * s:.3f}h{w * s:.3f}v{h * s:.3f}h{-w * s:.3f}Z")
    return "".join(f'<path fill="{c}" d="{"".join(d)}"/>' for c, d in groups.items())


def font(name, axes):
    path = CACHE / "fonts" / name
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(FONTS[name], path)
    return instantiateVariableFont(TTFont(path), axes)


def text_path(f, text, size, tracking=0.0):
    """Outline text; returns (path d, width, cap height) with the baseline at y=0."""
    cmap, gs, upm = f.getBestCmap(), f.getGlyphSet(), f["head"].unitsPerEm
    s = size / upm
    pen = SVGPathPen(gs)
    x = 0.0
    for ch in text:
        g = cmap[ord(ch)]
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x, 0)))
        x += gs[g].width * s + tracking * size
    x -= tracking * size
    bp = BoundsPen(gs); gs[cmap[ord("H")]].draw(bp)
    return pen.getCommands(), x, bp.bounds[3] * s


def svg(w, h, body, title="SIRA"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}" width="{w:.0f}" height="{h:.0f}">'
            f'<title>{title}</title>{body}</svg>\n')


def main():
    W, H, rects = mark_rects()
    assert decode(rects) == NAME, decode(rects)
    print(f"Checked the mark: it decodes to {decode(rects)} ({' '.join(ITU[c] for c in NAME)})")

    serif = font("Fraunces.ttf", {"opsz": 72, "wght": 500, "SOFT": 0, "WONK": 0})
    sans = font("InterTight.ttf", {"wght": 500})
    word_d, word_w, cap = text_path(serif, NAME, 100, tracking=0.03)
    caps_d, caps_w, caps_cap = text_path(sans, NAME, 40, tracking=0.6)
    l1_d, l1_w, l_cap = text_path(sans, "Societal Impacts", 38)
    l2_d, l2_w, _ = text_path(sans, "Research on AI", 38)

    files = {}
    U = 20  # one Morse unit in the standalone mark files
    marks = {"soft": SOFT, "soft-dark": SOFT_DARK, "ink": INK, "cream": CREAM}
    for name, colours in marks.items():
        files[f"sira-mark-{name}.svg"] = svg(W * U, H * U, paths(rects, colours, s=U))

    # Tiles: the mark centred on a square. -small has less padding, for 16-48 px.
    tiles = {"night": (NIGHT, SOFT_DARK), "cream": (CREAM, SOFT), "ink": (INK, CREAM)}
    for name, (bg, colours) in tiles.items():
        for suffix, pad in {"": 0.2, "-small": 0.1}.items():
            s = 140 * (1 - 2 * pad) / W
            dy = (140 - H * s) / 2
            body = f'<rect width="140" height="140" fill="{bg}"/>' + paths(rects, colours, 140 * pad, dy, s)
            files[f"sira-tile-{name}{suffix}.svg"] = svg(140, 140, body)

    # Lockups. colourway: (mark colours, text, secondary text)
    lockups = {"soft": (SOFT, INK, "#52606b"), "dark": (SOFT_DARK, CREAM, "#aea9a0"),
               "ink": (INK, INK, INK), "cream": (CREAM, CREAM, CREAM)}
    for name, (mc, tc, sc) in lockups.items():
        mh = cap * 1.18                      # the mark a little taller than the capitals
        s = mh / H
        mw = W * s
        gap = mh * 0.42
        base = mh / 2 + cap / 2
        body = paths(rects, mc, 0, 0, s) + f'<path transform="translate({mw + gap:.1f} {base:.1f})" fill="{tc}" d="{word_d}"/>'
        files[f"sira-logo-horizontal-{name}.svg"] = svg(mw + gap + word_w + 4, mh, body)

        x_rule = mw + gap + word_w + gap * 0.8
        x_text = x_rule + 2 + gap * 0.8
        lh = l_cap * 1.75
        y1 = mh / 2 - lh / 2 + l_cap / 2
        body_full = body + (f'<rect x="{x_rule:.1f}" y="{mh * 0.06:.1f}" width="2.4" height="{mh * 0.88:.1f}" fill="{sc}" opacity="0.6"/>'
                            f'<path transform="translate({x_text:.1f} {y1:.1f})" fill="{sc}" d="{l1_d}"/>'
                            f'<path transform="translate({x_text:.1f} {y1 + lh:.1f})" fill="{sc}" d="{l2_d}"/>')
        files[f"sira-logo-full-{name}.svg"] = svg(x_text + max(l1_w, l2_w) + 4, mh, body_full)

        t = 240                              # stacked: mark above SIRA in spaced capitals
        th = t * H / W
        w = max(t, caps_w) + 40
        body = (paths(rects, mc, (w - t) / 2, 0, t / W)
                + f'<path transform="translate({(w - caps_w) / 2:.1f} {th + 56 + caps_cap:.1f})" fill="{tc}" d="{caps_d}"/>')
        files[f"sira-logo-stacked-{name}.svg"] = svg(w, th + 56 + caps_cap + 6, body)

    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    for fn, content in files.items():
        (OUT / fn).write_text(content)
    print(f"Wrote {len(files)} SVG files to brand/svg/.")


if __name__ == "__main__":
    main()
