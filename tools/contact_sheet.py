"""Render brand/contact-sheet.png (every logo file) and brand/mockups.png (the logo in use).

    python3 tools/contact_sheet.py

Run after tools/logo.py and tools/logo_png.sh. Needs Google Chrome (set CHROME to override)
and Pillow, and the fonts in tools/.cache/fonts.
"""
import os
import pathlib
import subprocess
import tempfile

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
B = ROOT / "brand"
SVG, PNG, SOCIAL = B / "svg", B / "png", B / "social"
FONTS = ROOT / "tools" / ".cache" / "fonts"
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
INK, TERRA, CREAM, NIGHT = "#22313d", "#a9532f", "#f7f0e6", "#16222b"

STYLE = f"""@font-face{{font-family:Fraunces;src:url('file://{FONTS}/Fraunces.ttf')}}
@font-face{{font-family:InterTight;src:url('file://{FONTS}/InterTight.ttf')}}
body{{margin:0;padding:40px;background:#eceae6;font:15px/1.45 InterTight,sans-serif;color:{INK}}}
h1{{font:500 34px Fraunces,serif;margin:0 0 4px}} .sub{{color:#52606b;margin:0 0 26px}}
h2{{font:500 21px Fraunces,serif;margin:30px 0 12px}} figure{{margin:0}} figcaption{{font-size:12px;color:#52606b;margin-top:6px;word-break:break-all}}"""


def shoot(html, out, width):
    """Screenshot a page at a given width, then trim the empty space below the content."""
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(html)
    subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", "--allow-file-access-from-files",
                    f"--window-size={width},6000", f"--screenshot={out}", f"file://{f.name}"],
                   check=True, stderr=subprocess.DEVNULL)
    os.unlink(f.name)
    im = Image.open(out).convert("RGB")
    px = im.load()
    bg = px[5, im.height - 5]
    bottom = im.height - 1
    while bottom > 0 and all(px[x, bottom] == bg for x in range(0, im.width, 7)):
        bottom -= 1
    im.crop((0, 0, im.width, min(im.height, bottom + 40))).save(out)


def ground(name):
    if "-cream" in name and "tile" not in name:
        return INK
    if "-dark" in name:
        return NIGHT
    return CREAM


