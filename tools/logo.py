"""Draw the SIRA mark from Babbage's punched card and build the SVG logo kit.

    python3 tools/logo.py

The mark is seven bars hanging from a rule. They are the table digits on the sample card
Charles Babbage printed for his Analytical Engine in Passages from the Life of a Philosopher
(1864, p. 121): the number 2303 and its logarithm, 3.3622939. Each digit was punched as that
many holes in a column, so each bar is as long as its column of holes. The script checks that
the card really holds log10(2303) before drawing anything.

Writes brand/svg/: the mark in three colours (plus heavier -small versions for 16-48 px), the
tile in three colourways, the mark beside the name, the mark beside the full name, and the
stacked logo. Text is converted to outlines from Fraunces and Inter Tight (SIL Open Font
License), downloaded to tools/.cache/fonts. Run tools/logo_png.sh afterwards for PNGs and icons.
"""
import math
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

# Babbage's card: the number and its logarithm from the table, as printed.
NUMBER, TABLE = "2303", "3622939"

INK, TERRA, CREAM, NIGHT, GLOW = "#22313d", "#a9532f", "#f7f0e6", "#16222b", "#e39a74"
FONTS = {
    "Fraunces.ttf": "https://github.com/google/fonts/raw/main/ofl/fraunces/Fraunces%5BSOFT,WONK,opsz,wght%5D.ttf",
    "InterTight.ttf": "https://github.com/google/fonts/raw/main/ofl/intertight/InterTight%5Bwght%5D.ttf",
}


def card_digits():
    """The table digits, after checking the card holds log10(2303) to all seven printed places."""
    characteristic = len(NUMBER) - 1
    printed = characteristic + int(TABLE) / 10 ** len(TABLE)
    true = math.log10(int(NUMBER))
    assert abs(true - printed) < 0.5 / 10 ** len(TABLE), f"card says {printed}, log10({NUMBER}) is {true}"
    print(f"Checked Babbage's card: log10({NUMBER}) = {true:.7f}, printed 3.{TABLE}")
    return [int(c) for c in TABLE]


def mark_rects(digits, bar=7.0, gap=4.0, rule=7.0, under=3.0):
    """Seven bars hanging from a rule, proportioned to a square. Returns (size, rects)."""
    w = len(digits) * bar + (len(digits) - 1) * gap
    unit = (w - rule - under) / max(digits)       # one punched hole
    rects = [(0, 0, w, rule)]
    rects += [(i * (bar + gap), rule + under, bar, d * unit) for i, d in enumerate(digits)]
    return w, rects


def rects_path(rects, dx=0.0, dy=0.0, s=1.0):
    return "".join(f"M{dx + x * s:.3f} {dy + y * s:.3f}h{w * s:.3f}v{h * s:.3f}h{-w * s:.3f}Z" for x, y, w, h in rects)


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
    digits = card_digits()
    size, regular = mark_rects(digits)
    size_s, heavy = mark_rects(digits, bar=8.4, gap=2.6, rule=8.0, under=3.0)   # for 16-48 px

    serif = font("Fraunces.ttf", {"opsz": 72, "wght": 500, "SOFT": 0, "WONK": 0})
    sans = font("InterTight.ttf", {"wght": 500})
    word_d, word_w, cap = text_path(serif, "SIRA", 100, tracking=0.03)
    caps_d, caps_w, caps_cap = text_path(sans, "SIRA", 40, tracking=0.6)
    l1_d, l1_w, l_cap = text_path(sans, "Societal Impacts", 38)
    l2_d, l2_w, _ = text_path(sans, "Research on AI", 38)

    files = {}
    # The mark alone, transparent background.
    marks = {"ink": INK, "cream": CREAM, "terracotta": TERRA}
    for name, colour in marks.items():
        files[f"sira-mark-{name}.svg"] = svg(size, size, f'<path fill="{colour}" d="{rects_path(regular)}"/>')
        files[f"sira-mark-{name}-small.svg"] = svg(size_s, size_s, f'<path fill="{colour}" d="{rects_path(heavy)}"/>')

    # The tile: the mark on a solid square, for avatars, app icons, and favicons.
    tiles = {"ink": (INK, CREAM), "cream": (CREAM, INK), "terracotta": (TERRA, CREAM)}
    for name, (bg, fg) in tiles.items():
        for suffix, (sz, rects, pad) in {"": (size, regular, 0.22), "-small": (size_s, heavy, 0.14)}.items():
            s = 140 * (1 - 2 * pad) / sz
            body = f'<rect width="140" height="140" fill="{bg}"/><path fill="{fg}" d="{rects_path(rects, 140 * pad, 140 * pad, s)}"/>'
            files[f"sira-tile-{name}{suffix}.svg"] = svg(140, 140, body)

    # Lockups. colourway: (mark, text, secondary text)
    lockups = {"ink": (INK, INK, "#52606b"), "cream": (CREAM, CREAM, "#d4cec4"), "dark": (GLOW, CREAM, "#aea9a0")}
    for name, (mc, tc, sc) in lockups.items():
        m = cap * 1.32                       # the mark a little taller than the capitals
        gap = m * 0.30
        y_mark = 0
        base = m / 2 + cap / 2
        body = (f'<path fill="{mc}" d="{rects_path(regular, 0, y_mark, m / size)}"/>'
                f'<path transform="translate({m + gap:.1f} {base:.1f})" fill="{tc}" d="{word_d}"/>')
        files[f"sira-logo-horizontal-{name}.svg"] = svg(m + gap + word_w + 4, m, body)

        # Full name: mark, SIRA, a thin rule, then "Societal Impacts / Research on AI".
        x_rule = m + gap + word_w + gap * 0.9
        x_text = x_rule + 2 + gap * 0.9
        lh = l_cap * 1.75
        y1 = m / 2 - lh / 2 + l_cap / 2
        body_full = body + (f'<rect x="{x_rule:.1f}" y="{m * 0.08:.1f}" width="2.4" height="{m * 0.84:.1f}" fill="{sc}" opacity="0.6"/>'
                            f'<path transform="translate({x_text:.1f} {y1:.1f})" fill="{sc}" d="{l1_d}"/>'
                            f'<path transform="translate({x_text:.1f} {y1 + lh:.1f})" fill="{sc}" d="{l2_d}"/>')
        files[f"sira-logo-full-{name}.svg"] = svg(x_text + max(l1_w, l2_w) + 4, m, body_full)

        # Stacked: the mark above SIRA in spaced capitals.
        t = 240
        w = max(t, caps_w) + 40
        body = (f'<path fill="{mc}" d="{rects_path(regular, (w - t) / 2, 0, t / size)}"/>'
                f'<path transform="translate({(w - caps_w) / 2:.1f} {t + 60 + caps_cap:.1f})" fill="{tc}" d="{caps_d}"/>')
        files[f"sira-logo-stacked-{name}.svg"] = svg(w, t + 60 + caps_cap + 6, body)

    OUT.mkdir(parents=True, exist_ok=True)
    for fn, content in files.items():
        (OUT / fn).write_text(content)
    print(f"Wrote {len(files)} SVG files to brand/svg/.")


if __name__ == "__main__":
    main()
