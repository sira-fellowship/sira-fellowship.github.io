"""Build the mentors page and one profile page per mentor from a CSV, and crop mentor photos.

Usage: python3 tools/mentors_page.py [tools/mentors.csv]

Writes the cards on mentors/index.html (between the MENTORS markers) and a page per mentor at
mentors/profile/<slug>/index.html, after pivotal-research.org/mentors/profile/<slug>. Profiles of
mentors no longer in the CSV are removed.

CSV columns (one row per mentor; only name, title, and discipline are required):
    name, title, affiliation, discipline, photo, bio, website, linkedin, scholar, cohort, badge,
    directions, example_project, methods, recent_work, looking_for, mentoring_style, profile_updated

- discipline: one or more of DISCIPLINES below, separated by commas (each gets a tag and appears in
  the filter; the first sets the colour of the initials when there is no photo).
- photo: a file in images/mentors/source/ (any size; it is centre-cropped to a square and
  saved as images/mentors/<slug>-480.jpg and -960.jpg). Leave blank to show initials.
- bio: a few sentences. Blank lines are not supported.
- cohort: the group heading, e.g. "Summer 2027" (default). Groups appear in CSV order.
- badge: optional short label on the photo's corner, e.g. "Returning".
- Profile fields, all optional, shown on the profile page under the bio:
    directions       research questions, separated by " | "
    example_project  one paragraph, shown as an illustrative example, not a commitment
    methods          methods the mentor can supervise, separated by ", " (or " | " if an item has commas)
    recent_work      "Title :: URL" items separated by " | " (URL optional)
    looking_for      who the mentor would like to work with
    mentoring_style  how the mentor works with fellows
    profile_updated  date the mentor last reviewed these fields, e.g. 2026-11-04
The list page's "Last updated" date is the day the script runs.

Only list mentors who have agreed to be named, with the photo and title they chose. This repo and
everything in it is public, so mentors who have not confirmed stay in tools/mentors-pending.csv and
their photos in tools/mentors-pending/ (both git-ignored). When someone confirms: move their row to
tools/mentors.csv, move their photo to images/mentors/source/, run this script, and push.
"""

import csv
import datetime
import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "mentors" / "index.html"
PROFILES = ROOT / "mentors" / "profile"
PHOTOS = ROOT / "images" / "mentors"
START, END = "<!-- MENTORS:START -->", "<!-- MENTORS:END -->"
SITE = "https://sira-project.org"
FELLOW_FORM = "https://airtable.com/appjnZXuP3QQHiV6X/pagdpah3mjgyQ4jzf/form"

# Discipline -> tag colour, one per discipline: the logo palette (sage, wheat, roof, slate) plus
# six muted companions in the same range (teal, olive, plum, ochre, rose, sky), defined in style.css.
DISCIPLINES = {
    "Psychology": "sage",
    "Cognitive science": "wheat",
    "Computational neuroscience": "teal",
    "Economics": "olive",
    "Political science": "slate",
    "Sociology": "roof",
    "Organizational behavior": "plum",
    "Anthropology": "ochre",
    "Communication": "rose",
    "AI safety research": "sky",
}


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def initials(name):
    parts = [p for p in re.split(r"\s+", name) if p]
    return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()


def g(m, k):
    return (m.get(k) or "").strip()


def e(m, k):
    return html.escape(g(m, k))


def fmt(d):
    return f"{d.day} {d:%b %Y}"


def crop(src, s):
    from PIL import Image, ImageOps
    img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    side = min(img.size)
    left, top = (img.width - side) // 2, max(0, (img.height - side) // 3)  # favour the face
    img = img.crop((left, top, left + side, top + side))
    PHOTOS.mkdir(parents=True, exist_ok=True)
    for size in (480, 960):
        img.resize((size, size), Image.LANCZOS).save(PHOTOS / f"{s}-{size}.jpg", quality=85, optimize=True)


def role(m):
    return ", ".join(x for x in (e(m, "title"), e(m, "affiliation")) if x)


def discs(m):
    return [d.strip() for d in g(m, "discipline").split(",") if d.strip()]


def tag(m):
    return "".join(f'<span class="mentor-tag tag-{DISCIPLINES[d]}">{html.escape(d)}</span>' for d in discs(m))


def photo(m, root, size_hint):
    """The square photo, or initials on a tint. `root` is the relative path to the site root."""
    s = slug(m["name"])
    if g(m, "photo"):
        return (f'<img src="{root}images/mentors/{s}-480.jpg" srcset="{root}images/mentors/{s}-480.jpg 480w, '
                f'{root}images/mentors/{s}-960.jpg 960w" sizes="{size_hint}" alt="" width="480" height="480" loading="lazy">')
    return f'<span class="mentor-initials tone-{DISCIPLINES[discs(m)[0]]}" aria-hidden="true">{initials(m["name"])}</span>'


