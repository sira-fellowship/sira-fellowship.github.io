"""Draw the LinkedIn company banner: a soft gradient with a grid of small square dots.

    python3 tools/banner.py [--morse] [out.png]

1128 x 191, rendered at 2x. The gradient runs from a pale sage (the hero painting's sky) at the
top, through the site's cream, to a pale wheat at the bottom. The dots are squares, like the
mark. With --morse, one row of dots spells SIRA in Morse code, repeated across the banner.
No text or logo: LinkedIn shows the page logo over the banner's bottom-left corner.
"""
import pathlib
import sys

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H = 2256, 382
STOPS = [(0.0, (228, 236, 228)), (0.48, (251, 248, 242)), (1.0, (247, 232, 214))]   # sage, cream, wheat
STEP, DOT = 40, 5                     # dot spacing and size, in pixels at 2x
DOT_COLOUR = (34, 49, 61, 46)         # ink at about 18% opacity
MORSE = {"S": "...", "I": "..", "R": ".-.", "A": ".-"}
MORSE_COLOURS = [(95, 138, 108), (201, 162, 39), (184, 80, 47), (62, 103, 135)]   # the mark's colours


def lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def gradient():
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        t = y / (H - 1)
        for (t0, c0), (t1, c1) in zip(STOPS, STOPS[1:]):
            if t0 <= t <= t1:
                c = lerp(c0, c1, (t - t0) / (t1 - t0))
                break
        for x in range(W):
            px[x, y] = c
    return im


def morse_cells():
    """Grid columns for SIRA in Morse: dot = 1 cell, dash = 3, gaps 1 inside a letter, 3 between
    letters, 7 between words. Returns [(column, letter index)]."""
    cells, col = [], 0
    for i, ch in enumerate("SIRA"):
        for j, sym in enumerate(MORSE[ch]):
            n = 1 if sym == "." else 3
            cells += [(col + k, i) for k in range(n)]
            col += n + (1 if j < len(MORSE[ch]) - 1 else 0)
        col += 3
    return cells, col - 3 + 7


def main(out, morse):
    im = gradient().convert("RGBA")
    dots = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(dots)
    cols, rows = range(STEP // 2, W, STEP), range(STEP // 2 - 2, H, STEP)
    special = {}
    if morse:
        cells, period = morse_cells()
        mid = len(rows) // 2
        for rep in range(0, len(cols), period):
            for c, i in cells:
                if rep + c < len(cols):
                    special[(rep + c, mid)] = i
    for ci, x in enumerate(cols):
        for ri, y in enumerate(rows):
            if (ci, ri) in special:
                continue
            d.rectangle([x - DOT // 2, y - DOT // 2, x - DOT // 2 + DOT - 1, y - DOT // 2 + DOT - 1], fill=DOT_COLOUR)
    for (ci, ri), i in special.items():           # Morse cells: a little larger, in the mark's colours
        x, y = cols[ci], rows[ri]
        d.rectangle([x - 5, y - 5, x + 5, y + 5], fill=MORSE_COLOURS[i] + (200,))
        if (ci + 1, ri) in special and special[(ci + 1, ri)] == i:    # join the cells of a dash
            d.rectangle([x, y - 5, cols[ci + 1], y + 5], fill=MORSE_COLOURS[i] + (200,))
    Image.alpha_composite(im, dots).convert("RGB").save(out, optimize=True)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--morse"]
    main(args[0] if args else ROOT / "brand" / "social" / "linkedin-banner-company.png", "--morse" in sys.argv)
