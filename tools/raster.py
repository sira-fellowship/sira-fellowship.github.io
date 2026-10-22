"""Rasterize a mark or tile SVG from brand/svg/ to a pixel-sharp PNG.

    python3 tools/raster.py <in.svg> <out.png> <size>

The mark is only rectangles, so instead of letting a browser anti-alias edges that fall between
pixels, this snaps every edge to a whole pixel: the PNG has no soft fringe. The image is square;
a mark that isn't square is centred in it on a transparent background.
Used by tools/logo_png.sh for the mark and tile PNGs from 32 px up.
"""
import re
import sys

from PIL import Image, ImageDraw


def hex_rgba(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def main(src, out, size):
    svg = open(src).read()
    vw, vh = map(float, re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).groups())
    s = size / max(vw, vh)
    ox, oy = (size - vw * s) / 2, (size - vh * s) / 2
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    bg = re.search(r'<rect width="[\d.]+" height="[\d.]+" fill="(#[0-9a-fA-F]{6})"', svg)
    if bg:
        d.rectangle([0, 0, size - 1, size - 1], fill=hex_rgba(bg.group(1)))
    # Each rectangle is written as M x y h w v h h -w Z (see tools/logo.py), one path per colour.
    for fill, path in re.findall(r'<path fill="(#[0-9a-fA-F]{6})" d="([^"]+)"', svg):
        for x, y, w, h in re.findall(r"M([\d.\-]+) ([\d.\-]+)h([\d.\-]+)v([\d.\-]+)h[\d.\-]+Z", path):
            x0, y0 = round(ox + float(x) * s), round(oy + float(y) * s)
            x1, y1 = round(ox + (float(x) + float(w)) * s), round(oy + (float(y) + float(h)) * s)
            d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=hex_rgba(fill))
    im.save(out, optimize=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]))
