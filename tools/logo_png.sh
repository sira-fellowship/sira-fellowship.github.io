#!/bin/zsh
# Render the PNG exports, icons, link-preview image, and social banner from brand/svg/
# with headless Chrome.
#
#     zsh tools/logo_png.sh
#
# Writes brand/png/, brand/social/, favicon.ico, favicon.svg, and apple-touch-icon.png.
# Needs Google Chrome and Python with Pillow (tools/requirements.txt), and the fonts that
# tools/logo.py downloads to tools/.cache/fonts. Set CHROME to use a different browser binary.
set -e
cd "$(dirname "$0")/.."
ROOT=$PWD
CHROME=${CHROME:-"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"}
PY=${PYTHON:-python3}
SVG=$ROOT/brand/svg
PNG=$ROOT/brand/png
SOCIAL=$ROOT/brand/social
FONTS=$ROOT/tools/.cache/fonts
mkdir -p $PNG $SOCIAL

shot() {  # shot <html file> <out.png> <width> <height> [transparent]
    local bg=""
    [[ -n $5 ]] && bg="--default-background-color=00000000"
    "$CHROME" --headless=new --hide-scrollbars --allow-file-access-from-files $bg --window-size=$3,$4 --screenshot=$2 "file://$1" 2>/dev/null
}
# render <svg> <out.png> <width> <height>: the SVG on a transparent background
render() {
    local html=$(mktemp -t render).html
    print -r -- "<!doctype html><html><body style=\"margin:0;background:transparent;width:${3}px;height:${4}px;display:grid;place-items:center\"><img src=\"file://$1\" style=\"width:${3}px;height:${4}px;object-fit:contain\"></body></html>" > $html
    shot $html $2 $3 $4 transparent
    rm -f $html
}
# height for a given width, from the SVG's viewBox
height() { $PY -c "import re,sys;w,h=map(float,re.search(r'viewBox=\"0 0 ([\d.]+) ([\d.]+)',open(sys.argv[1]).read()).groups());print(round(int(sys.argv[2])*h/w))" $1 $2; }

# Marks and tiles are drawn edge-snapped by tools/raster.py, so they stay sharp at every size.
for c in soft soft-dark ink cream; do
    for s in 512 1024 2048; do $PY tools/raster.py $SVG/sira-mark-$c.svg $PNG/sira-mark-$c-$s.png $s; done
done
for c in night cream ink; do
    for s in 512 1024 2048; do $PY tools/raster.py $SVG/sira-tile-$c.svg $PNG/sira-tile-$c-$s.png $s; done
done
for c in soft dark ink cream; do
    for kind in horizontal full stacked; do
        w=1600; [[ $kind == stacked ]] && w=1000
        render $SVG/sira-logo-$kind-$c.svg $PNG/sira-logo-$kind-$c.png $w $(height $SVG/sira-logo-$kind-$c.svg $w)
    done
done
# Icon sizes. From 32 px up, edge-snapped. At 16 px the half-unit gaps between rows are under a
# pixel, so snapping would merge rows; the browser's smooth rendering keeps them apart there.
for c in night cream; do
    for s in 32 48 180 192 512; do $PY tools/raster.py $SVG/sira-tile-$c-small.svg $PNG/sira-tile-$c-small-$s.png $s; done
    render $SVG/sira-tile-$c-small.svg $PNG/sira-tile-$c-small-16.png 16 16
done

# Shared styles for the link-preview image and the banner: the site's cream, ink, and fonts.
STYLE="@font-face{font-family:Fraunces;src:url('file://$FONTS/Fraunces.ttf')}
@font-face{font-family:InterTight;src:url('file://$FONTS/InterTight.ttf')}
body{margin:0;background:#f7f0e6;color:#22313d;font-family:InterTight,sans-serif;overflow:hidden}
.art{position:absolute;top:0;right:0;height:100%;background:url('file://$ROOT/images/factories-at-asnieres-2000.jpg') 50% 55%/cover;
-webkit-mask-image:linear-gradient(to right,transparent,#000 38%),linear-gradient(to bottom,transparent,#000 10%,#000 90%,transparent);
-webkit-mask-composite:source-in;mask-composite:intersect}"

# Link-preview image (Open Graph), 1200 x 630.
html=$(mktemp -t og).html
print -r -- "<!doctype html><html><head><style>$STYLE
.l{position:absolute;left:76px;top:0;bottom:0;width:560px;display:flex;flex-direction:column;justify-content:center}
.kick{color:#a9532f;font-size:22px;font-weight:500;margin:52px 0 14px}
h1{font:500 72px/1.06 Fraunces,serif;margin:0;letter-spacing:-.01em}
p{font-size:25px;line-height:1.4;color:#52606b;margin:22px 0 0}
.url{position:absolute;left:76px;bottom:52px;font-size:20px;font-weight:500}</style></head><body style=\"width:1200px;height:630px\">
<div class=\"art\" style=\"width:640px\"></div>
<div class=\"l\"><img src=\"file://$SVG/sira-logo-horizontal-soft.svg\" style=\"height:58px;align-self:flex-start\">
<div class=\"kick\">Proposed fellowship &middot; Summer 2027</div><h1>Societal Impacts Research on AI</h1>
<p>A mentored research fellowship giving social scientists a structured path into AI safety.</p></div>
<div class=\"url\">sirafellowship.org</div></body></html>" > $html
shot $html $PNG/og-image.png 1200 630
rm -f $html

# LinkedIn company banner: 1128 x 191, rendered at 2x. LinkedIn places the page's logo over the
# bottom-left corner, so the text starts about a fifth of the way in, clear of it.
html=$(mktemp -t banner).html
print -r -- "<!doctype html><html><head><style>$STYLE
.t{position:absolute;left:430px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center}
h1{font:500 64px/1.1 Fraunces,serif;margin:0}
p{font-size:30px;color:#52606b;margin:14px 0 0}</style></head><body style=\"width:2256px;height:382px\">
<div class=\"art\" style=\"width:760px\"></div>
<div class=\"t\"><h1>Societal Impacts Research on AI</h1><p>A research fellowship for social scientists in AI safety &middot; sirafellowship.org</p></div>
</body></html>" > $html
shot $html $SOCIAL/linkedin-banner-company.png 2256 382
rm -f $html

# Site icons: the night tile with the soft colours reads on light and dark browser tabs and
# phone wallpapers alike, so one version serves everywhere.
cp $SVG/sira-tile-night-small.svg $ROOT/favicon.svg
cp $PNG/sira-tile-night-small-180.png $ROOT/apple-touch-icon.png
$PY - "$PNG" "$ROOT/favicon.ico" <<'PY'
import sys
from PIL import Image
png, out = sys.argv[1], sys.argv[2]
imgs = [Image.open(f"{png}/sira-tile-night-small-{s}.png").convert("RGBA") for s in (16, 32, 48)]
imgs[2].save(out, sizes=[(16, 16), (32, 32), (48, 48)], append_images=imgs[:2])
PY
echo "Rendered PNGs, social images, and icons."