def card(m, root, href):
    """One card in a grid of mentors: photo and name link to the profile page."""
    badge = f'<span class="mentor-badge">{e(m, "badge")}</span>' if g(m, "badge") else ""
    search = html.escape(" ".join(g(m, k) for k in ("name", "title", "affiliation", "discipline")).lower())
    return f'''                    <li class="mentor" data-discipline="{html.escape("|".join(discs(m)))}" data-search="{search}">
                        <a class="mentor-card" href="{href}">
                            <span class="mentor-photo">{photo(m, root, "(min-width: 1000px) 25vw, (min-width: 720px) 33vw, 50vw")}{badge}<span class="mentor-hover" aria-hidden="true">View profile</span></span>
                            <span class="mentor-name">{e(m, "name")}</span>
                        </a>
                        <p class="mentor-role">{role(m)}</p>
                        <p class="mentor-tags">{tag(m)}</p>
                    </li>'''


def sections(m):
    """Profile sections after the bio: durable research directions, an illustrative example project,
    methods, recent work, fit, and mentoring style. Blank fields are left out."""
    out = []
    if g(m, "bio"):
        out.append(f"<h2>About</h2><p>{e(m, 'bio')}</p>")
    if g(m, "directions"):
        items = "".join(f"<li>{html.escape(x.strip())}</li>" for x in g(m, "directions").split(" | ") if x.strip())
        out.append(f'<h2>Research directions</h2><ul class="profile-list">{items}</ul>')
    if g(m, "example_project"):
        out.append('<h2>Example project</h2><p class="profile-note">Illustrative. Final projects are confirmed '
                   f'before applications open.</p><p>{e(m, "example_project")}</p>')
    if g(m, "methods"):
        chips = "".join(f"<li>{html.escape(x.strip())}</li>" for x in re.split(r" \| " if " | " in g(m, "methods") else ", ", g(m, "methods")) if x.strip())
        out.append(f'<h2>Methods they can supervise</h2><ul class="profile-chips">{chips}</ul>')
    if g(m, "recent_work"):
        items = []
        for x in g(m, "recent_work").split(" | "):
            title, _, url = (p.strip() for p in x.partition("::"))
            items.append(f'<li><a href="{html.escape(url)}">{html.escape(title)}</a></li>' if url
                         else f"<li>{html.escape(title)}</li>")
        out.append(f'<h2>Recent work</h2><ul class="profile-list">{"".join(items)}</ul>')
    if g(m, "looking_for"):
        out.append(f"<h2>Who they’re looking for</h2><p>{e(m, 'looking_for')}</p>")
    if g(m, "mentoring_style"):
        out.append(f"<h2>Mentoring style</h2><p>{e(m, 'mentoring_style')}</p>")
    if g(m, "profile_updated"):
        d = datetime.date.fromisoformat(g(m, "profile_updated"))
        out.append(f'<p class="profile-updated">Profile last updated: <time datetime="{d.isoformat()}">{fmt(d)}</time></p>')
    return "\n                        ".join(out)


def shell(list_page):
    """Head, header, and footer for a profile page, from the mentors page (one level deeper by two)."""
    head, rest = list_page.split('    <main id="top"', 1)
    footer = rest.split("</main>\n", 1)[1]
    footer = re.sub(r"    <script>\n        // Search and discipline filter.*?</script>\n", "", footer, flags=re.S)
    fix = lambda t: t.replace('href="../', 'href="../../../').replace('src="../', 'src="../../../')
    return fix(head), fix(footer)