def contact_sheet():
    def cell(p, h):
        return (f'<figure><div style="background:{ground(p.name)};padding:18px;height:{h}px;display:flex;align-items:center">'
                f'<img src="file://{p}" style="max-height:{h}px;max-width:100%"></div><figcaption>brand/{p.relative_to(B)}</figcaption></figure>')

    svgs = sorted(SVG.glob("*.svg"))
    marks = "".join(cell(p, 110) for p in svgs if "-mark-" in p.name or "-tile-" in p.name)
    logos = "".join(cell(p, 90) for p in svgs if "-logo-" in p.name)
    pngs = sorted(PNG.glob("*.png"))
    png_list = "".join(f"<li>{p.name} <span>{Image.open(p).size[0]} × {Image.open(p).size[1]}</span></li>" for p in pngs)
    icons = "".join(f'<figure><div style="background:#fff;padding:14px;display:flex;gap:12px;align-items:flex-end">'
                    f'<img src="file://{ROOT / f}" width="{w}"></div><figcaption>{f}</figcaption></figure>'
                    for f, w in [("favicon.svg", 64), ("favicon.ico", 32), ("apple-touch-icon.png", 90)])
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{STYLE}
.grid{{display:grid;grid-template-columns:repeat(6,1fr);gap:14px}} .grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
.icons{{display:flex;gap:16px}} ul{{columns:3;font-size:12px;padding-left:18px}} li span{{color:#7f8a91}}</style></head><body>
<h1>SIRA logo kit</h1><p class="sub">Every file in brand/, on the background it is made for. Mark: Babbage's 1864 card, log₁₀ 2303 = 3.3622939.</p>
<h2>Marks and tiles</h2><div class="grid">{marks}</div>
<h2>Lockups</h2><div class="grid3">{logos}</div>
<h2>Site icons</h2><div class="icons">{icons}</div>
<h2>Link preview and banner</h2><div class="grid3" style="grid-template-columns:1fr 2fr">
<figure><img src="file://{PNG / 'og-image.png'}" style="width:100%"><figcaption>brand/png/og-image.png · 1200 × 630</figcaption></figure>
<figure><img src="file://{SOCIAL / 'linkedin-banner-company.png'}" style="width:100%"><figcaption>brand/social/linkedin-banner-company.png · 2256 × 382 (1128 × 191 at 2×)</figcaption></figure></div>
<h2>PNG exports ({len(pngs)})</h2><ul>{png_list}</ul></body></html>"""
    shoot(html, B / "contact-sheet.png", 1500)


def mockups():
    tile = lambda size, c="ink", small=True: f'<img src="file://{SVG}/sira-tile-{c}{"-small" if small else ""}.svg" width="{size}" height="{size}" style="display:block">'
    logo = lambda h, c="ink", kind="horizontal": f'<img src="file://{SVG}/sira-logo-{kind}-{c}.svg" style="height:{h}px;display:block">'
    mark = lambda h, c="ink": f'<img src="file://{SVG}/sira-mark-{c}.svg" style="height:{h}px;display:block">'
    painting = ROOT / "images" / "factories-at-asnieres-1000.jpg"
    cards = [
        ("Browser tab", f'''<div class="browser"><div class="tabs"><div class="tab on">{tile(16)}<span>SIRA · Societal Impacts Research on AI</span></div>
<div class="tab">Inbox</div></div><div class="url">sirafellowship.org</div>
<div class="page"><div class="pghdr">{logo(26)}<span class="nav">About · Program · <b>Get involved</b></span></div></div></div>'''),
        ("Social profiles: circle and square crops", f'''<div class="social">
<div class="prof"><div class="banner" style="background:{INK}"></div><div class="av circle">{tile(84, small=False)}</div><div class="pinfo"><b>SIRA</b><span>Societal Impacts Research on AI</span></div></div>
<div class="prof"><div class="banner" style="background:{TERRA}"></div><div class="av">{tile(84, small=False)}</div><div class="pinfo"><b>SIRA Fellowship</b><span>Research fellowship</span></div></div></div>'''),
        ("Phone home screen (light and dark)", f'''<div class="phones">{"".join(f"""<div class="phone" style="background:{bg}"><div class="grid">{"".join(f'<div class="app"><div class="ic" style="background:{c}"></div><span style="color:{fc}">{n}</span></div>' for n, c in [("Mail", "#3b82f6"), ("Calendar", "#ef4444"), ("Notes", "#f59e0b"), ("Maps", "#10b981"), ("Photos", "#f472b6"), ("Docs", "#2563eb"), ("Slack", "#4a154b")])}<div class="app"><img src="file://{ROOT}/apple-touch-icon.png" class="ic"><span style="color:{fc}">SIRA</span></div></div></div>""" for bg, fc in [("linear-gradient(160deg,#c9d8e4,#e9d9c7)", "#1d1d1f"), ("linear-gradient(160deg,#1c2833,#0b1118)", "#f2f2f2")])}</div>'''),
        ("Presentation slide", f'''<div class="slide">{logo(30)}<div class="sl-title">Social scientists are AI safety's most underused talent.</div>
<div class="sl-rule"></div><div class="sl-sub">A 10–12 week mentored research fellowship · Summer 2027</div></div>'''),
        ("Poster", f'''<div class="poster">{mark(48, "cream")}<div class="ps-kick">Proposed fellowship · Summer 2027</div>
<div class="ps-title">Societal Impacts Research on AI</div><div class="ps-img" style="background-image:url('file://{painting}')"></div>
<div class="ps-foot">Express interest at <b>sirafellowship.org</b></div></div>'''),
        ("Name badge", f'''<div class="badge"><div class="bd-top">{logo(26, "cream")}</div><div class="bd-name">Emilio Barkett</div><div class="bd-role">Organizer</div><div class="bd-strip"></div></div>'''),
        ("Stickers", f'''<div class="stickers"><div class="stk r1">{tile(120, small=False)}</div><div class="stk r2">{tile(120, "terracotta", False)}</div><div class="stk ci">{tile(120, "cream", False)}</div></div>'''),
        ("Email signature", f'''<div class="mail"><p>Thanks for your interest. I'd love to set up a call next week.</p><p>Best,</p>
<div class="sig"><b>Emilio Barkett</b><div class="sg-role">Organizer, SIRA</div><div class="sg-logo">{logo(22, kind="full")}</div>
<div class="sg-links">sirafellowship.org · contact@sirafellowship.org</div></div></div>'''),
        ("Link preview", f'''<div class="slack"><b>Emilio</b> <span class="t">10:42 AM</span><div>Here's the fellowship proposal: <a>https://sirafellowship.org</a></div>
<div class="unfurl"><div class="uf-site">{tile(16)} SIRA</div><div class="uf-title">Societal Impacts Research on AI (SIRA)</div>
<img src="file://{PNG}/og-image.png" style="width:340px;display:block;margin-top:8px"></div></div>'''),
    ]
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{STYLE}
.wall{{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}} .stage{{background:#fff;padding:22px;height:300px;display:flex;align-items:center;justify-content:center;overflow:hidden}}
.browser{{width:100%;border:1px solid #d6d6d6}} .tabs{{display:flex;gap:2px;background:#dfe3e7;padding:6px 6px 0;font-size:12px}}
.tab{{display:flex;align-items:center;gap:7px;padding:7px 10px;background:#e9edf0;white-space:nowrap}} .tab.on{{background:#fff}}
.url{{padding:6px 12px;font-size:12px;color:#555;border-bottom:1px solid #eee}} .page{{background:{CREAM};padding:14px 16px;height:120px}}
.pghdr{{display:flex;align-items:center}} .nav{{margin-left:auto;font-size:12px;color:#52606b}} .nav b{{background:{TERRA};color:#fff;font-weight:500;padding:5px 9px}}
.social{{display:flex;gap:16px}} .prof{{width:220px;border:1px solid #e3e3e3;position:relative}} .banner{{height:60px}}
.av{{position:absolute;top:20px;left:14px;border:4px solid #fff;overflow:hidden;line-height:0}} .av.circle{{border-radius:50%}}
.pinfo{{padding:56px 14px 14px}} .pinfo b{{display:block}} .pinfo span{{font-size:12px;color:#666}}
.phones{{display:flex;gap:12px}} .phone{{width:128px;height:236px;border-radius:24px;padding:26px 10px;box-sizing:border-box}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px 4px}} .app{{display:flex;flex-direction:column;align-items:center;gap:3px}}
.ic{{width:28px;height:28px;border-radius:7px;display:block}} .app span{{font-size:7px}}
.slide{{width:100%;height:240px;background:{CREAM};padding:22px 26px;box-sizing:border-box}} .sl-title{{font:500 26px/1.15 Fraunces,serif;margin-top:34px}}
.sl-rule{{width:48px;height:4px;background:{TERRA};margin:14px 0 10px}} .sl-sub{{font-size:13px;color:#52606b}}
.poster{{width:200px;height:290px;background:{INK};color:{CREAM};padding:18px;box-sizing:border-box;display:flex;flex-direction:column;gap:7px}}
.ps-kick{{font-size:9px;color:#e39a74;margin-top:6px}} .ps-title{{font:500 22px/1.1 Fraunces,serif}} .ps-img{{flex:1;background-size:cover;background-position:60% 50%;margin:4px -18px}} .ps-foot{{font-size:9px}}
.badge{{width:180px;height:260px;background:#fff;box-shadow:0 3px 10px rgba(0,0,0,.15);display:flex;flex-direction:column;align-items:center}}
.bd-top{{width:100%;background:{INK};padding:34px 0 18px;display:flex;justify-content:center}} .bd-name{{font:500 21px Fraunces,serif;margin-top:28px}}
.bd-role{{font-size:12px;color:#7f8a91}} .bd-strip{{margin-top:auto;width:100%;height:12px;background:{TERRA}}}
.stickers{{display:flex;gap:16px}} .stk{{background:#fff;padding:7px;box-shadow:0 3px 9px rgba(0,0,0,.18);line-height:0}} .r1{{transform:rotate(-6deg)}} .r2{{transform:rotate(4deg)}}
.ci,.ci img{{border-radius:50%}} .mail{{width:100%;font-size:13px}} .mail p{{margin:4px 0}} .sig{{margin-top:12px;padding-top:10px;border-top:1px solid #eee}}
.sg-role{{font-size:12px;color:#666}} .sg-logo{{margin:8px 0 4px}} .sg-links{{font-size:12px;color:{TERRA}}}
.slack{{width:100%;font-size:13px}} .slack .t{{color:#888;font-size:11px}} .slack a{{color:#1264a3}} .unfurl{{border-left:4px solid #ddd;padding-left:12px;margin-top:8px}}
.uf-site{{display:flex;align-items:center;gap:6px;font-weight:600;font-size:12px}} .uf-title{{color:#1264a3;font-weight:600}}</style></head><body>
<h1>SIRA in use</h1><p class="sub">The kit's own files in context: ink {INK}, terracotta {TERRA}, cream {CREAM}.</p>
<div class="wall">{"".join(f'<figure><div class="stage">{inner}</div><figcaption>{t}</figcaption></figure>' for t, inner in cards)}</div></body></html>"""
    shoot(html, B / "mockups.png", 1500)


if __name__ == "__main__":
    contact_sheet()
    mockups()
    print("Wrote brand/contact-sheet.png and brand/mockups.png.")