def profile_page(m, others, head, footer):
    s = slug(m["name"])
    first = re.split(r"(?<=\.)\s", g(m, "bio"))[0] if g(m, "bio") else f"{g(m, 'name')}, mentor for SIRA’s fellowship."
    desc = html.escape(first)
    title = f"{e(m, 'name')} · Mentors · SIRA"
    url = f"{SITE}/mentors/profile/{s}/"
    h = re.sub(r"<title>[^<]*</title>", f"<title>{title}</title>", head)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*"', lambda x: x.group(1) + title + '"', h)
    h = re.sub(r'(<meta (?:name="description"|property="og:description") content=")[^"]*"', lambda x: x.group(1) + desc + '"', h)
    h = h.replace(f"{SITE}/mentors/", url)
    links = "".join(f'<a href="{e(m, k)}">{label}</a>' for k, label in
                    (("website", "Website"), ("linkedin", "LinkedIn"), ("scholar", "Google Scholar")) if g(m, k))
    more = ""
    if others:
        more = f'''
            <section class="profile-more" aria-labelledby="more-mentors">
                <h2 id="more-mentors">More mentors</h2>
                <ul class="mentors">
{chr(10).join(card(o, "../../../", f"../{slug(o['name'])}/") for o in others)}
                </ul>
            </section>'''
    main = f'''    <main id="top" class="project-page mentors-page mentor-profile">
        <div class="wrap">
            <p class="profile-back"><a href="../../">← All mentors</a></p>
            <div class="profile-grid">
                <div class="profile-side">
                    <div class="mentor-photo">{photo(m, "../../../", "(min-width: 720px) 320px, 100vw")}</div>
                    {f'<p class="bio-links">{links}</p>' if links else ""}
                    <a class="hero-button hero-button-fill" href="{FELLOW_FORM}" target="_blank" rel="noopener">Express interest as a fellow</a>
                </div>
                <article class="profile-main">
                    <p class="profile-cohort">Mentor · {e(m, "cohort")}</p>
                    <h1>{e(m, "name")}</h1>
                    <p class="profile-role">{role(m)}</p>
                    <p class="mentor-tags">{tag(m)}</p>
                    <div class="profile-body">
                        {sections(m)}
                    </div>
                </article>
            </div>{more}
        </div>
    </main>
'''
    out = PROFILES / s / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(h + main + footer)


def main(src):
    mentors = list(csv.DictReader(open(src, newline="", encoding="utf-8-sig")))
    for m in mentors:
        if not discs(m) or any(d not in DISCIPLINES for d in discs(m)):
            sys.exit(f"{m.get('name')}: discipline must be one of {', '.join(DISCIPLINES)}")
        m["cohort"] = g(m, "cohort") or "Summer 2027"
        if g(m, "photo"):
            crop(PHOTOS / "source" / g(m, "photo"), slug(m["name"]))
    by_last = lambda m: m["name"].split()[-1].lower()
    cohorts = list(dict.fromkeys(m["cohort"] for m in mentors))
    used = [d for d in DISCIPLINES if any(d in discs(m) for m in mentors)]
    options = "".join(f'<option value="{html.escape(d)}">{html.escape(d)}</option>' for d in used)
    today = datetime.date.today()
    groups = []
    for c in cohorts:
        members = sorted((m for m in mentors if m["cohort"] == c), key=by_last)
        groups.append(f'''            <section class="mentor-group" aria-labelledby="cohort-{slug(c)}">
                <h2 class="mentor-cohort" id="cohort-{slug(c)}">{html.escape(c)}</h2>
                <ul class="mentors">
{chr(10).join(card(m, "../", f"profile/{slug(m['name'])}/") for m in members)}
                </ul>
            </section>''')
    n = len(mentors)
    if not n:
        groups = ['            <p class="mentor-empty">Mentors will be listed here as they confirm.</p>']
    block = f'''{START}
            <div class="mentor-toolbar">
                <p class="mentor-count"><strong>{n}</strong> mentor{"s" if n != 1 else ""}</p>
                <div class="mentor-controls">
                    <label><span class="visually-hidden">Search mentors</span><input type="search" class="mentor-search" placeholder="Search mentors"></label>
                    <label><span class="visually-hidden">Discipline</span><select class="mentor-discipline"><option value="">All disciplines</option>{options}</select></label>
                </div>
                <p class="mentor-updated">Last updated: <time datetime="{today.isoformat()}">{fmt(today)}</time></p>
            </div>
{chr(10).join(groups)}
            <p class="mentor-empty" hidden>No mentors match.</p>
            {END}'''
    page = PAGE.read_text()
    a, b = page.index(START), page.index(END) + len(END)
    page = page[:a] + block + page[b:]
    PAGE.write_text(page)

    # Profile pages; remove any for mentors no longer listed.
    head, footer = shell(page)
    keep = {slug(m["name"]) for m in mentors}
    if PROFILES.exists():
        for d in PROFILES.iterdir():
            if d.is_dir() and d.name not in keep:
                shutil.rmtree(d)
    ordered = sorted(mentors, key=by_last)
    for m in ordered:
        profile_page(m, [o for o in ordered if o is not m], head, footer)
    # Sitemap: the mentors page plus one entry per listed profile.
    sitemap = ROOT / "sitemap.xml"
    lines = [l for l in sitemap.read_text().splitlines() if "/mentors/" not in l]
    end = lines.index("</urlset>")
    lines[end:end] = [f"  <url><loc>{SITE}/mentors/</loc></url>"] + \
        [f"  <url><loc>{SITE}/mentors/profile/{slug(m['name'])}/</loc></url>" for m in ordered]
    sitemap.write_text("\n".join(lines) + "\n")
    print(f"{n} mentors in {len(cohorts)} group(s): mentors/index.html and {n} profile pages")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT / "tools" / "mentors.csv")
